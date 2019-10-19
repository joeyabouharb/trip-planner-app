"""
Index / Home Page
"""
from flask import Blueprint, g, render_template

from flask_server.services.cache_class import Cache

INDEX_BLUEPRINT = Blueprint('index', __name__)


@INDEX_BLUEPRINT.before_request
def load_cache():
    """
    load up cache trips cache
    :return:
    """
    g.trips_db = Cache('trips')


@INDEX_BLUEPRINT.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    trips_db = g.trips_db
    trips_db.read_db()

    if g.client.error in [500, 404]:
        return render_template(
            'index.jinja2', trips=[], names=[],
            error="Connection to API Failed."
        ), 404

    return render_template('index.jinja2', trips=trips_db.data)


@INDEX_BLUEPRINT.teardown_request
def teardown_current_context(_):
    """
    delete cache instance after request completion
    :param _:
    :return:
    """
    g.pop('trips_db', None)
