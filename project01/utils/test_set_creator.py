from genericpath import getsize
from os import listdir
import os
from os.path import isfile, join
import pickle
import pandas as pd
import sys
from edit_extractor import Page, Revision

__author__ = 'wikipedia_project_group'

# append to existing files?
append = True


def read_pickles(input_dir, corpus_dir):
    """
    This methods read in test pickle files and creates a test corpus as csv file;
    Format:
        row:    id  \t  text content
    :param input_dir: Input directory
    :param corpus_dir: The directory of the corpus
    :return: csv files
    """
    train_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    country_id = 0

    countries_id_dic = {}

    # remove all corpus files, so that they will be created anew
    if not append:
        for file in os.path.isfile(corpus_dir):
            os.remove(corpus_dir+file)

    for f in train_files:
        if "Talk:" in f or ".DS_Store" in f:
            continue

        page = pickle.load(open(input_dir + f, 'rb'))
        for revision in page.revisions:
            country = revision.country

            # remove all usernames
            if "  " in country:
                continue

            if country not in countries_id_dic.keys():
                countries_id_dic[country] = country_id
                country_id += 1

            if country == "":
                continue

            # does file exists
            if os.path.isfile(corpus_dir+country):
                # append
                with open(corpus_dir+country, "a") as file:
                    file.write(str(countries_id_dic[country]) + '\t' + revision.diff_content + '\n')
            else:
                # create new
                with open(corpus_dir+country, "w") as file:
                    file.write("id\ttext\n")
                    file.write(str(countries_id_dic[country]) + '\t' + revision.diff_content + '\n')


def create_test_pickles(corpus_dir, test_pickle_dir='../data/test_pickles/', chunksize=2000, nr_revisions=5):
    """
    This method read in test corpus csv files, and puts the all
    the text to a Page pickle. Countries with text smaller than filesize will be rejected,
    the rest will be trimmed to the same filesize.
    :param corpus_dir:          directory to csv corpus
    :param test_pickle_dir:     path to store the test pages
    :param chunksize:           chunk size, text for every revision
    :param nr_revisions:        number of revisions per country
    :return:                    pickle pages for every country
    """
    country_ids = 0
    for file_name in os.listdir(corpus_dir):
        if file_name == '.DS_Store':
            continue

        size_of_file = getsize(corpus_dir+file_name)
        if size_of_file < chunksize:
            continue

        page = Page()
        page.add_title(file_name)
        print("Process: "+file_name)

        df = pd.read_csv(corpus_dir+file_name, sep="\t", dtype={'id': object, 'text': object})
        # id of the first row
        country_ids += 1

        i = 0
        rev = None
        for row in df['text']:
            if i >= nr_revisions:
                break
            rev = Revision(id, p_ip="", p_country=file_name, content="")
            test_content = ""
            if type(row) is str and sys.getsizeof(page) < chunksize:
                for word in row.split():
                    test_content += word+" "

                    if sys.getsizeof(test_content) > chunksize:
                        rev.set_diff_content(test_content)
                        page.add_revision(rev)
                        i += 1
                        break

        if i >= nr_revisions:
            page.add_revision(rev)
            page.save_as_serialized_object(path_to_pickle=test_pickle_dir)


if __name__ == '__main__':
    # read_pickles("../data/pickle/", "../data/countries/test/")
    create_test_pickles("../data/countries/test/")
