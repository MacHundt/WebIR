# coding=utf-8


from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import logging
import csv


def open_url(url):
    try:
        html = urlopen(url)
        doc = html.read()
        html.close()
        return doc
    except HTTPError as http_e:
        logging.error("%s while connecting to: %s", http_e, url)
        return None
    except URLError as url_e:
        logging.error("%s while connecting to: %s", url_e, url)
    except UnicodeEncodeError as unic_e:
        logging.error("%s while connecting to: %s", unic_e)
        return None


def download_file(url, path):
    doc = open_url(url)
    f = open_f(path, "w")
    if f is not None:
        doc = doc.decode("utf-8", "ignore")
        f.write(doc)
        close_f(f)
        return True
    else:
        return False


def open_f(path, mode):
    try:
        fp = open(path, mode)
        return fp
    except IOError as io_e:
        logging.error(io_e)
        return None


def close_f(fp):
    if fp is not None:
        fp.close()
        return True
    else:
        return False


def main():
    url = "https://ia802707.us.archive.org/1/items/macbeth02264gut/0ws3410.txt"
    path = "MacBeth.txt"
    download_file(url, path)


if __name__ == '__main__':
    main()
