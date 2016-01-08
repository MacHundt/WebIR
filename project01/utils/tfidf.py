from os import listdir
from os.path import isfile, join

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

import nltk

from scipy import sparse as sp


def load_corpus(input_dir):
    train_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    train_set = []

    for filename in train_files:
        df = pd.read_csv(input_dir + '/' + filename, sep="\t", dtype={'id': object, 'text': object})

        for row in df['text']:
            train_set.append({"label": filename, "text": row})

    return train_set


def pos_tags(txt):
    tokens = nltk.word_tokenize(txt)
    return " ".join([tag for (word, tag) in nltk.pos_tag(tokens)])


def main():
    train_set = load_corpus("asdf")

    word_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), max_features=2000, binary=False)
    char_vector = TfidfVectorizer(ngram_range=(2, 3), analyzer="char", max_features=2000, binary=False, min_df=0)

    corpus = []
    classes = []
    tags = []

    for item in train_set:
        corpus.append(item["text"])
        classes.append(item["label"])

    vectorizer = FeatureUnion([("chars", char_vector), ("words", word_vector)])

    X = vectorizer.fit(corpus)

    tag_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False,
                                 max_features=2000, decode_error='ignore')

    x1 = vectorizer.fit_transform(corpus)
    x2 = vectorizer.fit_transform(tags)

    X = sp.hstack((x1, x2), format='csr')
