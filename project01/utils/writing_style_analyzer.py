# coding: utf-8
"""
The file used for the writing style analysis.
"""

from writing_styles import GeolocatedWritingStyle

__author__ = 'wikipedia_project_group'


class WritingStyleLearner:
    """Learns the mean writing style for different geo-locations."""

    def __init__(self):
        # Creates and empty list of geo-located writing styles
        self.geo_located_writing_styles = []

    def add_writing_style(self, writing_style):
        """
        Adds a writing style to the learner
        :param writing_style: The actual writing style
        """
        # Retrieves the right geo-located writing style from the list and adds the current writing style to it
        # If the entry does not exist it creates a new writing geo-located writing style and adds it to the list
        self.geo_located_writing_styles = writing_style


class WritingStylePredictor:
    """Predicts the geo-location for a given writing style."""

    def __init__(self, writing_style_learner):
        self.geo_located_writing_styles = writing_style_learner.geo_located_writing_styles

    def predict_geo_location(self, writing_style):
        """
        Predicts the geo-location for a given writing style
        :param writing_style: The actual writing style
        :return: The geo-location
        """
        # Iterates through all the geo-located writing styles and returns the best fitting one
        # (alternatively it returns all probabilities)
        self.geo_located_writing_styles = writing_style
