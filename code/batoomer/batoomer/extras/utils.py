def my_print(text, verbose, end='\n'):
    """
    Simple wrapper for the pythons default print() method.
    """
    if verbose == 1:
        print(text, end=end)


# Function For Text Normalization
def clean_text(data):
    """
    Removes URLs, anything that is not a alphabet letter and replaces multiple whitespaces with a single one.
    Finally, transforms all letters to lowercase.

    :param data: DataFrame column containing the text data.
    :return: DataFrame column containing processed text data.
    """
    urls = r'http\S+'
    non_unicode_char = r'\W'
    numbers = r'[0-9_]'
    fix_whitespace = r'\s+'
    single_whitespace = ' '

    data = (data.replace([urls], single_whitespace, regex=True)
            .replace([non_unicode_char, numbers], single_whitespace, regex=True)
            .replace(fix_whitespace, single_whitespace, regex=True))
    data = data.apply(lambda s: s.lower() if type(s) == str else s)
    return data


# NLP Functions
def remove_stopwords(row, nlp, STOPWORDS):
    """
    Removes stopwords from the data. This is used with the pandas DataFrame.apply() method.

    :param row: DataFrame row.
    :param nlp: spacy NLP model to perform tokenization.
    :param STOPWORDS: set of Stopwords to remove.
    :return: the row with the stopwords removed.
    """
    row = [str(token) for token in nlp(row)]
    return [w for w in row if w not in STOPWORDS]


def tokenize_lemmatize(row, nlp):
    """
    Lemmatizes words. This is used with the pandas DataFrame.apply() method.

    :param row: DataFrame row
    :param nlp: spacy NLP model to perform lemmatization
    :return: the row with the words lemmatized.
    """
    return [str(token.lemma_) for token in nlp(row)]

