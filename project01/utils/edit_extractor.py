import operator
from queue import Queue
import threading
import math
from geolocator import retrieve_geo_location as get_geo
from difflib import Differ, SequenceMatcher
from html2text import html2text  # download with pip
import re
import pickle
import os
import time

__author__ = 'wikipedia_project_group'


path_to_dump = "../data/wiki_dump/enwiki-20151102-pages-meta-history1"
test = "../data/wiki_dump/test_page"

# USE TEST data
# path_to_dump = test

num_lines = 45000

# training data
path_to_xml_data = "../data/xml/"
path_to_pickle_objects = "../data/pickle/"

override = False
do_pickle = True
do_xml = False

MIN_CONTENT_SIZE = 400      # in char
MAX_DIFF_CHARS = 300        # in char

start_page = False
revision_text = ""
ip = ""
country = ""
start_revision = False
stop_revision = True
has_ip = False
is_text = False
has_previous = False

# create Automates for regex
text_pattern = re.compile('[a-z]')                      # match text only
number_pattern = re.compile('[0-9]+(th|st|nd|s|\'s)')   # match 21th, 2nd, 1st, 1990s, ect
preprocess_pattern = re.compile('[^a-z.\'?!:-]+')          # all NOT text or sentence-end punctuations

tagList = ["b", "em", "i", "small", "strong", "sub", "sup", "ins", "del", "mark", "strike", "u", "href", "ref"]
openTag = ["<{0}>".format(x) for x in tagList]
closedTag = ["</{0}>".format(x) for x in tagList]


