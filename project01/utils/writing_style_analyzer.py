"""The file used for the writing-style-analyzation."""
import copy
import numpy as np

import nltk

import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import FeatureUnion
# from sklearn.metrics import confusion_matrix

# from scipy.sparse import hstack
import pandas as pd

# import matplotlib.pylab as pl

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


def train_model(train_set):
    """
    Train the models, using 10-fold-cv and LibLinear classification.
    :param train_set: The set that is used for training
    """
    # Create two blocks of features, word anc character n-grams, size of 2
    # We can also append here multiple other features in general
    word_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False, max_features=2000)
    char_vector = TfidfVectorizer(ngram_range=(2, 3), analyzer="char", binary=False, min_df=0, max_features=2000)
    # tag_vector = TfidfVectorizer(analyzer="word", ngram_range=(2, 2), binary=False, max_features=2000,
    #                             decode_error='ignore')

    # Our vectors are the feature union of word/char n-grams
    inner_vectorizer = FeatureUnion([("chars", char_vector), ("words", word_vector)])

    # Corpus is a list with the n-word chunks
    corpus = []
    # Classes is the labels of each chunk
    classes = []
    # The tags of the n-word chunks
    # tags = []

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
    print("Processed Countries:\n"+str(used_countries))

    # Fit the model of tf-idf vectors for the corpus
    x1 = inner_vectorizer.fit_transform(corpus)
    # x2 = tag_vector.fit_transform(tags)

    # matrix = hstack((x1, x2), format='csr')

    print("Number of features: ", len(inner_vectorizer.get_feature_names()))

    x = x1.toarray()
    y = np.asarray(classes)

    print()
    print("Training model...")

    inner_model = LinearSVC(loss='hinge', dual=True)
    inner_model.fit(x, y)

    print("Saving model...")

    pickle.dump(inner_model, open('../data/model/trained_model', 'wb'))

    print("Saving tfidf-vectorizers...")

    pickle.dump(inner_vectorizer, open('../data/model/vectorizer', 'wb'))
    # pickle.dump(tag_vector, open('../data/model/tag_vector', 'wb'))

    # y_prediction = model.fit(x_train, y_train).predict(x_test)
    # cm = confusion_matrix(y_test, y_prediction)
    #
    # print(cm)
    #
    # pl.matshow(cm)
    # pl.title('Confusion matrix')
    # pl.colorbar()
    # pl.ylabel('True label')
    # pl.xlabel('Predicted label')
    # pl.show()


def predict_geo_location(text, path='../data/model/'):
    """
    Predicts the geo-location of a given text.
    :param text: The actual text
    :param path: The path to the dumps
    :return: The most likeliest geo-location
    """
    global vectorizer, model

    if vectorizer is None or model is None:
        vectorizer = pickle.load(open(path + 'vectorizer', 'rb'))
        model = pickle.load(open(path + 'trained_model', 'rb'))

    corpus = [text]
    x1 = vectorizer.transform(corpus)
    y_prediction = model.predict(x1.toarray())

    return y_prediction[0]

if __name__ == '__main__':
    corpora = load_corpus("../data/countries")
    train_model(corpora)
