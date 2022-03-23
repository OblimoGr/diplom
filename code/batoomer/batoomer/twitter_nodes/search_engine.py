import tweepy
from googleapiclient.discovery import build
import numpy as np
import pandas as pd
import re


class TwitterSearchEngine:

    def __init__(self, twitter_credentials):
        # Variable to hold the results
        self._results = pd.DataFrame()

        # TwitterAPI Authentication
        auth = tweepy.OAuthHandler(twitter_credentials['consumer_key'],
                                   twitter_credentials['consumer_secret'])
        auth.set_access_token(twitter_credentials['access_token_key'],
                              twitter_credentials['access_token_secret'])
        self._API = tweepy.API(auth)

        # If Authentication Fails raise Exception
        if not self._API.verify_credentials():
            raise Exception(f'Authentication has failed!')

    def search(self, query, count):
        """
        Using the TwitterAPI search_users endpoint, search for twitter accounts that correspond to the given query.

        :param query: Query to search for
        :param count: Number of results to get from the endpoint
        """

        # Initialize Variables
        p = 0  # Page Number
        accounts = []  # List to hold screen_names returned by the search users endpoint
        old_results = []  # List to hold results for p-1, if results do not change the loop stops

        # Main Loop
        while len(accounts) < count:
            # Increase p by one. (First Page has a Value of 1)
            p += 1

            # Flag to check if new search results are found
            old_results_len = len(accounts)

            # Call the search users endpoint with query and p
            search_results = self._API.search_users(q=query, page=p)

            # Iterate search_results to get screen_names
            new_results = []  # List to hold results from page p
            for result in search_results:
                new_results.append(result.screen_name)

            # If results from page p and page p-1 are not the same, add them to the final result list.
            # If they are the same the loop will break as old_results_len == len(accounts) will be True.
            if old_results != new_results:
                accounts += new_results
                old_results = new_results

            # If new results are not found break
            if old_results_len == len(accounts):
                # Append np.nan until the length of accounts equals to count
                while len(accounts) < count:
                    accounts.append(np.nan)

                break

        # return the possible accounts found
        self._results = pd.DataFrame(data=[query] + accounts,
                                     index=['Query'] + [f'Result {i + 1}' for i in range(len(accounts))]).T

    def get_results(self):
        """
        :return: Pandas DataFrame containing the results
        """
        return self._results


class GoogleSearchEngine:
    def __init__(self, google_api_key, search_engine_id):
        # Variable to hold the results
        self._results = pd.DataFrame()
        # Google API key
        self._api = google_api_key
        # Custom Search Engine ID
        self._seID = search_engine_id

    @staticmethod
    def __google_search(query, api, seID):
        """
        Search google using the custom search engine, provided by google.

        :param query: Search term to search for
        :param api: Google API key
        :param seID: Custom Search Engine ID
        :return:
        """
        service = build('customsearch', 'v1', developerKey=api)
        return service.cse().list(q=query, cx=seID).execute()

    def search(self, query, platform='twitter'):
        if platform == 'twitter':
            # Call __google_search method to get the results
            result = self.__google_search(query=f'{query} twitter', api=self._api, seID=self._seID)

            # Variable to keep twitter accounts
            accounts = []

            # If there are results start processing
            if 'items' in result.keys():
                # Variable to join all search result titles
                titles = ''
                # Iterate through all search result titles and join them
                for res in result['items']:
                    titles += res['title']

                # Using regex, search for twitter accounts on the titles  '@\w+'
                accounts = re.findall(r'@\w+', titles)

                # TODO KEEP OR REMOVE
                if accounts:
                    accounts = [acc[1:] for acc in accounts]

                # if no account was found append np.nan to accounts
                if not accounts:
                    accounts.append(np.nan)

            # Else if no results were found by google, append np.nan to accounts
            else:
                accounts.append(np.nan)

            # Return the possible account found
            self._results = pd.DataFrame(data=[query] + accounts,
                                         index=['Query'] + [f'Result {i + 1}' for i in range(len(accounts))]).T
        else:
            result = self.__google_search(query=f'{query} site:www.facebook.com', api=self._api, seID=self._seID)

            # Variable to keep facebook accounts
            accounts = []

            # If there are results start processing
            if 'items' in result.keys():
                # Iterate through all search result titles and try to find Home | Facebook
                for res in result['items']:
                    if re.findall(r'Home \| Facebook', res['title']):
                        accounts.append(res['link'])

                # if no account was found append np.nan to accounts
                if not accounts:
                    accounts.append(np.nan)

            # Else if no results were found by google, append np.nan to accounts
            else:
                accounts.append(np.nan)

            # Return the possible account found
            self._results = pd.DataFrame(data=[query] + accounts,
                                         index=['Query'] + [f'Result {i + 1}' for i in range(len(accounts))]).T

    def get_results(self):
        """
         :return: Pandas DataFrame containing the results
         """
        return self._results

