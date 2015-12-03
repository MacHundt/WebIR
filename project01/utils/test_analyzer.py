# coding: utf-8
"""
The file used for evaluation of our writing style analyser
"""

import pickle
import os.path
from edit_extractor import Page, Revision
from writing_style_analyzer import WritingStyleProcessor, WritingStyleLearner,WritingStylePredictor

__author__ = 'wikipedia_project_group'



def main():
    processor = pickle.load(open("../data/trained_processor", 'rb'))
    counter = 0
    true_positive_counter = 0
    for file_name in os.listdir("../data/test_pages"):
        page = pickle.load(open("../data/test_pages/" + file_name, 'rb'))
        print(page.title)
        for revision in page.revisions:
            test_content = revision.diff_content
            probabilities, predicted_geo_location = processor.predict_text(test_content)

            if predicted_geo_location == revision.country:
                true_positive_counter +=1

            counter += 1

    print("*************** Result *************")
    print("Count Geolocations: " + str(len(processor.writing_style_learner.geo_located_writing_styles)))
    print("Precision: {0}".format(str(true_positive_counter / counter)))

if __name__ == '__main__':
    main()