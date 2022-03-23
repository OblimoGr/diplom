# This file contains functions that are necessary for the friends based classifiers to work.
# Some of the function need to be explicitly imported

from batoomer.extras.utils import my_print
import tweepy
import pandas as pd
from tqdm import tqdm


# ------------------------------------ Functions For Fr Models -------------------------------------------
# This functions have to be explicitly imported in order for the corresponding models to work
# parl -> greek parliament members classifier
def get_data_parl_fr(df):
    data = df['friends_politician_count_1000'].to_numpy()
    return data.reshape(-1, 1)


# ------------------------------------- Functions For Data Fetching ---------------------------------------
def fetch_friends(node, API, verbose, count=1000):
    """
    Given a node returns a DataFrame containing the names and descriptions of <count> friends. If the node is
    protected or does not have friends, returns a empty DataFrame instead.

    :param node: screen_name or ID of the node
    :param API: tweepy API object
    :param verbose: Int, If 1 prints, else it doesn't print.
    :param count: number of friends to fetch
    :return: DataFrame object with columns 'name' and 'description
    """
    my_print(f'Fetching friends of: {node}.', verbose)
    # Fetch friend IDs
    friend_ids = []
    try:
        for ids in tweepy.Cursor(API.friends_ids, node).items(count):
            friend_ids.append(ids)

    except tweepy.error.TweepError as err:
        my_print(f'Not authorized to fetch friends for node: {node}. Returning an empty DataFrame.', verbose)
        return pd.DataFrame(columns=['name', 'description'])

    except Exception as err:
        raise Exception(f'An unknown Error has occurred.\n{err}')

    # If node has zero friends
    if not friend_ids:
        my_print(f'Node {node} has zero friends. Returning an empty DataFrame.', verbose)
        return pd.DataFrame(columns=['name', 'description'])

    # Calculate Iteration Required, to iterate per 100 ids
    if (int(len(friend_ids)) % 100) == 0:
        it_num = int(len(friend_ids) / 100)
    else:
        it_num = (int(len(friend_ids) / 100) + 1)

    # Transform IDs to User Objects
    users = list()
    try:
        for i in range(it_num):
            users.append(API.lookup_users(friend_ids[100 * i: 100 * (1 + i)]))
    except Exception as err:
        raise Exception(f'An unknown Error has occurred.\n{err}')

    # Extract Profile Name and Description for each friends and save it to a DataFrame
    results = pd.DataFrame()
    for items in users:
        for user in items:
            results = results.append(pd.DataFrame([user.name, user.description]).T)
    results.columns = ['name', 'description']
    results = results.reset_index().drop('index', axis=1)

    my_print('Fetching completed.', verbose)
    return results


def calculate_parliament_friends(nodes, API, verbose, twitter_credentials):
    """
    Given a list of nodes. Extracts 1000 friends, classifies them, and calculates the number of friends, that are
    parliament members.

    :param nodes: list containing twitter screen_names or IDs
    :param API: tweepy API object
    :param verbose: Int, If 1 prints, else it doesn't print.
    :param twitter_credentials: json object containing twitter api credentials.
    :return: List of integers
    """
    from batoomer.twitter_nodes.classification import Classifier
    counts = []

    my_print(f'\nCalculating number of friends that are parliament members. This will take some time.', verbose)
    for node in tqdm(nodes, leave=False, desc='Calculating friends parliament member count.'):
        # Get Required Data
        data = fetch_friends(node=node, API=API, verbose=0, count=1000)

        # Get Labels
        if not data.empty:
            clf = Classifier(model_name='classifier_parl_nd', twitter_credentials=twitter_credentials,
                             verbose=0)
            data['label'] = clf.predict_given_data(data)

            count = len(data[data['label'] == 1])
        else:
            count = 0

        counts.append(count)

    my_print(f'Calculations completed.\n', verbose)

    return counts
