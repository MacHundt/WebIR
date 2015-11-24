# coding: utf-8
"""
The file used for the writing style analysis.
Uses writing_style (to install: 'pip install writing_style')
"""

from writing_style.analyzer import average_word_lengths, stdev_word_lengths, average_sentence_lengths,\
    stdev_sentence_lengths

__author__ = 'wikipedia_project_group'


def get_difference(text1, text2):
    """
    Gets the percentual difference in writing-style between two text-objects.
    :param text1: The first text-object
    :param text2: The second text-object
    :return: The difference in writing style
    """
    return [float(text1.average_word_length - text2.average_word_length) / text1.average_word_length,
            float(text1.stdev_word_length - text2.stdev_word_length) / text1.stdev_word_length,
            float(text1.average_sentence_length - text2.average_sentence_length) / text1.average_sentence_length,
            float(text1.stdev_sentence_length - text2.stdev_sentence_length) / text1.stdev_sentence_length]


class Text:
    """A text with writing style."""

    def __init__(self, text):
        """
        Initializes the Text-object
        :param text: The actual text
        """
        self.text = text

        self.average_word_length = average_word_lengths(text)
        self.stdev_word_length = stdev_word_lengths(text)
        self.average_sentence_length = average_sentence_lengths(text)
        self.stdev_sentence_length = stdev_sentence_lengths(text)