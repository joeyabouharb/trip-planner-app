"""# Flask Factory Method
Initialises Flask server with routes to:
    - /stops
    - /trips
    - /departures
    - /trip-planner
Also, configures our connection to the API by loading our keys in our environment
to be loaded during a request contexts
"""

from flask import Flask
from dotenv import load_dotenv, find_dotenv
from flask_server import client as api
from flask_server.routes.trips import TRIP_BLUEPRINT
from flask_server.routes.stops import STOP_BLUEPRINT
from flask_server.routes.index import INDEX_BLUEPRINT



def create_app():
    """
    Factory Method that configures our server / API connection
    to be used by a wsgi container, or for testing
    :return: returns app: Flask
    """
    app = Flask(__name__)
    load_dotenv(find_dotenv())
    trip_api_key = app.config.get('TRIP_PLANNER_API_KEY', False)
    print(trip_api_key)
    if not trip_api_key:
        try:
            #app.config.get('CONFIG')
            #app.config.get('TRIP_PLANNER_API_KEY')
            app.config.from_pyfile('config/default.py')
        except Exception:
            raise RuntimeError("No API key Configured")
    api.init_app(app)
    app.register_blueprint(STOP_BLUEPRINT)
    app.register_blueprint(TRIP_BLUEPRINT)
    app.register_blueprint(INDEX_BLUEPRINT)
    return app
