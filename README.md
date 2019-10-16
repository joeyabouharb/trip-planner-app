# NSW Trip Planner
Spins a Flask HTTP Server that fetches Public transport infofrom the NSW OPEN DATA API (Using their swagger client configuration).

## Features



- Search for stops and return their departure info for a particular date as well as current statuses and track works affecting the stop
- Plan a trip from a given origin, destination as well as date, and save them to your dashboard to retrieve trip details anytime.

## Requirements

As listed in the requirements text file, this requires:

- Flask
- datetime module with the dateutils extension
- auto-generated swagger client for API.  RECOMMENDED :this package served at my github, since my application relies on some modifications: https://github.com/joeyabouharb/opendata-swagger.
- python-dotenv to load environmental variables
- (OPTIONAL) gunicorn as production WSGI Server

##### To Run

```bash
pip install -r requirements.txt (or pipenv install) # for pipenv users
pip install -e .
# with gunicorn
gunicorn flask_server:server.APP
# or
FLASK_APP=flask_server/server.py flask run --host 0.0.0.0          

```

