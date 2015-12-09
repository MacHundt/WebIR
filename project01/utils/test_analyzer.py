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
    country_occurrences = {}

    for file_name in os.listdir("../data/test_pages"):
        if file_name == '.DS_Store':
            continue

        page = pickle.load(open("../data/test_pages/" + file_name, 'rb'))

        # Iterate over all revisions, predict the geo-location and count the positive occurrences
        for revision in page.revisions:
            test_content = revision.diff_content
            probabilities, predicted_geo_location = processor.predict_text(test_content)

            if predicted_geo_location == revision.country:
                true_positive_count += 1

            # Also count the occurrences for each geo-location
            if predicted_geo_location in country_occurrences:
                country_occurrences[predicted_geo_location] += 1
            else:
                country_occurrences[predicted_geo_location] = 1

            count += 1
        print("Processed: " + page.title)

    gl_writing_styles = processor.get_geo_located_writing_styles()
    country_deviations = {}

    # Create standard values for the country-deviations
    for key, value in country_occurrences.items():
        country_deviations[key] = 'No entry in training-set found.'

    # Look how much the predicted geo-locations deviate from the training-set
    for key, value in country_occurrences.items():
        for gl_writing_style in gl_writing_styles:
            if gl_writing_style.geo_location == key:
                country_deviations[key] = "%.2f" % (((value / gl_writing_style.count) * 100) - 100) + '%'
                continue

    print()
    print(12 * '-' + " Deviation from expected results " + 12 * '-')
    print()

    # Print the country-deviations
    for key, value in country_deviations.items():
        print(key + ': ' + value)

    print()
    print(12 * '-' + " Result " + 12 * '-')
    print()
    print("Count Geo-locations: " + str(len(processor.get_geo_located_writing_styles())))
    print("Count Revisions: " + str(count))
    print()
    print("True positive count: {0}".format(str(true_positive_count)))
    print("Precision: {0}".format(str(true_positive_count / count)))
    print("Precision compared with randomness: {0}".format(
        str((true_positive_count / count) - (1 / len(processor.get_geo_located_writing_styles())))))

if __name__ == '__main__':
    main()
