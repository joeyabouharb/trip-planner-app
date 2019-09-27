from setuptools import setup, find_packages 

NAME = "trip_planner"
VERSION = "1.0.0"
DESCRIPTION = "Trip Planner for NSW Transport REST API"
EMAIL = ''
URL = ""
KEYWORDS = ["assessment 2",
    "Trip Planner", "flask restful api"]

LONG_DESC = """\
    This application handles communication between
    the NSW Trip Planner API in order to provide a
    way for the user to organise and set out their
    weekly commute on public transport.
    this application provides useful data aggregation,
    providing the ability for the user to calculate time
    of trips and the cost of fares over their week
    """

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author_email=EMAIL,
    url=URL,
    keywords=KEYWORDS,
    packages=find_packages(exclude='*.egg-info'),
    include_package_data=True,
    long_description=LONG_DESC
)