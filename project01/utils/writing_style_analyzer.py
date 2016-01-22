"""The file used for the writing-style-analyzation."""
import copy
import numpy as np

import nltk

import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC, SVC
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import FeatureUnion

import pandas as pd

import sys

from os import listdir
from os.path import isfile, join, getsize

vectorizer = None
model = None
min_filesize = 40000


def load_corpus(directory):
    """
    Loads the corpus (in this case countries) from within a given directory.
    :param directory: The actual directory
    :return: Returns the train-set
    """
    train_files = [f for f in listdir(directory) if isfile(join(directory, f))]
    train_set = {}

    if ".DS_Store" in train_files:
        train_files.remove(".DS_Store")

    global used_countries, min_filesize
    used_countries = copy.deepcopy(train_files)

    for f in train_files:
        size_of_file = getsize(directory + '/' + f)

        # A file needs to be at least 40KB big
        if size_of_file < min_filesize:
            used_countries.remove(f)
            continue

        train_set[f] = []

        label = f
        df = pd.read_csv(directory + "/" + f, sep="\t", dtype={'id': object, 'text': object})

        for row in df['text']:
            if type(row) is str:
                train_set[label].append({"label": label, "text": row})

    return train_set


def retrieve_pos_tags(text):
    """
    Retrieves the pos-tags of a text.
    :param text: The actual text
    :return: Returns the pos-tags of the given text
    """
    tokens = nltk.word_tokenize(text)
    return " ".join([tag for (word, tag) in nltk.pos_tag(tokens)])


def train_model(train_set, mode='linear'):
    """
    Train the models, using 10-fold-cv and LibLinear classification.
    :param train_set: The set that is used for training
    :param mode: The that gets used for training
    """
    # Create two blocks of features, word anc character n-grams, size of 2
    # We can also append here multiple other features in general
    word_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False, max_features=2000)
    char_vector = TfidfVectorizer(ngram_range=(2, 3), analyzer="char", binary=False, min_df=0, max_features=2000)

    # Our vectors are the feature union of word/char n-grams
    inner_vectorizer = FeatureUnion([("chars", char_vector), ("words", word_vector)])

    # Corpus is a list with the n-word chunks
    corpus = []
    # Classes is the labels of each chunk
    classes = []

    # Load training set
    for key, country_list in train_set.items():
        # print("Processing " + '"' + key + '"')

        for item in country_list:
            corpus.append(item['text'])
            classes.append(item['label'])
            # tags.append(retrieve_pos_tags(item['text']))

    print()
    print("Size of corpus: " + str(sys.getsizeof(corpus)))
    print("Number of training instances: ", len(classes))
    print("Number of training classes: ", len(set(classes)))
    global used_countries
    print("Processed Countries:\n" + str(used_countries))

    # Fit the model of tf-idf vectors for the corpus
    x1 = inner_vectorizer.fit_transform(corpus)

    print("Number of features: ", len(inner_vectorizer.get_feature_names()))

    x = x1.toarray()
    y = np.asarray(classes)

    print()
    print("Training model...")

    if mode == 'kernel_rbf':
        inner_model = SVC(kernel="rbf")
        inner_model.fit(x, y)
    elif mode == 'kernel_poly':
        inner_model = SVC(kernel="poly")
        inner_model.fit(x, y)
    elif mode == 'kernel_linear':
        inner_model = SVC(kernel="linear")
        inner_model.fit(x, y)
    elif mode == 'neural_network':
        inner_model = BernoulliRBM()
        inner_model.fit(x, y)
    else:
        inner_model = LinearSVC(loss='hinge', dual=True)
        inner_model.fit(x, y)
        mode = 'linear'

    print("Saving model...")

    pickle.dump(inner_model, open('../data/model/trained_model_' + mode, 'wb'))

    print("Saving tfidf-vectorizers...")

    pickle.dump(inner_vectorizer, open('../data/model/vectorizer_' + mode, 'wb'))


def predict_geo_location(text, path='../data/model/', mode='linear'):
    """
    Predicts the geo-location of a given text.
    :param text: The actual text
    :param path: The path to the dumps
    :param mode: The model that gets used for predicting
    :return: The most likeliest geo-location
    """
    global vectorizer, model

    if vectorizer is None or model is None:
        vectorizer = pickle.load(open(path + 'vectorizer_' + mode, 'rb'))
        model = pickle.load(open(path + 'trained_model_' + mode, 'rb'))

    corpus = [text]
    x1 = vectorizer.transform(corpus)
    y_prediction = model.predict(x1.toarray())

    return y_prediction[0]

if __name__ == '__main__':
    corpora = load_corpus("../data/countries")
    train_model(corpora, mode='linear')