def extract_edits():
    """
    The edit extractor uses a widipedia dump file to extract the edits of a page and maps them to a geo location.
    The diff-content to the previous edit is calculated and stored, if it is big enough.
    We only use edits with an ip address.
    """
    global revision_text, ip, country, start_revision, stop_revision, has_ip, is_text, \
        start_page, has_previous, MAX_DIFF_CHARS, path_to_xml_data, num_lines, test

    ip_counter = 0
    page_counter = 0
    revision_id = 0

    script_start_time = time.time()

    # test_file = open(test, "w")

    # read through wiki dump
    with open(path_to_dump) as fp:
        for line in fp:

            # # Create a test_data
            # test_file.write(line)
            # num_lines -= 1
            # if num_lines == 0:
            #     test_file.write("</text> \n  </revision> \n </page>")
            #     test_file.close()

            # START create a new Page()
            if "<page>" in line:
                page_start_time = time.time()
                start_page = True
                # revision history
                has_previous = False
                page_counter += 1
                revision_id = 0
                page = Page()

            # we start with a Page ..
            if not start_page:
                continue

            # store text after opening tag to revision text
            #if has_ip:                                                 ***
            if '<text xml' in line:
                is_text = True
                temp = line[line.find('>') + 1:]
                revision_text += normalize_text(temp)
                continue

            # cancel the revision
            if start_revision:
                global country
                if '<username>' in line:
                    country = line.replace("<username>", "")
                    country = country[0:country.find('<')]
                #     reset()
                #     continue

                # get the country from ip
                if '<ip>' in line:
                    has_ip = True
                    ip_counter += 1
                    ip_last = line.split("<ip>")[1]
                    ip = ip_last[:ip_last.find("<")]
                    # cannot find a country
                    if get_country(ip) is not None:
                        country = get_country(ip)
                    # else:
                    #     reset()
                    #     continue

            # END of a page
            if "</page>" in line:
                page_end_time = time.time()
                # STORE the page and reset to continue
                if len(page.revisions) > 1:
                    print('save page "' + page.title + '"')
                    start_page = False
                    has_previous = False
                    reset()
                    if do_xml:
                        page.write_to_XML_file(path_to_xml_data)
                    if do_pickle:
                        page.save_as_serialized_Object(path_to_pickle_objects)
                    print("running time for " + page.title + ": " + str(
                        round(page_end_time - page_start_time, 2)) + " sec.\n")
                    continue

            # only continue if the page doesn't exist already
            if start_page:

                if "<title>" in line:
                    title_part = line.split("<title>")[1]
                    title = title_part[:title_part.find("<")]
                    title = re.sub('[/ ]', "_", title)
                    path_to_file = path_to_pickle_objects + title
                    print('"' + title + '" ...', end='')

                    if not override and os.path.isfile(path_to_file):
                        print(" exists already")
                        start_page = False
                        has_previous = False
                        reset()
                        continue
                    print()
                    page.add_title(title)

            # start a new revision
            if '<revision>' in line:
                stop_revision = False
                start_revision = True
                continue

            # store text
            if is_text:

                if '</text>' in line:
                    line = line.replace("</text>", "")
                    stop_revision = True

                revision_text += normalize_text(line)
                # END of revision: ADD to page

                # if normalize says its faulty text, it will return empty strings
                if stop_revision:
                    if len(revision_text) > MIN_CONTENT_SIZE:
                        if has_ip:

                            revision = Revision(revision_id, ip, country, revision_text)
                            revision_id += 1
                            page.add_revision(revision)
                            # revision, calculate diff_ratio --> calc diff
                            if has_previous:
                                diff_ratio = revision.gef_diff_ratio(prev_revision)
                                if diff_ratio <= 0.995:
                                    revision.diff(prev_revision)

                                    # POST-Cleaning!
                                    diff_text = revision.diff_content
                                    # first 140 chars, 7 different ones
                                    if not variety_char_threshold(diff_text[:140], 6):
                                        # if len(diff_text) > 500:
                                        #     print("Post-Cleaning: Variety_char")
                                        #     print(diff_text)
                                        diff_text = ""

                                    # # heuristic: 30 words with average length of 12 chars - Then a sentence punctuation must occur
                                    # if len(diff_text) > 360 and not re.search('[;:.!?]', diff_text[:600]):
                                    #     if len(diff_text) > 500:
                                    #         print("Post-Cleaning: Sentence_Punctuation")
                                    #         print(diff_text)
                                    #     diff_text = ""

                                    if len(diff_text) > 2 and abnormal_word_frequency(diff_text, threshold=0.4, epsilon=0.2):
                                        # if len(diff_text) > 500:
                                        #     print("Post-Cleaning: Abnormal_Word_Freq")
                                        #     print(diff_text)
                                        diff_text = ""

                                    revision.set_diff_content(diff_text)


                                    # override content, but remove the current revision
                                    if len(revision.diff_content) < MAX_DIFF_CHARS:
                                        prev_revision.set_content(revision.content)
                                        page.remove_revision(revision.rev_id)
                                    else:
                                        prev_revision = revision

                                # override content, but remove the current revision
                                else:
                                    prev_revision.set_content(revision.content)
                                    page.remove_revision(revision.rev_id)
                            else:
                                has_previous = True
                                revision.set_diff_content(revision.content)
                                prev_revision = revision
                        # NO IP
                        else:
                            # Change content of previous revision to current content
                            if has_previous:
                                #print(country)     # the username or None
                                prev_revision.set_content(revision_text)

                        reset()
                    else:
                        reset()


        print(ip_counter)
    end_script_time = time.time()
    print("running time of script: " + str(round(end_script_time - script_start_time, 2)))


def get_country(ip):
    """
    Get the country from the ip address using geolocator
    :param ip: The actual ip-address
    :return: The geo-location
    """
    geo_location = get_geo(ip)
    if geo_location is not "None":
        return geo_location.country.name
    else:
        return None


def variety_char_threshold(line, max_diff_chars):
    """
    A helper class to measure the usefulness of a text line.
    If a whole line contains less than <max_diff> chars from the alphabet the function will return False.
    :param line: String
    :param max_diff_chars: int
    :return: True or False
    """
    global varTest
    alphabet_set = set()
    for char in line:
        if len(alphabet_set) > max_diff_chars:
            varTest = True
            return True
        if char not in alphabet_set:
            alphabet_set.add(char)
    varTest = False
    return False


