import argparse
import csv
import json
import sys
from pathlib import Path
import time
from tqdm import tqdm
from batoomer.twitter_nodes.search_engine import GoogleSearchEngine, TwitterSearchEngine
import pandas as pd
from googleapiclient.errors import HttpError
import tweepy

description = """
Given a set of search queries, this script returns possible social media accounts.\n
If a text file containing search queries is given as the input it will export the results to a .csv file.\n
To search with a single query, set parameter -t to true. The result will be printed on the screen.\n\n
The available social media platforms are: \n- Facebook \n- Twitter.

This tool was developed during the thesis: Classification of social media nodes.

Democritus University of Thrace 2021-2022, Department of Electrical and Computer Engineering
"""

version = "0.1.0"


def arguments():
    parser = argparse.ArgumentParser(prog='search-accounts',
                                     description=description,
                                     epilog=f'Current version: {version}')
    parser.version = version

    parser.add_argument("input",
                        help='txt file containing search queries in each line.\n'
                             'The search query, if -t is set to true',
                        type=str)

    parser.add_argument('-c',
                        help='json file containing api credentials',
                        type=str,
                        required=True,
                        dest='credentials')

    parser.add_argument('-t',
                        help='If true, a single query can be set directly from the command line. Default is False.\n'
                             'Note the input must we wrapped with "". E.g "my search query" ',
                        type=bool,
                        default=False,
                        dest='single_mode')

    parser.add_argument('-v', action='version')
    return parser.parse_args()


# Check if the input file exists and is valid. If true, read the input file
def get_queries(input_file):
    queries = None
    if not input_file.is_file():
        exit(f"File: {input_file}, does not exist.\nScript terminated!")
    if input_file.suffix == '.txt':
        with open(input_file) as f:
            queries = [line.rstrip() for line in f]
    else:
        exit(f'File type: {input_file.suffix} is not supported. Please provide a .txt file.\nScript terminated!')

    if not queries:
        exit('Failed to read the queries from the provided file.\nScript terminated!')

    return queries


# Check if the input file exists and is valid. If true, read the input file
def get_credentials(credentials_file):
    credentials = None
    if not credentials_file.is_file():
        exit(f"file: {credentials_file}, does not exist. Script terminated!")

    if credentials_file.suffix == '.json':
        with open(credentials_file, "r") as file:
            credentials = json.load(file)
    else:
        exit(f'File type: {credentials_file.suffix} is not supported for credentials.\nScript terminated!')

    if not credentials:
        exit('Failed to read the credentials from the provided file.\nScript terminated!')

    return credentials


# Wait time for API Limits
def wait(t):
    tqdm.write('\nRate Limits Hit! Waiting...')
    while t >= 0:
        mins, secs = divmod(t, 60)
        hours, mins = divmod(mins, 60)
        print('{:d}:{:02d}:{:02d}'.format(hours, mins, secs), end='\r')
        time.sleep(1)
        t -= 1


# Search
def start_search(queries, credentials, platform, api_type):
    results = pd.DataFrame()
    # Twitter Accounts
    if platform == '0':
        # GoogleAPI
        if api_type == '1':
            se = GoogleSearchEngine(google_api_key=credentials['api_key'], search_engine_id=credentials['twitter_seID'])

            for query in tqdm(queries):
                try:
                    tqdm.write(f'\nSearching for: {query}')
                    se.search(query=query, platform='twitter')
                    result = se.get_results()
                    results = results.append(result)
                except HttpError as err:
                    if err.resp.status == 429:
                        wait(60 * 60 * 24)
                        se.search(query=query, platform='twitter')
                        result = se.get_results()
                        results = results.append(result)
                    else:
                        exit(f"Unexpected error: {err}")
                except Exception as err:
                    exit(f"Unexpected error: {err}")

        # TwitterAPI
        if api_type == '0':
            se = TwitterSearchEngine(twitter_credentials=credentials)

            for query in tqdm(queries):
                try:
                    tqdm.write(f'\nSearching for: {query}')
                    se.search(query=query, count=10)
                    result = se.get_results()
                    results = results.append(result)
                except tweepy.RateLimitError as err:
                    wait(60 * 15)
                    se.search(query=query, count=10)
                    result = se.get_results()
                    results = results.append(result)
                except Exception as err:
                    exit(f'Something went wrong: {err}')

    # Facebook Accounts
    else:
        se = GoogleSearchEngine(google_api_key=credentials['api_key'], search_engine_id=credentials['twitter_seID'])

        for query in tqdm(queries):
            try:
                tqdm.write(f'\nSearching for: {query}')
                se.search(query=query, platform='facebook')
                result = se.get_results()
                results = results.append(result)
            except HttpError as err:
                if err.resp.status == 429:
                    wait(60 * 60 * 24)
                    se.search(query=query, platform='facebook')
                    result = se.get_results()
                    results = results.append(result)
                else:
                    exit(f"Unexpected error: {err}")
            except Exception as err:
                exit(f"Unexpected error: {err}")

    return results


def main():
    args = arguments()
    if not args.single_mode:
        # Read the queries
        input_file = Path(args.input)
        queries = get_queries(input_file)
    else:
        queries = ' '.join(args.input.split('_'))
        queries = [queries]

    # Read the credentials
    credentials_file = Path(args.credentials)
    credentials = get_credentials(credentials_file)

    # Choose a platform
    while True:
        platform = input('\nPlease select a social media platform:\n- 0: Twitter\n- 1: Facebook.\n')
        if platform == '1' or platform == '0':
            if platform == '1':
                print('Facebook was chosen as the platform.')
            elif platform == '0':
                print('Twitter was chosen as the platform.')
            break
        else:
            print(f"Sorry, {platform} is not a valid input. Please, input 0 for Twitter or 1 for Facebook.")

    # Choose an API
    if platform == '0':
        while True:
            api_type = input('\nPlease select the API to search with:\n- 0: TwitterAPI\n- 1: GoogleAPI\n')
            if api_type == '1' or api_type == '0':
                if api_type == '1':
                    print('GoogleAPI was chosen.')
                elif api_type == '0':
                    print('TwitterAPI was chosen.')
                break
            else:
                print(f"Sorry, {api_type} is not a valid input.")
    elif platform == '1':
        api_type = '1'

    # Search
    print('\nStarting search.')
    results = start_search(queries=queries, credentials=credentials, platform=platform, api_type=api_type)

    if not args.single_mode:
        # Export Results
        if platform == '0':
            plat_name = 'twitter_accounts'
        elif platform == '1':
            plat_name = 'facebook_accounts'

        output_file = Path(input_file.parent, f'{input_file.stem}_{plat_name}_results.csv')
        results.to_csv(output_file, index=False)
        print(f'\nResult Exported to {output_file}')
    else:
        print(f'\n\nThe possible accounts for "{queries[0]}" are: \n')
        print('-------------------------------\n')
        for i, col in enumerate(results.columns):
            if col != 'Query':
                print(f'{col}: {results.loc[0,col]}')
