# coding: utf-8
"""
The file used for the geo-locations.
Uses geoip2 (to install: 'pip install geoip2')
"""

import geoip2.database
import os

__author__ = 'wikipedia_project_group'

reader = geoip2.database.Reader(os.path.abspath("../data/GeoLite2-City.mmdb"))


def retrieve_geo_location(ip_address):
    """
    Retrieves the geo-location for a given ip-address.
    :param ip_address: The ip-address
    :return: The geo-location
    """
    global reader
    try:
        return reader.city(ip_address)
    except Exception as e:
        return "None"