def abnormal_word_frequency(line, threshold=0.25, topK=5, epsilon=0.15 ):
    """
    1) If the most frequent word occurs more than threshold
    2) Check for items_to_look_at (max: topK) if they occur against ZIPF's Law (with epsilon range)

    :param line: Text
    :param threshold: 0.25 default, tf / len(dictionary),
    :param topK: 3 default,
    :param epsilon: + 15% range
    :return: boolean, if abnormal
    """

    word_dic = {}
    word_count = 0
    for word in line.split():
        word_count += 1
        if word in word_dic.keys():
            word_dic[word] = word_dic[word] + 1
        else:
            word_dic[word] = 1

    word_dic = sorted(word_dic.items(), key=operator.itemgetter(1), reverse=True)
    top_score = word_dic[0][1]

    # if most frequent word occurs more often than threshold --> abnormal!
    if (round(top_score / word_count, 2) > threshold):
        # if len(line) > 500:
        #     print("Score: ", round(top_score / word_count, 2))
        #     print(word_dic)
        #     print(line)
        return True

    # check for items_to_look_at if they occur against ZIPF's Law (with epsilon range)
    items_to_look_at = int(min(topK, math.ceil(math.log(top_score)), 2))
    if len(word_dic) < items_to_look_at:
        print("Items to look at is < length of dictionary")   # --> abnormal!
        return True

    for i in range(1, items_to_look_at):
        zipf_score = round((top_score * (1/i)) / word_count, 2)      # should more or less be the frequency of the next tf
        score = round(word_dic[i][1] / word_count, 2)

        deviation = zipf_score * (1+epsilon) - score

        if deviation < 0:
            print("ZIPF - Score: ", round(top_score / word_count, 2))
            print(word_dic)
            print(line)
            return True

    return False



def normalize_text(line):
    """
    This method normalizes a given text.
    Newlines are removed.
    Markup is converted to html, tags are removed.
    Garbage and junk is filtered out (using some heuristics)
    :param line: String
    :return: void
    """
    # empty line
    if line is "\n":
        return ""

    # first 140 chars, 7 different ones
    if not variety_char_threshold(line[:140], 6):
        # print("<6: "+line)
        return ""

    # heuristic: 30 words with average length of 12 chars - Then a sentence punctuation must occur
    if len(line) > 360 and not re.search('[;:.!?]', line[:360]):
        # print("Sen_Fault: "+line)
        return ""

    if abnormal_word_frequency(line):
        return ""


    line = line.lower()
    if "align=" in line:
        return ""
    if "namespace" in line[:17]:
        return ""

    # convert html tags
    line = html2text(line)
    # remove tags
    for x in openTag:
        line = re.sub(str('{0}'.format(x)), "", line, re.MULTILINE)
    for x in closedTag:
        line = re.sub(str('{0}'.format(x)), "", line, re.MULTILINE)


    # remove all ::+ ignore \n
    line = re.sub('[:][:]+', " ", line, re.MULTILINE)
    line = re.sub('[\']+', "\'", line)
    line = line.replace("...", " ")

    line = line.replace("[[", "")
    line = line.replace("]]", "")
    line = line.replace("\\", "")

    words = line.split()
    # no whitespace in line, only one word, return
    if len(words) < 2:
        return ""

    output = ""
    first = words[0]
    for word in words:
        if word is "\n":
            continue

        # Keep the ' in a word . e.g don't
        if "\'" in word:
            if not re.match("[a-z]+[\'][a-z]+", word):
                # print(word, end=' -> ' )
                word = re.sub('[\']+', "", word)
                # print(word)
        # greater than "longest word in english"
        if len(word) > 45:
            continue
        if '/' in word or '\\' in word or '|' in word:
            continue
        # remove url
        if "http:" in word or "www." in word:
            continue

        if number_pattern.match(word):
            output += " "+word
            continue

        word = word.replace("(", "")
        word = word.replace(")", "")
        word = word.replace('\n', '')
        # word.replace("ref","")

        # now take all none text elements out
        word = re.sub(preprocess_pattern, '', word)

        # remove - in beginning e.g.  -word
        if "-" in word[:1]:
            word = word[1:]
        # concat words where first word has - at the end.
        if "-" in first[-1:]:
            if first is not word:
                output = output[:-1]
        first = word
        output += " "+word

    # some abnormal mistake, remove manual
    if "ref " in output:
        output = output.replace("ref ", " ")

    return output + "\n"


def reset():
    """
    The methods resets al the variables
    :return: void
    """
    global revision_text, start_revision, stop_revision, has_ip, is_text, country, ip
    revision_text = ""
    country = ""
    ip = ""
    start_revision = False
    stop_revision = True
    has_ip = False
    is_text = False


