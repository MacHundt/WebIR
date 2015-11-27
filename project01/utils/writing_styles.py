# coding: utf-8
"""
The file used for the structure of the writing styles.
Uses writing_style (to install: 'pip install writing_style')
Uses nltk (to install: 'pip install nltk' and nltk.download('punkt') and nltk.download('averaged_perceptron_tagger')
"""

from writing_style.analyzer import average_word_lengths, stdev_word_lengths, average_sentence_lengths,\
    stdev_sentence_lengths

import nltk
from collections import Counter

__author__ = 'wikipedia_project_group'


def get_difference(gl_writing_style, writing_style):
    """
    Gets the percentual difference between a geo-located and normal writing style.
    :param gl_writing_style: The geo-located writing style
    :param writing_style: The writing style
    :return: The difference in percentage
    """
    return [float(gl_writing_style.average_word_length - writing_style.average_word_length) /
            gl_writing_style.average_word_length,

            float(gl_writing_style.stdev_word_length - writing_style.stdev_word_length) /
            gl_writing_style.stdev_word_length,

            float(gl_writing_style.average_sentence_length - writing_style.average_sentence_length) /
            gl_writing_style.average_sentence_length,

            float(gl_writing_style.stdev_sentence_length - writing_style.stdev_sentence_length) /
            gl_writing_style.stdev_sentence_length]


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
        self.average_word_length = average_word_lengths(text)
        self.stdev_word_length = stdev_word_lengths(text)
        self.average_sentence_length = average_sentence_lengths(text)
        self.stdev_sentence_length = stdev_sentence_lengths(text)

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
        self.tag_counts = {}
        self.mean_average_word_length = writing_style.average_word_length
        self.mean_stdev_word_length = writing_style.stdev_word_length
        self.mean_average_sentence_length = writing_style.stdev_word_length
        self.mean_stdev_sentence_length = writing_style.stdev_sentence_length

    def add_writing_style(self, writing_style):
        """
        Adds a writing-style.
        :param writing_style: The actual writing-style
        """
        self.mean_average_word_length = (self.mean_average_word_length * self.count +
                                         writing_style.average_word_length) / (self.count + 1)

        self.mean_stdev_word_length = (self.mean_stdev_word_length * self.count +
                                       writing_style.stdev_word_length) / (self.count + 1)

        self.mean_average_sentence_length = (self.mean_average_sentence_length * self.count +
                                             writing_style.average_sentence_length) / (self.count + 1)

        self.mean_stdev_sentence_length = (self.mean_stdev_sentence_length * self.count +
                                           writing_style.stdev_sentence_length) / (self.count + 1)

        # Add the tags of the writing-style to the dictionary
        for tag, count in writing_style.tag_counts.items():
            if self.tag_counts.get(tag) is None:
                self.tag_counts[tag] = count
            else:
                self.tag_counts[tag] += count

        self.count += 1
