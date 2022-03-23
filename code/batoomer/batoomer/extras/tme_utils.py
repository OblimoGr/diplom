# This file contains functions that are necessary for the statuses-mentions classifiers to work.
# Some of the function need to be explicitly imported

from batoomer.extras.utils import my_print, clean_text, tokenize_lemmatize, remove_stopwords
import tweepy
from tqdm import tqdm
import spacy


# ------------------------------------ Functions For TME Models -------------------------------------------
# This functions have to be explicitly imported in order for the corresponding models to work
# parl -> greek parliament members classifier

def get_numeric_data_parl_tme(df):
    """
    This function is used by the model classifier_parl_tme. It performs all necessary pre processing and returns
    the numeric data the classifiers requires.
    :param df: DataFrame
    :return: DataFrame columns with the pre processed text data.
    """
    data = df['mentions_politician_count'].to_numpy()
    return data.reshape(-1, 1)


def get_text_data_parl_tme(df):
    """
    This function is used by the model classifier_parl_tme. It performs all necessary pre processing and returns
    the text data the classifiers requires.
    :param df: DataFrame
    :return: DataFrame columns with the pre processed text data.
    """
    nlp_el = spacy.load('el_core_news_md')
    nlp_en = spacy.load('en_core_web_sm')
    STOPWORDS = set(list(spacy.lang.en.STOP_WORDS) + list(spacy.lang.el.STOP_WORDS))

    df = df.copy()
    df['textdata'] = clean_text(df['recent_100_tweets'])
    df['textdata'] = df['textdata'].apply(lambda row: tokenize_lemmatize(row, nlp_el))
    df['textdata'] = df['textdata'].apply(lambda row: ' '.join(row))
    df['textdata'] = df['textdata'].apply(lambda row: remove_stopwords(row, nlp_el, STOPWORDS))
    df['textdata'] = df['textdata'].apply(lambda row: ' '.join(row))
    return df.textdata


# ------------------------------------- Functions For Data Fetching ---------------------------------------
def fetch_statuses(nodes, API, verbose, count=100):
    """
    Given a set of nodes, returns <count> recent statuses for each node. If permission is not given by the node
    to extract its Statuses, an empty String is considered as it's statuses. Note the statuses are concentrated in
    a single String Object. To fetch each status separately, this method is not recommended, however it can be used.

    :param nodes: List of screen_names or IDs for each Node.
    :param API: tweepy API object
    :param verbose: Int, If 1 prints, else it doesn't print.
    :param count: Int, Number of statuses to fetch. Default = 100
    :return: List of statuses for each Node.
    """

    # Variable to hold the results
    recent_100_tweets = []
    my_print(f'\nFetching Statuses.', verbose)

    # Main Loop to iterate each node
    for node in tqdm(nodes, leave=False, desc='Fetching Statuses'):
        # Variable to Hold the Statuses
        statuses = ''
        try:
            # Fetch Statuses for the node
            for status in tweepy.Cursor(API.user_timeline, node).items(count):
                statuses = statuses + ' ' + status.text

        except tweepy.error.TweepError as err:
            my_print(f'Not authorized to fetch statuses for node: {node}. Setting statuses to empty string.', verbose)
        except Exception as err:
            raise Exception(f'An unknown Error has occurred.\n{err}')

        recent_100_tweets.append(statuses)

    my_print('Fetching completed.\n', verbose)
    return recent_100_tweets


def calculate_parliament_mentions(data, API, verbose, twitter_credentials):
    """
    Given a DataFrame containing statuses. Extracts mentions, classifies them using classifier_parl_nd, and calculates
    the number of mentions that are parliament members.

    :param data: pandas DataFrame containing a column named 'recent_100_tweets'
    :param API: tweepy API object
    :param verbose: Int, If 1 prints, else it doesn't print.
    :param twitter_credentials: json object containing twitter api credentials.
    :return: List of integers
    """
    from batoomer.twitter_nodes.classification import Classifier
    from batoomer.extras.nd_utils import fetch_nd_data
    result = []

    clf = Classifier(model_name='classifier_parl_nd', twitter_credentials=twitter_credentials, verbose=0)
    mentions = data['recent_100_tweets'].str.findall(r'@\w+')
    my_print('\nCalculating number of mentions that are parliament members. This will take some time.', verbose)
    for accs in tqdm(mentions, leave=False, desc='Calculating mentions parliament member count'):
        # Get Required Data
        me_data = fetch_nd_data(nodes=accs, API=API, verbose=0, extended=False)

        if not me_data.empty:
            # Predict
            labels = clf.predict_given_data(me_data)
            me_data['label'] = labels

            # COUNT
            count = len(me_data[me_data['label'] == 1])
        else:
            count = 0

        result.append(count)

    my_print('Calculations completed.\n', verbose)
    return result
