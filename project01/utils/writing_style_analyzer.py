# coding: utf-8
"""
The file used for the writing style analysis.
"""

from writing_styles import WritingStyle, GeolocatedWritingStyle, get_difference, MINIMUM_WRITING_STYLES_COUNT
from edit_extractor import Page, Revision

import pickle
import random
import os.path

__author__ = 'wikipedia_project_group'


class WritingStyleProcessor:
    """Processes wikipedia pages, determines (geo-located) writing styles and predicts writing styles."""

    def __init__(self):
        self.writing_style_learner = WritingStyleLearner()

    def process_wikipedia_page(self, page):
        """
        Processes a single wikipedia page.
        :param page: The actual page
        """
        for revision in page.revisions:
            writing_style = WritingStyle(revision.diff_content, revision.country)
            self.writing_style_learner.add_writing_style(writing_style)

    def predict_text(self, text):
        """
        Gets the geo-location-probabilities and the geo-location-prediction for a text.
        :param text: The actual text
        :return: The probabilities and the prediction
        """
        writing_style = WritingStyle(text, None)
        writing_style_predictor = WritingStylePredictor(self.writing_style_learner)

        probabilities = writing_style_predictor.get_probabilities(writing_style)
        predicted_geo_location = writing_style_predictor.predict_geo_location(writing_style)

        return probabilities, predicted_geo_location

    def get_geo_located_writing_styles(self):
        """
        Only returns the geo-located writing styles that contain a certain threshold of texts.
        :return: The geo-located writing styles
        """
        filtered = []

        for gl_writing_style in self.writing_style_learner.geo_located_writing_styles:
            if gl_writing_style.count >= MINIMUM_WRITING_STYLES_COUNT:
                filtered.append(gl_writing_style)

        return filtered


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
        found = False
        for i, v in enumerate(self.geo_located_writing_styles):
            if self.geo_located_writing_styles[i].geo_location == writing_style.geo_location:
                self.geo_located_writing_styles[i].add_writing_style(writing_style)
                found = True
                break

        if not found:
            gl_writing_style = GeolocatedWritingStyle(writing_style)
            self.geo_located_writing_styles.append(gl_writing_style)


class WritingStylePredictor:
    """Predicts the geo-location for a given writing style."""

    def __init__(self, writing_style_learner):
        self.geo_located_writing_styles = writing_style_learner.geo_located_writing_styles

    def get_probabilities(self, writing_style):
        """
        Gets the probabilities of the geo-locations for a given writing style
        :param writing_style: The actual writing style
        :return: The probabilities of the geo-locations
        """
        probabilities = {}

        for gl_writing_style in self.geo_located_writing_styles:
            difference = get_difference(gl_writing_style, writing_style)

            if difference is not None:
                probabilities[gl_writing_style.geo_location] = difference

        return probabilities

    def predict_geo_location(self, writing_style):
        """
        Predicts the geo-location based on the tags
        :param writing_style: The actual writing style
        :return: The predicted geo-location
        """
        probabilities = self.get_probabilities(writing_style)

        prediction, prediction_value = '', -1
        for geo_location, differences in probabilities.items():
            if prediction_value == -1 or differences[2] < prediction_value:
                prediction = geo_location
                prediction_value = differences[2]

        return prediction


def train_writing_style_predictor():
    processor = WritingStyleProcessor()

    for file_name in os.listdir("../data/pickle"):
        page = pickle.load(open("../data/pickle/" + file_name, 'rb'))
        processor.process_wikipedia_page(page)
        print("Processed: " + page.title)

    pickle.dump(processor, open("../data/trained_processor", 'wb'))

if __name__ == '__main__':
    train_writing_style_predictor()
