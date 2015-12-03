# coding: utf-8
"""
The file used for the structure of the writing styles.
Uses writing_style (to install: 'pip install writing_style')
Uses nltk (to install: 'pip install nltk' and nltk.download('punkt') and nltk.download('averaged_perceptron_tagger')
"""

from writing_style.analyzer import stdev_word_lengths, stdev_sentence_lengths

import nltk
from collections import Counter
from copy import deepcopy

__author__ = 'wikipedia_project_group'

MINIMUM_WRITING_STYLES_COUNT = 10


def get_similarity(gl_writing_style, writing_style):
    """
    Gets the percentual similarity between a geo-located and normal writing style.
    :param gl_writing_style: The geo-located writing style
    :param writing_style: The writing style
    :return: The similarity in percentage as a list
    """
    # Return if the geo-located writing style has not enough entries
    if gl_writing_style.count < MINIMUM_WRITING_STYLES_COUNT:
        return None

    gl_mean_tags = gl_writing_style.get_mean_tags()
    tag_differences = deepcopy(writing_style.tag_counts)

    for key, value in writing_style.tag_counts.items():
        if gl_mean_tags[key] == 0:
            tag_differences[key] = 0.0
        else:
            tag_differences[key] = (gl_mean_tags[key] - float(value)) / gl_mean_tags[key]

    match = 0.0
    for _, value in tag_differences.items():
        match += 1 - abs(value)

    match /= len(writing_style.tag_counts)

    return [(1 - abs((gl_writing_style.mean_stdev_word_length - writing_style.stdev_word_length) /
                     gl_writing_style.mean_stdev_word_length)) * 100,

            (1 - abs((gl_writing_style.mean_stdev_sentence_length - writing_style.stdev_sentence_length) /
                     gl_writing_style.mean_stdev_sentence_length)) * 100,

            match * 100]


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

        # The writing style
        self.stdev_word_length = stdev_word_lengths(text)
        self.stdev_sentence_length = stdev_sentence_lengths(text)

        # Make sure that each text has at least one sentence
        if self.stdev_sentence_length == 0:
            self.stdev_sentence_length = 1

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

        return tag_counts


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
        self.tag_counts = Counter()
        self.mean_stdev_word_length = writing_style.stdev_word_length
        self.mean_stdev_sentence_length = writing_style.stdev_sentence_length

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
        self.mean_stdev_word_length = (self.mean_stdev_word_length * self.count +
                                       writing_style.stdev_word_length) / (self.count + 1)

        self.mean_stdev_sentence_length = (self.mean_stdev_sentence_length * self.count +
                                           writing_style.stdev_sentence_length) / (self.count + 1)

        # Add the tags of the writing-style to the dictionary
        self.tag_counts += writing_style.tag_counts

        self.count += 1
