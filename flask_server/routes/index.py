"""
Index / Home Page
"""
from flask import Blueprint, g, render_template

from flask_server import CLIENT
from flask_server.services.cache_class import Cache

INDEX_BLUEPRINT = Blueprint('index', __name__)


@INDEX_BLUEPRINT.before_request
def load_cache():
    """
    load up cache trips cache
    :return:
    """
    g.trips_db = Cache('trips')
    g.stops_db = Cache('stops')


@INDEX_BLUEPRINT.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    trips_db: Cache = g.trips_db
    stops_db: Cache = g.stops_db
    client = CLIENT.connection

    trips_db.read_db()
    stops_db.read_db()
    if client.error == 404:
        return render_template(
            'index.jinja2', trips=[], names=[],
            error="Connection to API Failed."
        ), 404

    return render_template(
        'index.jinja2',
        trips=trips_db.data[trips_db.key],
        stops=stops_db.data[stops_db.key]
    )


@INDEX_BLUEPRINT.teardown_request
def teardown_current_context(_):
    """
    delete cache instance after request completion
    :param _:
    :return:
    """
    g.pop('trips_db', None)