class Page:
    """
    This class collects all revisions, where the diff is big enough
    """

    def __init__(self):
        '''
        :param title: String
        '''
        self.title = ""
        self.revisions = []

    def add_title(self, title):
        self.title = title

    def add_revision(self, revision):
        self.revisions.append(revision)

    def remove_revision(self, id):
        for rev in self.revisions:
            if rev.rev_id == id:
                self.revisions.remove(rev)
                break

    def to_XML(self):
        output = "<page>\n\t<title>{0}</title>\n".format(self.title)
        for revision in self.revisions:
            output += revision.to_XML()
        output += "</page>\n"
        return output

    def write_to_XML_file(self, path_to_XML):
        with open(path_to_XML + "{0}".format(self.title) + ".xml", "w") as write_file:
            xml_header = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
            write_file.write(xml_header)
            output = "<pages>\n<page>\n\t<title>{0}</title>\n".format(self.title)
            write_file.write(output)
            for revision in self.revisions:
                write_file.write(revision.to_XML())

            write_file.write("</page>\n</pages>\n")

    def save_as_serialized_Object(self, path_to_pickle):
        '''
        This method stores itself as pickle object to a given path folder
        :param path_to_pickle: String
        :return: void
        '''
        pickle.dump(self, open(path_to_pickle + self.title, "wb"))


class Revision:
    """
    This class stores the diff content of a revision, which has an ip-address:
    <revID>, <ip>, <country>, <diff_content>
    When diff() was executed the
    """

    def __init__(self, id, ip, country, content, keep_content=False):
        '''
        :param id: Int
        :param ip: String
        :param country: String
        :param content: String
        :param keep_content: Boolean  keep after diff() was calculated
        '''
        self.rev_id = id
        self.ip = ip
        self.country = country
        self.content = content
        self.diff_content = ""
        self.keep_content = keep_content
        self.diff_size = 0

    def to_XML(self):
        output = "\t<revision>\n"
        output = "\t<revID>{0}</revID>\n".format(self.rev_id)
        output += "\t\t<ip>{0}</ip>\n".format(self.ip)
        output += "\t\t<country>{0}</country>\n".format(self.country)
        output += "\t\t<diff_content>{0}\t\t</diff_content>\n".format(self.diff_content)
        output += "\t</revision>\n"
        return output

    def set_content(self, content):
        self.content = content

    def set_diff_content(self, diff):
        self.diff_content = diff

    def gef_diff_ratio(self, prev_revision):
        """
        This method calculates the diff_content to the input revision
        :param prev_revision: Class revision
        """
        d = Differ()

        s1 = prev_revision.content
        s2 = self.content
        return SequenceMatcher(lambda x: x == " ", s1, s2).quick_ratio()

    def diff(self, prev_revision):
        """
        This method calculates the diff_content to the input revision
        :param prev_revision: Class revision
        """
        d = Differ()
        s1 = prev_revision.content
        s2 = self.content

        # if diff text is too big, cut it into smaller chunks to avoid Errors --> brought errors :(

        # if abs(len(s1) - len(s2)) > 3000:
        #     if len(s2) > 2000 and len(s1) > 1000:
        #         last_index = 0
        #
        #         for i in range(math.ceil(len(s2) / 1000)):
        #             s2_i_content = s2[last_index:(i + 1) * 1000]
        #             s2_i_revsision = Revision(self.rev_id,
        #                                       self.ip,
        #                                       self.country,
        #                                       s2_i_content,
        #                                       keep_content=True)
        #             s2_i_revsision.diff(prev_revision)
        #             if self.diff_content:
        #                 self.diff_content = self.diff_content[:-1]
        #             self.diff_content += s2_i_revsision.diff_content
        #             self.diff_size += s2_i_revsision.diff_size
        #             last_index = (i + 1) * 1000
        #         prev_revision.content = None
        #         return

        diff = list(d.compare(s1.split(" "), s2.split(" ")))

        for line in diff:
            # print(line)
            if line[0] == "+":
                # print(line)
                temp = str(line).replace("\n", "")
                temp = temp.replace("+ ", "")
                temp = temp.replace("]", "")
                # print(temp)
                self.diff_content += temp + " "

        self.diff_size = len(self.diff_content)

        if not self.keep_content:
            prev_revision.content = None

if __name__ == '__main__':
    extract_edits()
