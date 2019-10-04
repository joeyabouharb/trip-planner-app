from setuptools import setup, find_packages

NAME = "trip_planner"
VERSION = "1.0.0"
DESCRIPTION = "Trip Planner for NSW Transport REST API"
EMAIL = ''
URL = ""
KEYWORDS = ["assessment 2",
            "Trip Planner", "flask restful api"]

INSTALL_REQUIRES = [
    "astroid",
    "certifi",
    "Click",
    "entrypoints",
    "Flask",
    "isort",
    "itsdangerous",
    "Jinja2",
    "lazy-object-proxy",
    "MarkupSafe",
    "mccabe",
    "pycodestyle",
    "pyflakes"
    "pylint"
    "python-dateutil"
    "six"
    "git+https://github.com/joeyabouharb/trip-planner-app.git@f349e18e32c64f5e1c1a57a0b83ec05f8e3c2fc3#egg=trip_planner",
    "typed-ast",
    "urllib3",
    "Werkzeug",
    "wrapt"
]

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
    long_description=LONG_DESC,
    install_requires=INSTALL_REQUIRES
)
