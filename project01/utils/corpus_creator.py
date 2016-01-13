from os import listdir
import os
from os.path import isfile, join
import pickle
from edit_extractor import Page, Revision

__author__ = 'wikipedia_project_group'


def read_pickles(input_dir, corpus_dir):
    train_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    country_id = 0

    countries_id_dic = {}

    for f in train_files:
        if "Talk:" in f:
            continue

        page = pickle.load(open(input_dir + f, 'rb'))
        for revision in page.revisions:
            country = revision.country

            if '\t' in country:
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


if __name__ == '__main__':
    read_pickles("../data/pickle/", "../data/countries/" )

