"""
Flask server app
Initialises Flask server with routes to:
    - /stops
    - /trips
    - /departures
    - /trip-planner
"""

from os import environ
import sys
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, g
from flask_server.client_class import Client
from flask_server.routes.stops import STOP_BLUEPRINT
from flask_server.routes.trips import TRIP_BLUEPRINT
from flask_server.routes.index import INDEX_BLUEPRINT


load_dotenv(find_dotenv())

APP = Flask(__name__)


@APP.before_request
def create_client_service():
    """
    load up and create our client service during each request context
    """
    trip_api_key = environ.get('TRIP_PLANNER_API_KEY', False)
    if not trip_api_key:
        try:
            APP.config.from_envvar('CONFIG')
            trip_api_key = APP.config.get('TRIP_PLANNER_API_KEY', False)
        except RuntimeError:
            sys.exit('No .env or api key configured. closing')
    g.client = Client(trip_api_key)


# trips/ route
APP.register_blueprint(TRIP_BLUEPRINT)
# /stop/ route
APP.register_blueprint(STOP_BLUEPRINT)
# / route
APP.register_blueprint(INDEX_BLUEPRINT)


@APP.errorhandler(404)
def not_found_error(_):
    """
    404 error handler page
    """
    return render_template('404.jinja2'), 404


@APP.teardown_appcontext
def destroy_client(_):
    """
    destroy client object after request is handled
    """
    g.pop('client')


if __name__ == '__main__':
    APP.run()
