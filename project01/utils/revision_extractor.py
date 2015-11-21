__author__ = 'wikipedia_project_group'

from geolocator import retrieve_geo_location as get_geo
import re

path_to_dump = "/Users/michaelhundt/Desktop/enwiki-20151102-pages-meta-history1"

revision_text = ""
start_revision = False
stop_revision = True
has_ip = False
is_text = False


def main():
    """ a main function for testing    """

    global revision_text, start_revision, stop_revision, has_ip, is_text

    ip_counter = 0
    text_tag = ""
    with open("learning_data.xml", 'a') as write_file:
        xml_header = '<?xml version="1.0" encoding="UTF-8"?>'+"\n"
        write_file.write(xml_header)
        with open(path_to_dump) as fp:
            for line in fp:

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
                        has_ip = True
                        ip_counter += 1
                        revision_text += line
                        ip_last = line.split("<ip>")[1]
                        ip = ip_last[:ip_last.find("<")]
                        country = get_country_tag(ip)
                        if country is not None:
                            revision_text += "\t\t"+ country+ "\n"
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
                            revision_text += "\t\t</content>\n\t</revision>"
                            print(revision_text)
                            write_file.write(revision_text)

                        reset()


        print(ip_counter)


def get_country_tag(ip):

    geo_location = get_geo(ip)
    if geo_location is not "None":
        return "<country>{0}</country>".format(str(geo_location.country.name))
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
    global revision_text, start_revision, stop_revision, has_ip, is_text
    revision_text = ""
    start_revision = False
    stop_revision = True
    has_ip = False
    is_text = False


if __name__ == '__main__':
    main()