# coding: utf-8
"""
The file used for the structure of the writing styles.
Uses writing_style (to install: 'pip install writing_style')
Uses nltk (to install: 'pip install nltk' and nltk.download('punkt') and nltk.download('averaged_perceptron_tagger')
"""
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from writing_style.analyzer import average_word_lengths, average_sentence_lengths
import nltk
from collections import Counter
from copy import deepcopy

__author__ = 'wikipedia_project_group'

MINIMUM_WRITING_STYLES_COUNT = 50


def get_difference(gl_writing_style, writing_style):
    """
    Gets the difference between a geo-located and a writing style.
    :param gl_writing_style: The geo-located writing style
    :param writing_style: The writing style
    :return: The difference in percentage as a list
    """
    # Return if the geo-located writing style has not enough entries
    if gl_writing_style.count < MINIMUM_WRITING_STYLES_COUNT:
        return None

    gl_mean_tags = gl_writing_style.get_mean_tags()
    tag_differences = deepcopy(writing_style.tag_counts)

    # global dictionary with mean term frequency for every item
    gl_mean_terms = gl_writing_style.get_mean_terms()


    for key, value in writing_style.tag_counts.items():
        if gl_mean_tags[key] == 0:
            tag_differences[key] = 0.0
        else:
            tag_differences[key] = abs(gl_mean_tags[key] - value)

    match = 0.0
    for _, value in tag_differences.items():
        match += value

    match /= len(writing_style.tag_counts)

    return [abs(gl_writing_style.mean_word_length - writing_style.average_word_length),

            abs(gl_writing_style.mean_sentence_length - writing_style.average_sentence_length),

            match]


class WritingStyle:
    """A text with writing style and geo-location."""

    def __init__(self, text, geo_location):
        """
        Initializes the writing-style.
        :param text: The actual text
        :param geo_location: The actual geo-location
        """
        # The text and geo-location
        self.text = text
        self.geo_location = geo_location

        # Determine the tag-counts
        self.tag_counts = self._get_tag_counts(text)

        # The word- and sentence-lengths
        self.average_word_length = average_word_lengths(text)
        self.average_sentence_length = average_sentence_lengths(text)

        # Terms without stopwords (THIS FEATURE IS NOT BEING USED YET)
        self.term_counter = 0
        self.revision_term_dictionary = {}

        self.term_dictionary = {}
        # Count the terms, override self.term_counter and revision_term_dictionary
        self._get_term_counts(text)

        # Make sure that each text has at least one sentence
        if self.average_sentence_length == 0:
            self.average_sentence_length = 1

    @staticmethod
    def _get_tag_counts(text):
        """
        Retrieves the tags from a text and returns their counts.
        :param text: The actual text
        :return: The counts of the tags
        """
        words = nltk.word_tokenize(text)
        tags = nltk.pos_tag(words)
        tag_counts = Counter(tag for word, tag in tags)

        for key, value in tag_counts.items():
            tag_counts[key] = value / len(tags)

        return tag_counts

    def _get_term_counts(self, text):
        """
        Removes stopwords and counts the absolute terms and builds up a dictionary
        :param text:
        """

        # Import punctuation and stopwords
        tokenizer = RegexpTokenizer(r'\w+')
        text = tokenizer.tokenize(text)
        stop = stopwords.words('english')
        text_wo_stop = [i for i in text if i not in stop]

        for term in text_wo_stop:
            self.term_counter += 1
            if term in self.term_dictionary:
                self.term_dictionary[term] += 1
            else:
                self.term_dictionary[term] = 1


class GeolocatedWritingStyle:
    """The writing style for a specific geo-location."""

    def __init__(self, writing_style):
        """
        Initializes the geo-located writing-style.
        :param writing_style: The actual writing-style
        """

        # The geo-location
        self.geo_location = writing_style.geo_location

        # The mean writing-style
        self.count = 1
        self.tag_counts = writing_style.tag_counts
        self.mean_word_length = writing_style.average_word_length
        self.mean_sentence_length = writing_style.average_sentence_length

        # Term-Frequency: absolute counter of terms and a dictionary (THIS FEATURE IS NOT BEING USED YET)
        self.term_counter = 0
        # Term-Frequency: absolute counter of terms and a dictionary,
        self.term_counter = writing_style.term_counter
        self.term_dictionary = {}
        self.word_pool = len(writing_style.term_dictionary)

    def get_mean_tags(self):
        """
        Calculates the mean counts of the tags and returns them
        :return: The mean of the tags
        """
        tag_counts = deepcopy(self.tag_counts)

        for key, value in tag_counts.items():
            tag_counts[key] = float(value) / float(self.count)

        return tag_counts


    def add_writing_style(self, writing_style):
        """
        Adds a writing-style.
        :param writing_style: The actual writing-style
        """
        self.mean_word_length = (self.mean_word_length * self.count +
                                 writing_style.average_word_length) / (self.count + 1)

        self.mean_sentence_length = (self.mean_sentence_length * self.count +
                                     writing_style.average_sentence_length) / (self.count + 1)

        # Add the tags of the writing-style to the dictionary
        self.tag_counts += writing_style.tag_counts

        self.count += 1

        # terms
        self.term_counter = self.term_counter + writing_style.term_counter
        for term, count in writing_style.term_dictionary.items():
            if term in self.term_dictionary:
                self.term_dictionary[term] = self.term_dictionary[term] + count
            else:
                self.term_dictionary[term] = count

        self.word_pool = (self.word_pool * self.count + len(writing_style.term_dictionary)) / (self.count + 1)

        self.count += 1


    def get_mean_terms(self):
        """
        Calculates the mean counts of the tags and returns them
        :return: The mean of the tags
        """
        rel_term_dictionary = deepcopy(self.term_dictionary)

        for key, value in rel_term_dictionary.items():
            rel_term_dictionary[key] = float(value) / float(self.term_counter)

        return rel_term_dictionary
