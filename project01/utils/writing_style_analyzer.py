"""The file used for the writing-style-analyzation."""

import numpy as np

import nltk

import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import FeatureUnion
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import train_test_split

from scipy.sparse import hstack
import pandas as pd

import matplotlib.pylab as pl

import sys

from os import listdir
from os.path import isfile, join


def split_word_batches(filename, size_of_chunk=100):
    """
    Open the file, remove mentions & links,  split it in  chunks of n words and return the n-word block
    """
    with open(filename, "r") as f:
        lines = f.readlines()
        text = ""
    for l in lines:
        tokens = l.strip().split()
        if len(tokens) > 1:
            text += " " + tokens[1]

    text = text.decode('utf-8').lower().split()
    text = [word for word in text if word[0] != "@" and 'http' not in word[0:4] and word[0] != '#']
    start = 0
    end = start + size_of_chunk

    while True:
        start = end
        end = start + size_of_chunk

        if end >= len(text):
            break

        yield ' '.join(text[start:end])


def load_corpus(input_dir):
    train_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    train_set = []

    for f in train_files:
        if f == ".DS_Store":
            continue

        label = f
        df = pd.read_csv(input_dir + "/" + f, sep="\t", dtype={'id': object, 'text': object})

        for row in df['text']:
            if type(row) is str:
                train_set.append({"label": label, "text": row})

    return train_set


def pos_tags(txt):
    tokens = nltk.word_tokenize(txt)
    return " ".join([tag for (word, tag) in nltk.pos_tag(tokens)])


def train_model(train_set):
    """
    Train the models, using 10-fold-cv and LibLinear classification.
    """
    # Create two blocks of features, word anc character n-grams, size of 2
    # We can also append here multiple other features in general
    word_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False, max_features=2000)
    char_vector = TfidfVectorizer(ngram_range=(2, 3), analyzer="char", binary=False, min_df=0, max_features=2000)
    # tag_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False, max_features=2000, decode_error='ignore')

    # Our vectors are the feature union of word/char n-grams
    vectorizer = FeatureUnion([("chars", char_vector), ("words", word_vector)])

    # Corpus is a list with the n-word chunks
    corpus = []
    # Classes is the labels of each chunk
    classes = []
    # The tags of the n-word chunks
    # tags = []

    # Load training sets, for males & females
    for item in train_set:
        corpus.append(item['text'])
        classes.append(item['label'])
        # tags.append(pos_tags(item['text']))

    print("size of corpus: " + str(sys.getsizeof(corpus)))
    print("num of training instances: ", len(classes))
    print("num of training classes: ", len(set(classes)))

    # Fit the model of tf-idf vectors for the corpus
    # X1 = vectorizer.fit_transform(corpus)
    # X2 = tag_vector.fit_transform(tags)

    matrix = vectorizer.fit_transform(corpus)
    # matrix = hstack((X1, X2), format='csr')

    print("num of features: ", len(vectorizer.get_feature_names()))
    print("training model")

    x = matrix.toarray()
    y = np.asarray(classes)

    model = LinearSVC(loss='l1', dual=True)

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42)
    y_prediction = model.fit(x_train, y_train).predict(x_test)
    cm = confusion_matrix(y_test, y_prediction)

    print("saving model")

    pickle.dump(model, '../data/trained_model', 'wb')

    print(cm)

    # Calculate the accuracy
    diagonal = 0
    rest = 0
    for i, _ in enumerate(cm):
        for j, _ in enumerate(cm[i]):
            if i == j:
                diagonal += cm[i][j]
            else:
                rest += cm[i][j]

    print("accuracy: " + str((1 - (rest / (diagonal + rest))) * 100) + '%')

    pl.matshow(cm)
    pl.title('Confusion matrix')
    pl.colorbar()
    pl.ylabel('True label')
    pl.xlabel('Predicted label')
    pl.show()


if __name__ == '__main__':
    corpora = load_corpus("../data/countries")

    train_model(corpora)
