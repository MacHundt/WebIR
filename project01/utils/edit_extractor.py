__author__ = 'wikipedia_project_group'

from geolocator import retrieve_geo_location as get_geo
import os.path
from difflib import Differ

path_to_dump = "/Users/michaelhundt/Desktop/enwiki-20151102-pages-meta-history1"

start_page = False
revision_text = ""
start_revision = False
stop_revision = True
has_ip = False
is_text = False
country = ""



def main():
    """ a main function for testing    """

    global revision_text, start_revision, stop_revision, has_ip, is_text

    ip_counter = 0
    page_counter = 0

    with open(path_to_dump) as fp:

        for line in fp:

            if "<page>" in line:
                start_page = True
                page_counter += 1
                page = Page()

            if start_page:
                if "<title>" in line:
                    title = line.split("")


            if has_ip:
                if '<text xml' in line:
                    is_text = True
                    revision_text += "\t\t<content>"
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
                    revision_text += line
                    ip_last = line.split("<ip>")[1]
                    ip = ip_last[:ip_last.find("<")]
                    country = get_country(ip)
                    if country is not None:
                        revision_text += "\t\t" + "<country>{0}</country>".format(country) + "\n"
                    else:
                        reset()
                        continue

            if '<revision>' in line:
                revision_text += line
                stop_revision = False
                start_revision = True

            if is_text:
                revision_text += normalize_text(line)
                if '</text>' in line and len(revision_text) > 200:

                    # save text
                    if has_ip:
                        revision_text = revision_text.replace("</text>","")
                        revision_text += "\t\t</content>\n\t</revision>\n"
                        #print(revision_text)
                        path_to_learning_file = "../data/Countries/learning_data_{0}.xml".format(country)
                        if not os.path.isfile(path_to_learning_file):
                            with open(path_to_learning_file, 'a') as write_file:
                                xml_header = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
                                write_file.write(xml_header)
                                write_file.write(revision_text)
                        else:
                            with open(path_to_learning_file, 'a') as write_file:
                                write_file.write(revision_text)

                    reset()


        print(ip_counter)


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

    line = line.replace("[[","")
    line = line.replace("]]","")


    return line


def reset():
    global revision_text, start_revision, stop_revision, has_ip, is_text, country
    revision_text = ""
    start_revision = False
    stop_revision = True
    has_ip = False
    is_text = False
    country = ""


class Page:
    """
    This class collects all revisions, where the diff is big enough
    """

    def __init__(self, title):
        '''
        :param title: String
        '''
        self.title = ""
        self.revisions = []


    def add_title(self, title):
        self.title = title


    def add_revision(self, revision):
        self.revisions.append(revision)


    def to_XML(self):
        output = "<page>\n\t<title>{0}</title>\n".format(self.title)
        for revision in self.revisions:
            output += revision.to_XML()
        return output


class Revision:
    """
    This class stores the diff content of a revision, which has an ip-address:
    <ip>, <country>, <diff_content>
    """
    def __init__(self, ip, country, content):
        '''

        :param ip: String
        :param country: String
        :param content: String
        '''
        self.ip = ip
        self.country = country
        self.content = content
        self.diff_content = ""



    def to_XML(self):
        output = "\t<revision>\n"
        output += "\t\t<ip>{0}</ip>\n".format(self.ip)
        output += "\t\t<country>{0}</country>\n".format(self.country)
        output += "\t\t<content>{0}</content>\n".format(self.diff_content)
        output += "\t</revision>\n"
        return output


    def diff(self, revision):
        '''

        :param revision: Class revision
        :return:
        '''
        d = Differ()
        diff = list(d.compare(self.content, revision.content))
        #TODO go through list, just keep + and store in diff_content





if __name__ == '__main__':
    main()