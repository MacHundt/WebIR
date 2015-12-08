import math

__author__ = 'wikipedia_project_group'

from geolocator import retrieve_geo_location as get_geo
from difflib import Differ, SequenceMatcher
from html2text import html2text  # download with pip
import re
import pickle # download with pip
import os
import time

path_to_dump = "/Users/michaelhundt/Desktop/enwiki-20151102-pages-meta-history1"

path_to_learning_data = "../data/xml/"
path_to_pickle_objects = "../data/pickle/"

override = False

MIN_CONTENT_SIZE = 200      # in char
MAX_DIFF_CHARS = 100        # in char

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
preprocess_pattern = re.compile('[^a-z.?!:]+')          # all NOT text and sentence-end punctuations

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
        start_page, has_previous, MAX_DIFF_CHARS, path_to_learning_data

    ip_counter = 0
    page_counter = 0
    revision_id = 0

    script_start_time = time.time()
    # read through wiki dump
    with open(path_to_dump) as fp:
        for line in fp:
            ################ START create a new Page() ################
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
            if has_ip:
                if '<text xml' in line:
                    is_text = True
                    temp = line[line.find('>') + 1:]
                    revision_text += normalize_text(temp)
                    continue

            # cancel the revision
            if start_revision:
                if '<username>' in line:
                    reset()
                    continue

                # get the country from ip
                if '<ip>' in line:
                    global country
                    has_ip = True
                    ip_counter += 1
                    ip_last = line.split("<ip>")[1]
                    ip = ip_last[:ip_last.find("<")]
                    # cannot find a country
                    if get_country(ip) is not None:
                        country = get_country(ip)
                    else:
                        reset()
                        continue

            ################################# END of a page ##################################
            if "</page>" in line:
                page_end_time = time.time()
                ########## STORE the page and reset to continue ##########
                if len(page.revisions) > 1:
                    print('save page "' + page.title + '"')
                    start_page = False
                    has_previous = False
                    reset()
                    # page.write_to_XML_file(path_to_learning_data)
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
                revision_text += normalize_text(line)
                #############################  END of revision: ADD to page   #############################
                if '</text>' in line and len(revision_text) > MIN_CONTENT_SIZE:
                    if has_ip:
                        revision_text = revision_text.replace("</text>", "")
                        revision = Revision(revision_id, ip, country, revision_text)
                        revision_id += 1
                        page.add_revision(revision)
                        # revision, calculate diff_ratio --> calc diff
                        if has_previous:
                            diff_ratio = revision.gef_diff_ratio(prev_revision)
                            if diff_ratio <= 0.995:
                                revision.diff(prev_revision)
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

                    reset()


        print(ip_counter)
    end_script_time = time.time()
    print("running time of script: " + str(round(end_script_time - script_start_time, 2)))


def get_country(ip):
    """
    Get the country from the ip address using geolocator
    :param ip:
    :return:
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
    alphabet_set = set()
    for char in line:
        if len(alphabet_set) > max_diff_chars:
            return True
        if char not in alphabet_set:
            alphabet_set.add(char)
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
    # Irgnore lines with 'strange' start characters
    if "==" in line[:3]:
        return ""
    if "[[" in line[:4]:
        return ""
    if "*" in line[:2]:
        return ""
    if "''" in line[:2]:
        return ""
    if "#" in line[:2]:
        return ""
    if "{{" in line[:2]:
        return ""
    if "&l" in line[:2]:
        return ""
    if "---" in line[:5]:
        return ""
    if "...." in line[:5]:
        return ""
    if " | " in line[:4]:
        return ""

    # first 120 chars, 6 different ones
    if not variety_char_threshold(line[:120], 6):
        # print("<6: "+line)
        return ""
    # words in a sentence - heuristic: 30 words a average of 12 chars
    if len(line) > 360 and not re.search('[;:.!?]', line[:360]):
        # print("Sen_Fault: "+line)
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


    # remove all ::+
    line = re.sub('[:][:]+', " ", line, re.MULTILINE)

    line = line.replace("[[", "")
    line = line.replace("]]", "")
    line = line.replace("\\", "")
    line = line.replace("...", " ")

    words = line.split()
    # no whitespace in line, only one word, return
    if len(words) < 2:
        return ""
    output = ""
    first = words[0]
    for word in words:
        if word is "\n":
            continue
        # greater tnan "longest word in english"
        if len(word) > 45:
            continue
        if '/' in word or '\\' in word or '|' in word:
            continue
        # remove url
        if "http:" in word or "www." in word:
            continue
        if number_pattern.match(word):
            output += word
            continue
        word = word.replace("(", "")
        word = word.replace(")", "")
        word = word.replace('\n', ' ')
        # word.replace("ref","")

        word = re.sub(preprocess_pattern, '', word)
        # remove words with - in begining e.g.  -word
        if "-" in word[:1]:
            word = " " + word[1:]
        # concat words where first word has - at the end.
        if "-" in first[-1:]:
            if first is not word:
                output = output[:-1]
        first = word
        output += word + " "
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
        '''
        This method calculates the diff_content to the input revision
        :param prev_revision: Class revision
        '''
        d = Differ()
        s1 = prev_revision.content
        s2 = self.content
        return SequenceMatcher(lambda x: x == " ", s1, s2).quick_ratio()

    def diff(self, prev_revision):
        '''
        This method calculates the diff_content to the input revision
        :param prev_revision: Class revision
        '''
        d = Differ()
        s1 = prev_revision.content
        s2 = self.content

        # if diff text is too big, cut it into smaller chunks to avoid Errors

        if abs(len(s1) - len(s2)) > 3000:
            if len(s2) > 2000 and len(s1) > 1000:
                lastIndex = 0
                for i in range(math.ceil(len(s2) / 1000)):
                    s2_i_content = s2[lastIndex:(i + 1) * 1000]
                    s2_i_revsision = Revision(self.rev_id,
                                              self.ip,
                                              self.country,
                                              s2_i_content,
                                              keep_content=True)
                    s2_i_revsision.diff(prev_revision)
                    if self.diff_content:
                        self.diff_content = self.diff_content[:-1]
                    self.diff_content += s2_i_revsision.diff_content
                    self.diff_size += s2_i_revsision.diff_size
                    lastIndex = (i + 1) * 1000
                prev_revision.content = None
                return

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
