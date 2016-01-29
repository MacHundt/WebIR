# coding: utf-8
"""
The file used for evaluation of our writing style analyser
"""

import pickle
import os.path
import matplotlib.pylab as pl
from sklearn.metrics import confusion_matrix

from edit_extractor import Page, Revision
from writing_style_analyzer import predict_geo_location

__author__ = 'wikipedia_project_group'


def main():
    count = 0
    true_positive_count = 0
    country_occurrences = {}

    test = []
    prediction = []
    test_country_list = []

    for file_name in os.listdir("../data/test_pickles"):
        if file_name == '.DS_Store':
            continue

        if os.path.isdir("../data/test_pickles" + "/" + file_name):
            continue

        test_country_list.append(file_name)
        page = pickle.load(open("../data/test_pickles/" + file_name, 'rb'))

        # Iterate over all revisions, predict the geo-location and count the positive occurrences
        for revision in page.revisions:
            test_content = revision.diff_content
            predicted_geo_location = predict_geo_location(test_content)

            test.append(revision.country)
            prediction.append(predicted_geo_location)

            local_true_positive_count = 0
            if predicted_geo_location == revision.country:
                true_positive_count += 1
                local_true_positive_count = 1

            # Also count the occurrences for each geo-location
            if predicted_geo_location in country_occurrences:
                country_occurrences[predicted_geo_location] = [country_occurrences[predicted_geo_location][0] + 1,
                                                               country_occurrences[predicted_geo_location][1] +
                                                               local_true_positive_count]
            else:
                country_occurrences[predicted_geo_location] = [1, local_true_positive_count]

            count += 1
        print("Processed: " + page.title)

    print()
    print(12 * '-' + " Result " + 12 * '-')
    print()
    print("Countries with [Positive Count, True Positive Count]")
    print()

    for country, amount in country_occurrences.items():
        print(country + ': ' + str(amount))

    print()
    print("Count Revisions: " + str(count))
    print("True positive count: {0}".format(str(true_positive_count)))
    print("Accuracy: %.4f" % ((true_positive_count / count) * 100) + '%')

    cm = confusion_matrix(test, prediction, test_country_list)

    pl.matshow(cm)
    pl.title("Confusion Matrix")
    pl.colorbar()
    pl.ylabel('True label')
    pl.xlabel('Predicted label \n\n'+str(test_country_list))
    pl.show()

if __name__ == '__main__':
    main()
