# coding: utf-8
"""
The file used for the writing style analysis.
Uses writing_style (to install: 'pip install writing_style')
"""

from writing_style.analyzer import average_word_lengths, stdev_word_lengths, average_sentence_lengths,\
    stdev_sentence_lengths

__author__ = 'wikipedia_project_group'


def get_difference(wt1, wt2):
    """
    Gets the percentual difference between two writing styles.
    :param wt1: The first writing-style
    :param wt2: The second writing-style
    :return: The difference in percentage
    """
    return [float(wt1.average_word_length - wt2.average_word_length) / wt1.average_word_length,
            float(wt1.stdev_word_length - wt2.stdev_word_length) / wt1.stdev_word_length,
            float(wt1.average_sentence_length - wt2.average_sentence_length) / wt1.average_sentence_length,
            float(wt1.stdev_sentence_length - wt2.stdev_sentence_length) / wt1.stdev_sentence_length]


class WritingStyle:
    """A text with writing style."""

    def __init__(self, text):
        """
        Initializes the writing-style
        :param text: The actual text
        """
        self.text = text

        self.average_word_length = average_word_lengths(text)
        self.stdev_word_length = stdev_word_lengths(text)
        self.average_sentence_length = average_sentence_lengths(text)
        self.stdev_sentence_length = stdev_sentence_lengths(text)


class GeolocatedWritingStyle:
    """The writing style for a specific geo-location."""

    def __init__(self, geo_location):
        # The geo-location
        self.geo_location = geo_location

        # The writing-style
        self.text_count = 0
        self.average_word_length = 0
        self.stdev_word_length = 0
        self.average_sentence_length = 0
        self.stdev_sentence_length = 0

    def add_text(self, text):
        """
        Adds a text with writing style.
        :param text: The text with writing style
        """
        self.average_word_length = (self.average_word_length * self.text_count + text.average_word_length) / \
            self.text_count + 1
        self.stdev_word_length = (self.stdev_word_length * self.text_count + text.stdev_word_length) / \
            self.text_count + 1
        self.average_sentence_length = (self.average_sentence_length * self.text_count + text.average_sentence_length) / \
            self.text_count + 1
        self.stdev_sentence_length = (self.stdev_sentence_length * self.text_count + text.stdev_sentence_length) / \
            self.text_count + 1

        self.text_count += 1
