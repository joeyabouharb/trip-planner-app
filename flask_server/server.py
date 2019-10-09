"""
Flask server app
Initialises Flask Server with routes to:
    - /stop-search
    - /trips
    - /departures
    - /trip-planner
"""

from os import environ
from operator import attrgetter
from dotenv import load_dotenv, find_dotenv
from flask import (
    Flask, render_template, request, redirect, Response
)
from flask_server.client_class import Client
from flask_server.services.app_locals import VALID_TRANSPORT, TRIPS_DB, DEPARTURE_DB
from flask_server.services.data_factory import (
    generator_departure_info, generator_stop_information, generator_trip_data
)
from flask_server.services.cache_class import Cache

load_dotenv(find_dotenv())

app = Flask(__name__)
TRIPS_CACHE = Cache(TRIPS_DB)
DEPARTURE_CACHE = Cache(DEPARTURE_DB)
TRIP_API_KEY = environ.get('TRIP_PLANNER_API_KEY', False)
if not TRIP_API_KEY:
    try:
        app.config.from_envvar('CONFIG')
        TRIP_API_KEY = app.config.get('TRIP_PLANNER_API_KEY', False)
    except RuntimeError:
        exit('No .env or api key configured. closing')

CLIENT = Client(TRIP_API_KEY)


# get request to get status info? homepage extension
@app.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    TRIPS_CACHE.read_db()
    names = []
    for origin, dest in TRIPS_CACHE.data:
        origin_name = CLIENT.find_stops_by_name('stop', origin, is_id=True)
        origin_name = generator_stop_information(origin_name.locations, [], '')
        dest_name = CLIENT.find_stops_by_name('stop', dest, is_id=True)
        dest_name = generator_stop_information(dest_name.locations, [], '')
        names.append((next(origin_name), next(dest_name)))
    DEPARTURE_CACHE.read_db()
    stops = []
    for stop in DEPARTURE_CACHE.data:
        stops.append(stop)

    return render_template('index.jinja2', trips=names, stops=stops)


@app.route('/departures/<id_>')
def get_departures(id_: str):
    """
    get departures for a certain stop ID
    """
    date = request.args.get('date', '')
    time = request.args.get("time", '')
    if not date or not time:
        date_time = None
    else:
        date_time = (date, time)
    expected_type = request.args.get('expected_type', 'dep')
    departures = CLIENT.find_destinations_for(
        'any', id_, expected_type, date_time=date_time
    )

    departures_info = generator_departure_info(departures, date_time)\
        if departures.stop_events is not None else []
    sorted_departures = {}
    for departure in departures_info:
        location_key = sorted_departures.get(departure.location, False)
        if not location_key:
            sorted_departures[departure.location] = []
        sorted_departures[departure.location].append(departure)

    return render_template("departures.jinja2", departures_info=sorted_departures)


@app.route('/stops')
def get_stop_information():
    """
    :route: /stops
    returns a list of stops from entered key words
    :return:
    """
    date = request.args.get('date', '')
    time = request.args.get("time", '')
    req = request.args.get('query', False)
    stops = CLIENT.find_stops_by_name('any', req)
    is_suburb = bool(request.args.get('suburb', False))
    selections = [
        int(request.args.get(str(key), False))
        for key in VALID_TRANSPORT.keys() if int(request.args.get(str(key), False))
    ]

    locations = stops.locations
    data = (
        generator_stop_information(locations, selections, req, is_suburb)
        if req else []
    )  # return an empty list if no location was returned
    return render_template(
        'stops.jinja2', data=data, selected_type=selections,
        date=date, time=time
    )


@app.route('/trip/journeys')
def get_trip_info():
    """
    :route: /journeys
    returns a list of journeys for a specified trip
    :return:
    """
    type_origin, origin = (
        request.args.get('originType', 'any'),
        request.args.get('origin', '')
    )
    type_dest, destination = (
        request.args.get('destType', 'any'),
        request.args.get('dest', '')
    )

    dep = request.args.get('dep', 'dep')

    if not origin:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    if not destination:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[],
        )

    trips = CLIENT.find_trips_for_stop(
        (type_origin, origin), (type_dest, destination), dep
    )

    origin_name = CLIENT.find_stops_by_name(
        'stop', origin
    )

    if CLIENT.error == 404:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    destination_name = CLIENT.find_stops_by_name('stop', destination)

    if CLIENT.error == 404:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    origin_name = next(
        generator_stop_information(
            origin_name.locations, [], ''), False
        )
    if CLIENT.error == 404:
        return f"{CLIENT.error}"

    destination_name = next(
        generator_stop_information(
            destination_name.locations, [], ''), False
    )
    return render_template(
        'journeys.jinja2', trips=list(generator_trip_data(trips.journeys)),
        destination=destination_name, origin=origin_name,
    )


@app.route('/trip/planner')
def plan_trip():
    """
    route for trip planning
    """
    origins = []
    destinations = []

    origin_stop = request.args.get('origin', False)
    destination_stop = request.args.get('destination', False)
    origin_is_suburb = request.args.get('origin_suburb', False)
    dest_is_suburb = request.args.get('dest_suburb', False)

    origin_is_suburb = bool(origin_is_suburb)
    dest_is_suburb = bool(dest_is_suburb)

    if origin_stop and destination_stop:

        origins = CLIENT.find_stops_by_name('any', origin_stop, True)
        if CLIENT.error == 404:
            render_template(
                "trip-planner.jinja2", origins=[], destinations=[], err=404
            )

        destinations = CLIENT.find_stops_by_name('any', destination_stop, True)
        if CLIENT.error == 404:
            render_template(
                "trip-planner.jinja2", origins=[], destinations=[], err=404
            )

        origins = generator_stop_information(
            origins.locations, [], origin_stop, origin_is_suburb
        )
        destinations = generator_stop_information(
            destinations.locations, [], destination_stop, dest_is_suburb
        )

    return render_template(
        "trip-planner.jinja2", origins=origins, destinations=destinations, err=200
    )

# one post request? save a trip?
@app.route('/trip/save', methods=['POST'])
def save_journey():
    """
    save a journey by name
    :return:
    """
    destination = request.form.get('destination', ''), request.form.get('destination_name', '')
    origin = request.form.get('origin', ''), request.form.get('origin_name', '')
    if '' not in destination or '' not in origin:
        TRIPS_CACHE.write_db((origin, destination))
    return redirect('/')


@app.route('/stops/save', methods=['POST'])
def save_stop():
    stop = request.form.get('stop', '')
    if stop:
        DEPARTURE_CACHE.write_db(stop)
    return redirect('/')


@app.errorhandler(404)
def not_found_error():
    return render_template('404.jinja2')


if __name__ == '__main__':
    app.run()
