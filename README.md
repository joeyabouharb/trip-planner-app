# NSW Trip Planner
Spins a Flask HTTP Server that fetches Public transport infofrom the NSW OPEN DATA API (Using their swagger client configuration).

## Features



- Search for stops and return their departure info for a particular date as well as current statuses and track works affecting the stop
- Plan a trip from a given origin, destination as well as date, and save them to your dashboard to retrieve trip details anytime.

## Requirements

As listed in the requirements text file, this requires:

- Flask
- An API Key from the Open-Data Platform. Its free :smirk:
- datetime module with the dateutils extension
- auto-generated swagger client for API connectivity. This package is served on my github, with some changes which you can view here:
https://github.com/joeyabouharb/opendata-swagger.
- python-dotenv to load environmental variables
- (OPTIONAL) gunicorn as production WSGI Server

##### To Run

```bash
pip install -r requirements.txt (or pipenv install) # for pipenv users
# pip install -e . to install as a package
# with gunicorn as wsgi container
gunicorn flask_server.start:APP
# or
FLASK_APP=flask_server flask run --host 0.0.0.0          

```

