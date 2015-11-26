# coding: utf-8
"""
The file used for the structure of the writing styles.
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

        # The writing style
        self.average_word_length = average_word_lengths(text)
        self.stdev_word_length = stdev_word_lengths(text)
        self.average_sentence_length = average_sentence_lengths(text)
        self.stdev_sentence_length = stdev_sentence_lengths(text)


class GeolocatedWritingStyle:
    """The writing style for a specific geo-location."""

    def __init__(self, geo_location):
        """
        Initializes the geo-located writing-style.
        :param geo_location: The actual writing-style
        """

        # The geo-location
        self.geo_location = geo_location

        # The mean writing-style
        self.text_count = 0
        self.mean_average_word_length = 0
        self.mean_stdev_word_length = 0
        self.mean_average_sentence_length = 0
        self.mean_stdev_sentence_length = 0

    def add_writing_style(self, writing_style):
        """
        Adds a writing-style.
        :param writing_style: The actual writing-style
        """
        self.mean_average_word_length = (self.mean_average_word_length * self.text_count +
                                         writing_style.average_word_length) / self.text_count + 1

        self.mean_stdev_word_length = (self.mean_stdev_word_length * self.text_count +
                                       writing_style.stdev_word_length) / self.text_count + 1

        self.mean_average_sentence_length = (self.mean_average_sentence_length * self.text_count +
                                             writing_style.average_sentence_length) / self.text_count + 1

        self.mean_stdev_sentence_length = (self.mean_stdev_sentence_length * self.text_count +
                                           writing_style.stdev_sentence_length) / self.text_count + 1

        self.text_count += 1
