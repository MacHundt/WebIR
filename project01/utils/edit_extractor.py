import os
import time

__author__ = 'wikipedia_project_group'

from geolocator import retrieve_geo_location as get_geo
from difflib import Differ
from html2text import html2text     # download with pip
import re
import pickle

path_to_dump = "/Users/michaelhundt/Desktop/enwiki-20151102-pages-meta-history1"
path_to_learning_data = "../data/xml/"
path_to_pickle_objects = "../data/pickle/"

override = True

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

text_pattern = re.compile('[a-z]')
number_pattern = re.compile('[0-9]+(th|st|nd|s|\'s)')
preprocess_pattern = re.compile('[^a-z.|/\\-]+')


def main():
    """ a main function for testing    """

    global revision_text, ip, country, start_revision, stop_revision, has_ip, is_text, \
        start_page, has_previous, MAX_DIFF_CHARS, path_to_learning_data

    ip_counter = 0
    page_counter = 0
    revision_id = 0

    script_start_time = time.time()

    with open(path_to_dump) as fp:

        for line in fp:

            if "<page>" in line:
                page_start_time = time.time()
                start_page = True
                has_previous = False    # revision history
                page_counter += 1
                revision_id = 0
                page = Page()

            if not start_page:
                continue

            if has_ip:
                if '<text xml' in line:
                    is_text = True
                    temp = line[line.find('>')+1:]
                    revision_text += normalize_text(temp)
                    continue


            if start_revision:
                if '<username>' in line:
                    reset()
                    continue

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

            if "</page>" in line:
                page_end_time = time.time()
                if len(page.revisions) > 1:
                    print("save page with title name")
                    start_page = False
                    has_previous = False
                    reset()
                    #page.write_to_XML_file(path_to_learning_data)
                    page.save_as_serialized_Object(path_to_pickle_objects)
                    print("running time for "+page.title+": "+str(round(page_end_time-page_start_time, 2))+" sec.\n")
                    continue


            if start_page:
                if "<title>" in line:
                    title_part = line.split("<title>")[1]
                    title = title_part[:title_part.find("<")]
                    title = re.sub('[/ ]',"_", title)
                    path_to_file = path_to_pickle_objects+title

                    if override and os.path.isfile(path_to_file):
                        print(title+" exists already")
                        start_page = False
                        has_previous = False
                        reset()
                        continue

                    page.add_title(title)


            if '<revision>' in line:
                stop_revision = False
                start_revision = True
                continue



            if is_text:
                revision_text += normalize_text(line)
                if '</text>' in line and len(revision_text) > MIN_CONTENT_SIZE:
                    # save revision
                    if has_ip:
                        revision_text = revision_text.replace("</text>","")
                        revision = Revision(revision_id, ip, country, revision_text)
                        revision_id += 1
                        page.add_revision(revision)

                        if has_previous:
                            # Calculate the DIFF
                            revision.diff(prev_revision)

                            if len(revision.diff_content) < MAX_DIFF_CHARS:
                                # override content, but remove the current revision
                                # because the change is too small
                                prev_revision.set_content(revision.content)
                                page.remove_revision(revision.rev_id)
                            else:
                                #print(revision.diff_content+"\n")
                                prev_revision = revision

                        else:
                            has_previous = True
                            #print("First revision")
                            #print(revision_text)
                            revision.set_diff_content(revision.content)
                            prev_revision = revision

                    reset()

        print(ip_counter)

    end_script_time = time.time()
    print("running time of script: "+str(round(end_script_time - script_start_time, 2)))



def get_country(ip):

    geo_location = get_geo(ip)
    if geo_location is not "None":
        return geo_location.country.name
    else:
        return None



def normalize_text(line):

    #empty line?
    if line is "\n":
        return ""

    # remove == and ===
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
    if "namespace" in line[:17]:
        return ""

    # convert html
    line = html2text(line)
    line = line.replace("<b>","")
    line = line.replace("</b>","")
    line = line.replace("<i>","")
    line = line.replace("</i>","")

    words = line.split()

    if len(words) < 2:
        return ""

    line = ""
    first = words[0]
    for word in words:
        if word is "\n":
            continue
        # remove url
        if "http:" in word or "www." in word:
            continue
        if number_pattern.match(word):
            line += word
            continue
        if not text_pattern.match(word.lower()):
            continue

        word = re.sub(preprocess_pattern, '', word.lower())

        if "-" in first[-1:]:
            if first is not word:
                line = line[:-1]
        first = word
        line += word+" "

    return line+"\n"


def reset():
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
        with open(path_to_XML+"{0}".format(self.title)+".xml", "w") as write_file:
            xml_header = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
            write_file.write(xml_header)
            output = "<pages>\n<page>\n\t<title>{0}</title>\n".format(self.title)
            write_file.write(output)
            for revision in self.revisions:
                write_file.write(revision.to_XML())

            write_file.write("</page>\n</pages>\n")


    def save_as_serialized_Object(self, path_to_pickle):
        pickle.dump(self, open(path_to_pickle+self.title, "wb"))



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


    def diff(self, prev_revision):
        '''
        This method calculates the diff_content to the input revision
        :param prev_revision: Class revision
        '''
        d = Differ()
        s1 = prev_revision.content
        s2 = self.content
        #print("calc Diff :)")
        diff = list(d.compare(s1.split(" "), s2.split(" ")))

        #print(s1)
        #print(s2)

        for line in diff:
            #print(line)
            if line[0] == "+":
                #print(line)
                temp = str(line).replace("\n","")
                temp = temp.replace("+ ","")
                temp = temp.replace("]","")
                #print(temp)
                self.diff_content += temp+" "

        self.diff_size = len(self.diff_content)

        #print(len("Diff_conten_length: "+self.diff_content))
        if not self.keep_content:
            prev_revision.content = None


if __name__ == '__main__':
    main()