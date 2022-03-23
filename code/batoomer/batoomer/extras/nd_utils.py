# This file contains functions that are necessary for the name-description classifiers to work.
# Some of the function need to be explicitly imported
from batoomer.extras.utils import my_print, clean_text, tokenize_lemmatize, remove_stopwords
import tweepy
import pandas as pd
from tqdm import tqdm
import spacy


# ------------------------------------ Functions For ND Models -------------------------------------------
# This functions have to be epxlicity imported in order for the corresponding models to work
# parl -> greek parliament members classifier

def get_text_data_parl_nd(df):
    """
    This function is used by the model classifier_parl_nd. It performs all necessary pre processing and returns
    the data the classifiers requires.
    :param df: DataFrame
    :return: DataFrame columns with the pre processed text data.
    """
    nlp_el = spacy.load('el_core_news_md')
    nlp_en = spacy.load('en_core_web_sm')
    STOPWORDS = set(list(spacy.lang.en.STOP_WORDS) + list(spacy.lang.el.STOP_WORDS))

    df['textdata'] = clean_text(df['name'] + ' ' + df['description'])
    df['textdata'] = df['textdata'].apply(lambda row: tokenize_lemmatize(row, nlp_el))
    df['textdata'] = df['textdata'].apply(lambda row: ' '.join(row))
    df['textdata'] = df['textdata'].apply(lambda row: remove_stopwords(row, nlp_el, STOPWORDS))
    df['textdata'] = df['textdata'].apply(lambda row: ' '.join(row))

    return df.textdata


# ------------------------------------- Functions For Data Fetching ---------------------------------------
def fetch_nd_data(nodes, API, verbose, extended=False):
    """
    Given a list of nodes, fetches all required data for the model nd to work.

    :param nodes: List of Twitter screen_names or IDs.
    :param API: Tweepy API object. Authentication should be handled outside this function.
    :param verbose: Int, If 1 prints, else it doesn't print.
    :param extended: Boolean, if True in addition to name and description, returns statuses_count, friends_count,
    followers_count. Defaults to False.
    :return: pandas DataFrame containing the results.
    """
    # Variable to hold results
    results = []

    my_print('\nFetching Required Data For Model ND.', verbose)
    # Main Loop

    dis = False
    if verbose != 1:
        dis = True

    for node in tqdm(nodes, disable=dis, leave=False, desc='Fetching names and descriptions'):
        try:
            user = API.get_user(node)
            results.append(
                [user.screen_name, user.name, user.description,
                 user.statuses_count, user.friends_count, user.followers_count])
        except tweepy.error.TweepError as err:
            my_print(f'Error for node {node}: {err.reason}.\nSetting values to empty strings and zeros.', verbose)
            results.append(['', '', '', 0, 0, 0])
        except Exception as err:
            raise Exception(f'An unknown Error has occurred.\n{err}')

    if not results:
        results.append(['', '', '', 0, 0, 0])
    
    results = pd.DataFrame(results)
    results.columns = ['screen_name', 'name', 'description',
                       'statuses_count', 'friends_count', 'followers_count']
    results = results.reset_index().drop('index', axis=1)

    my_print('Fetching completed.\n', verbose)

    if not extended:
        return results[['screen_name', 'name', 'description']]

    return results
