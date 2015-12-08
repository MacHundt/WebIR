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

    count = 0
    true_positive_count = 0

    for file_name in os.listdir("../data/test_pages"):
        if file_name == '.DS_Store':
            continue

        page = pickle.load(open("../data/test_pages/" + file_name, 'rb'))

        for revision in page.revisions:
            test_content = revision.diff_content
            probabilities, predicted_geo_location = processor.predict_text(test_content)

            if predicted_geo_location == revision.country:
                true_positive_count += 1

            count += 1

        print("Processed: " + page.title)

    print()
    print(10 * '*' + " Result " + 10 * '*')
    print("Count Geo-locations: " + str(len(processor.get_geo_located_writing_styles())))
    print("Count Revisions: " + str(count))
    print()
    print("Precision: {0}".format(str(true_positive_count / count)))
    print("Precision compared with randomness: {0}".format(
        str((true_positive_count / count) - (1 / len(processor.get_geo_located_writing_styles())))))

if __name__ == '__main__':
    main()
