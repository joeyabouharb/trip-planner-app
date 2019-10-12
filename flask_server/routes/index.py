from flask import Blueprint, g, render_template
from flask_server.services.cache_class import Cache
from flask_server.services.data_factory import generator_stop_information, generate_status_info


INDEX_BLUEPRINT = Blueprint('index', __name__)


@INDEX_BLUEPRINT.before_request
def load_cache():
    g.trips_db = Cache('trips')
    g.stops_db = Cache('stops')


@INDEX_BLUEPRINT.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    trips_db = g.trips_db
    trips_db.read_db()
    stops = trips_db.data

    if g.client.error in [500, 404]:
        return render_template(
            'index.jinja2', trips=[], names=[],
            error="Connection to API Failed."
        ), 404

    stops_db = g.stops_db
    stops_db.read_db()
    saved_stops = stops_db.data
    statuses = []

    for stop in saved_stops:
        status = g.client.request_status_info(stop).infos.current

        status = generate_status_info(status)
  
        if status:
            statuses.append(status)

    return render_template('index.jinja2', trips=stops, statuses=statuses)


@INDEX_BLUEPRINT.teardown_request
def teardown_current_context(_):
    g.pop('stops_db', None)
    g.pop('trips_db', None)
