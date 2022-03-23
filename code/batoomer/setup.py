from setuptools import setup, find_packages
import pathlib

# Version Number
version = '0.0.2'

# Description
description = 'This Package was developed during the thesis: Classification of Social Media Nodes, Democritus ' \
              'University of Thrace '

# Dependencies
# TODO ADD dependencies
install_requires = ['tweepy', 'pandas', 'numpy', 'tqdm', 'spacy', 'joblib', 'google-api-python-client']

# Entry points
entry_points = {
    'console_scripts': ['search-accounts=bin.search_accounts:main']
}

# Readme file
curr_path = pathlib.Path(__file__).parent.resolve()
long_description = (curr_path / 'README.md').read_text(encoding='utf-8')

# Setup
setup(
    name='batoomer',
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Batouchan Omer',
    author_email=' ',
    packages=find_packages(),
    package_data={'batoomer': ['classifiers/*']},
    python_requires='>=3.5, <4',
    install_requires=install_requires,
    entry_points=entry_points
)
