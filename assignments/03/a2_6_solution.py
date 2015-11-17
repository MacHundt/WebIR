# coding=utf-8


import logging
import re
import csv
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from a2_3_solution import open_url
import ex7 as ex7
from a2_3_solution import open_f


def parse_html(html):
    if html is not None:
        try:
            bs_obj = BeautifulSoup(html, "html.parser")
            return bs_obj
        except IOError as io_e:
            logging.error(io_e)
            return None
    else:
        return None


def get_hrefs(url, pattern='.*'):
    if url:
        pattern = re.compile(pattern)
        html = open_url(url)
        bs_obj = parse_html(html)
        if bs_obj is None:
            return None
        try:
            hrefs = bs_obj.findAll("a", href=pattern)
            return hrefs
        except AttributeError as att_e:
            logging.error(att_e)
            return None
    else:
        return None


def constr_url(root_url, page):
    url_p = urlparse(page)
    root_p = urlparse(root_url)
    # case 1: page is valid url: scheme, netloc, path
    if root_url in page:
        return page
    # case 2: page is a ressource (url routing) or a file, construct url
    else:
        new_url = [root_p.scheme,
                   "://",
                   root_p.netloc,
                   page, url_p.params,
                   url_p.query,
                   url_p.fragment]
        return "".join(new_url)


def traverse_domain(root,
                    regex,
                    max_depth,
                    url_func=constr_url,
                    export=True):
    pages = set()
    parents = [root]
    children = []
    depth = 0
    site_map = []
    while parents:
        if export:
            site_map.append(parents)
        if depth <= max_depth:
            children = []
        else:
            if export:
                return site_map
            break
        for link in parents:
            children += get_hrefs(link, regex)
        parents = []
        for href in children:
            if "href" in href.attrs:
                if href.attrs["href"] not in pages:
                    new_page = href.attrs["href"]
                    pages.add(new_page)
                    new_url = url_func(root, new_page)
                    parents.append(new_url)
        depth += 1


def export_csv(site_map):
    csv_file = open_f("site_map.csv", "w")
    try:
        writer = csv.writer(csv_file)
        writer.writerow(("LEVEL", "URL"))
    except IOError as e:
        logging.error(e)
    if writer is not None:
        for level in range(len(site_map)):
            for site in site_map[level]:
                try:
                    writer.writerow((level, site))
                except IOError as e:
                    logging.error(e)
        csv_file.close()



def main():
    ex7.init_log()
    url = "https://de.wikipedia.org"
    pattern = "^(/wiki/)"

    site_map = traverse_domain(url, pattern, 1)
    export_csv(site_map)
    ex7.shutdown_log()


if __name__ == '__main__':
    main()
