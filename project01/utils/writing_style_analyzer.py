# coding: utf-8
"""
The file used for the writing style analysis.
"""

from writing_styles import WritingStyle, GeolocatedWritingStyle, get_similarity

import pickle
import os.path
from edit_extractor import Page, Revision

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
        # Iterate over all revisions
        for revision in page.revisions:
            writing_style = WritingStyle(revision.diff_content, revision.country)
            self.writing_style_learner.add_writing_style(writing_style)

    def predict_text(self, text):
        """
        Predicts the geo-location of a text.
        :param text: The actual text
        :return: The geo-location
        """
        writing_style = WritingStyle(text, None)
        writing_style_predictor = WritingStylePredictor(self.writing_style_learner)

        predicted_geo_location = writing_style_predictor.predict_geo_location(writing_style)

        return predicted_geo_location


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

    def predict_geo_location(self, writing_style):
        """
        Predicts the geo-location for a given writing style
        :param writing_style: The actual writing style
        :return: The geo-location
        """
        # Iterates through all the geo-located writing styles and returns the best fitting one
        # (alternatively it returns all probabilities)
        differences = []

        for gl_writing_style in self.geo_located_writing_styles:
            difference = get_difference(gl_writing_style, writing_style)
            differences.append(difference)

            print(difference)

        return differences


def main():
    if not os.path.isfile("../data/pickle/trainingsset"):
        page = pickle.load(open("../data/pickle/Anarchism", 'rb'))
        processor = WritingStyleProcessor()

        processor.process_wikipedia_page(page)
        geo_located_writing_styles = processor.writing_style_learner.geo_located_writing_styles

        pickle.dump(geo_located_writing_styles, open("../data/pickle/trainingsset", 'wb'))
    else:
        geo_located_writing_styles = pickle.load(open("../data/pickle/trainingsset", 'rb'))

    writing_style = WritingStyle("this article uses both autistic people or autistic person and people with autism see section below in sociology for terminology. english language on the surface individuals who have autism are physically indistinguishable from those without. sometimes autism cooccurs with other disorders and in those cases outward differences may be apparent. some iew.pdf retrieved ::noted behaviours typically developing infants are social beings  early in life they gaze at people turn toward voices grasp at fingers and smile. in contrast most autistic children do not show special interest in faces and seem to have tremendous difficulty learning to engage in everyday human interaction. even in the first few months of life many autistic children seem indifferent to other people lacking the eye contact and interaction with others that non autistic children exhibit naturally. some infants with autism may appear very calm they may cry less often because they do not seek parental attention or ministration. for other children with autism infantile development progresses normally through language acquisition. between  months and  years however skills previously mastered disappear including language and social skills. it has been noted that members of prefer person page  february autistic adults at the autism society of america  conference felt that the term individuals with autism separates their autism from who they are. in other words they believe their autism is part of who they are and want to be called autistic adults.", None)
    for gl_writing_style in geo_located_writing_styles:
        similarity = get_similarity(gl_writing_style, writing_style)

        print("-" * 20)
        print("Geolocation: " + gl_writing_style.geo_location)
        print("Revision-Count: " + str(gl_writing_style.count))
        print("Similarity standard-deviation word-length: " + '%.2f' % similarity[0] + '%')
        print("Similarity standard-deviation sentence-length: " + '%.2f' % similarity[1] + '%')
        print("Similarity tag-counts: " + '%.2f' % similarity[2] + '%')
        print("-" * 20)
        print()

if __name__ == '__main__':
    main()
