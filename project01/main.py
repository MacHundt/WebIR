# coding: utf-8
"""The main file of the project."""

from utils.geolocator import retrieve_geo_location

__author__ = 'wikipedia_project_group'


def main():
    """The main function of the project."""
    geo_location = retrieve_geo_location('80.220.78.90')

    if geo_location is not None:
        print("Country: " + geo_location.country.name + " - City: " + geo_location.city.name)
    else:
        print("The geo-location could not be determined.")

if __name__ == '__main__':
    main()
