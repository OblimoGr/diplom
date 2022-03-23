import tweepy
import numpy as np

import math
import sys
import webbrowser
import queue
from collections import deque
from itertools import zip_longest

from batoomer.extras.utils import my_print


class Frontier():
    """ Objects of this class keep track of the Breadth-First Search
    Frontier as it is expanded.

    Moreover, this implements the probabilistic expansion of nodes on the
    perimeter.

    """

    def __init__(self, src, expander, get_out_degree, lookup):
        self.internal = set()
        self.perimeter = set()
        self.distribution = {}

        self.perimeter.add(src)

        # self.distribution is a map of distances to the nodes that lie at that
        # distance from the source.
        self.distribution[0] = [src]

        # some metadata to be able to trace back the path from a node to
        # the source node
        self.metadata = {}
        self.metadata[src] = {"distance": 0, "parent": None}

        # Our expander makes a set out of the iterable returned
        self.expander = lambda u: set(expander(u))

        # get_out_degree is a function for obtaining the out-degree of a node.
        # It is useful because the way we compute out-degrees is different for
        # the BFS for the source and the destination nodes.
        self.get_out_degree = get_out_degree

        self.lookup = lookup

    def expand_perimeter(self, verbose):
        """This is going to implement the probabilistic algorithm for
        expanding the BFS territory.

        We pick the node with maximum outdegree at a specific
        distance. The distance is picked from an exponential probability
        distribution that favors BFS expansion, i.e. lower distances are
        more likely to be picked and the probability of a distance
        decreases exponentially with the distance value.
        """
        distances = self.distribution.keys()
        probabilities = []

        # Calculate probabilities for the distances
        for d in distances:
            probabilities.append(self._pdf(d))

        # Sample a distance and then a node to expand
        d = np.random.choice(a=list(distances), p=self._normalize(probabilities))

        # I think this is getting more difficult by not taking in the api object
        # as one of its inputs.
        nodes_at_d = self.lookup(self.distribution[d])
        u = max(nodes_at_d, key=self.get_out_degree).id

        self.internal.add(u)
        self.perimeter.remove(u)

        d = self.metadata[u]["distance"]
        self.distribution[d].remove(u)

        # Do not keep empty lists
        if self.distribution[d] == []:
            del self.distribution[d]

        # let's move the frontier forward at the node 'u'
        new_nodes = self.expander(u).difference(self.internal, self.perimeter)
        my_print(".", verbose=verbose, end="")
        sys.stdout.flush()

        # Keep track of distance of a node from src and its parent
        d = self.metadata[u]["distance"]
        for n in new_nodes:
            self.metadata[n] = {"distance": d + 1, "parent": u}
            try:
                self.distribution[d + 1].append(n)
            except KeyError:
                self.distribution[d + 1] = []

        self.perimeter.update(new_nodes)

        return set(new_nodes)

    def is_on_perimeter(self, user_id):
        """ Tells whether user_id is in on the perimeter of this bfs frontier.
        """
        return (user_id in self.perimeter)

    def covered_all(self):
        """ True if we have covered all the graph, i.e.
        The whole graph is now internal. There remain no nodes on
        the periphery.
        """
        return bool(self.perimeter)

    def _pdf(self, d):
        """ Compute the probability of selecting a distance d.
        p(d) = exp(alpha * d).
        We normalize values returned by this function later with _normalize()
        """
        alpha = -2
        return math.exp(alpha * d)

    def _normalize(self, probs):
        """ Normalize probability values to bring them in [0, 1] and to make
        their sum equal to 1.
        """
        probs = np.array(probs)
        probs = probs / probs.sum()
        return probs

    def get_parent(self, n):
        """ Returns the parent for node n.
        Will throw KeyError when we haven't seen the node before.
        But in this application, we don't expect that to happen. So, if it
        happens, something is really messed up.
        """
        return self.metadata[n]["parent"]

    def get_distance(self, n):
        """" Returns the distance of node `n` from the source.
        """
        return self.metadata[n]["distance"]


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def safe_lookup_users(api, ids):
    """ Handles looking up users more than 100.
    """
    users = []
    for batch_ids in grouper(ids, 100):
        ids = filter(lambda n: n != None, list(batch_ids))
        users.extend(api.lookup_users(user_ids=ids))

    return users


def __authenticate_twitterapi(twitter_credentials):
    """
    Handles twitter api authentication.

    :param twitter_credentials: json object containing twitter api credentials
    :return: tweepy api object
    """

    # TwitterAPI Authentication
    auth = tweepy.OAuthHandler(twitter_credentials['consumer_key'],
                               twitter_credentials['consumer_secret'])
    auth.set_access_token(twitter_credentials['access_token_key'],
                          twitter_credentials['access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,
                     timeout=60 * 3, retry_count=3, retry_delay=5)

    # If Authentication Fails raise Exception
    if not api.verify_credentials():
        raise Exception(f'Authentication has failed!')

    return api


def degree_of_separation_probabilistic(twitter_credentials, source, destination, verbose=0):
    api = __authenticate_twitterapi(twitter_credentials)

    source = source
    destination = destination

    if source == destination:
        return 0

    try:
        # Get user ids from the user handles
        src_user = api.get_user(source)
        dest_user = api.get_user(destination)

        my_print(f"Begin: {src_user.name}", verbose=verbose)
        my_print(f"End: {dest_user.name}", verbose=verbose)

        # If source or destination are protected account return -1
        if src_user.protected or dest_user.protected:
            return -1

        # if source does not have any friends or destination does not have any followers return -1
        if src_user.friends_count == 0 or dest_user.followers_count == 0:
            return -1

        src_frontier = Frontier(src_user.id, api.friends_ids
                                , lambda n: n.friends_count
                                , lambda ids: safe_lookup_users(api, ids))
        dest_frontier = Frontier(dest_user.id, api.followers_ids
                                 , lambda n: n.followers_count
                                 , lambda ids: safe_lookup_users(api, ids))

        while src_frontier.covered_all() or dest_frontier.covered_all():
            # Expand the source node's frontier first
            nodes = src_frontier.expand_perimeter(verbose=verbose)

            # check if any one of new nodes is on the destination's perimeter
            if any(map(lambda n: dest_frontier.is_on_perimeter(n), nodes)):
                my_print("Found!", verbose=verbose)
                break

            # Copy twice with a slight pain. If you have to copy thrice, abstract!
            nodes = dest_frontier.expand_perimeter(verbose=verbose)
            if any(map(lambda n: src_frontier.is_on_perimeter(n), nodes)):
                my_print("Found!", verbose=verbose)
                break

        # m = src_frontier.perimeter.intersection(dest_frontier.perimeter).pop()

        # The man in the middle!
        m = src_frontier.perimeter.intersection(dest_frontier.perimeter).pop()

        separation = src_frontier.get_distance(m) + dest_frontier.get_distance(m)
        my_print(text="Separation: {0}".format(separation), verbose=verbose)
        return separation

    except tweepy.TweepError as e:
        print("Something went wrong!")
        print(e)
