import joblib
import pandas as pd
from pathlib import Path
import tweepy
import numpy as np
import time

from batoomer.extras.utils import my_print


class Classifier:
    """
    This Class is used to classify Twitter Nodes using pretrained Machine Learning Models.
    The Available model are:
    - classifier_parl_nd
    - classifier_parl_tme
    - classifer_parl_fr
    - classifier_parl_fo
    """

    def __init__(self, model_name, twitter_credentials, verbose):
        self._verbose = verbose
        self._API = self.__authenticate_twitterapi(twitter_credentials)
        self._clf = self.__load_classifier(model_name)
        self.__model_type = model_name.split('_')[-1]
        self._model_class = model_name.split('_')[-2]
        self._twitter_credentials = twitter_credentials

    @staticmethod
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
                         timeout=60*3, retry_count=3, retry_delay=5)

        # If Authentication Fails raise Exception
        if not api.verify_credentials():
            raise Exception(f'Authentication has failed!')

        return api

    def __load_classifier(self, model_name):
        """
        Loads the classifier
        :param model_name: Name of the classifier
        :return: classifer
        """
        my_print(f'\nLoading classifer: {model_name}', self._verbose)
        file_path = Path(__file__).parent.parent.absolute()
        model = joblib.load(file_path / 'classifiers' / f'{model_name}.sav')
        my_print(f'Loading successful.\n', self._verbose)
        return model

    def predict(self, nodes):
        """
        Given a set of nodes , collects required data and predicts the nodes labels.

        :param nodes: Lists of screen_names or IDs
        :return: Numpy Array of Labels
        """
        data = self.__get_data(nodes)
        my_print('\nStarting Classification.', self._verbose)
        labels = self._clf.predict(data)
        my_print('Classification ended.\n', self._verbose)
        return labels

    def predict_proba(self, nodes):
        """
        Given a set of nodes , collects required data and predicts the nodes labels.

        :param nodes: Lists of screen_names or IDs
        :return: Numpy Array of Labels
        """
        data = self.__get_data(nodes)
        my_print('\nStarting Predictions of Probabilities.', self._verbose)
        proba = self._clf.predict_proba(data)
        my_print('Prediction ended.\n', self._verbose)
        return proba

    def predict_given_data(self, data):
        """
        Given a set of nodes, with the required data, returns labels predicted by the model.

        :param data: Pandas DataFrame
        :return: Numpy Array of Labels
        """
        return self._clf.predict(data)

    def predict_proba_given_data(self, data):
        """
        Given a set of nodes , with the required data, predicts the nodes probabilities belonging to a class.

        :param data:
        :return: Numpy Array of Labels
        """
        proba = self._clf.predict_proba(data)
        return proba

    def __get_data(self, nodes):
        if self._model_class == 'parl':
            # Data For Model ND
            if self.__model_type == 'nd':
                from batoomer.extras.nd_utils import fetch_nd_data
                data = fetch_nd_data(nodes=nodes, API=self._API, verbose=self._verbose)

            # Data For Model TMe
            elif self.__model_type == 'tme':
                from batoomer.extras.tme_utils import fetch_statuses, calculate_parliament_mentions
                data = pd.DataFrame()
                data['recent_100_tweets'] = fetch_statuses(nodes=nodes, API=self._API, verbose=self._verbose)

                data['mentions_politician_count'] = calculate_parliament_mentions(data=data, API=self._API,
                                                                                  twitter_credentials=self._twitter_credentials,
                                                                                  verbose=self._verbose)
            # Data For Model Fr
            elif self.__model_type == 'fr':
                from batoomer.extras.fr_utils import calculate_parliament_friends
                data = pd.DataFrame()
                data['friends_politician_count_1000'] = calculate_parliament_friends(nodes=nodes, API=self._API,
                                                                                     verbose=self._verbose,
                                                                                     twitter_credentials=self._twitter_credentials)
            # Data For Model Fo
            elif self.__model_type == 'fo':
                from batoomer.extras.fo_utils import calculate_parliament_followers
                data = pd.DataFrame()
                data['followers_politician_count_1000'] = calculate_parliament_followers(nodes=nodes, API=self._API,
                                                                                     verbose=self._verbose,
                                                                                     twitter_credentials=self._twitter_credentials)
            else:
                data = 'Error'
            return data


class VotingClassifier:
    def __init__(self, twitter_credentials, verbose):
        self.model_nd = Classifier(model_name='classifier_parl_nd',
                                   twitter_credentials=twitter_credentials,
                                   verbose=verbose)
        self.model_tme = Classifier(model_name='classifier_parl_tme',
                                    twitter_credentials=twitter_credentials,
                                    verbose=verbose)
        self.model_fr = Classifier(model_name='classifier_parl_fr',
                                   twitter_credentials=twitter_credentials,
                                   verbose=verbose)
        self.model_fo = Classifier(model_name='classifier_parl_fo',
                                   twitter_credentials=twitter_credentials,
                                   verbose=verbose)
        self._verbose = verbose

    def predict(self, nodes):
        nd_proba, tme_proba, fr_proba, fo_proba, data = self.__calculate_probas(nodes)
        a, b, c, d = self.__calculate_weights(data)

        proba = [0 for i in range(len(data))]
        for i in range(len(data)):
            proba[i] = (a[i] * nd_proba[i] + b[i] * tme_proba[i] + c[i] * fr_proba[i] + d[i] * fo_proba[i])/(a[i] + b[i] + c[i] + d[i])

        return np.argmax(proba, axis=1)

    def __calculate_probas(self, nodes):
        my_print('Starting Predictions of Probabilities.', self._verbose)

        from batoomer.extras.nd_utils import fetch_nd_data
        data = fetch_nd_data(nodes=nodes, API=self.model_nd._API, verbose=self._verbose, extended=True)
        nd_proba = self.model_nd.predict_proba_given_data(data)
        tme_proba = self.model_tme.predict_proba(nodes)
        fr_proba = self.model_fr.predict_proba(nodes)
        fo_proba = self.model_fo.predict_proba(nodes)
        return nd_proba, tme_proba, fr_proba, fo_proba, data

    def __calculate_weights(self, data):
        my_print('Starting Calculation of Weights.', self._verbose)
        a = [10 for i in range(len(data))]
        b = [3 for i in range(len(data))]
        c = [0.5 for i in range(len(data))]
        d = [0.5 for i in range(len(data))]

        for i, description in enumerate(data['description']):
            if description == '':
                a[i] = 0
            if data.iloc[i]['statuses_count'] == 0:
                b[i] = 0
            if data.iloc[i]['friends_count'] == 0:
                c[i] = 0

        return a, b, c, d
