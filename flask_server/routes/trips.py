"""
/trips route
"""
from flask import request, render_template, Blueprint, g, redirect

from flask_server.client_class import Client
from flask_server.services.cache_class import Cache
from flask_server.services.data_service import trip_journeys_generator, stop_information_generator


TRIP_BLUEPRINT = Blueprint('trips', __name__, url_prefix='/trip')


@TRIP_BLUEPRINT.before_request
def load_trips():
    """
    instantiate trips cache
    :return:
    """
    g.trip_db = Cache('trips')


@TRIP_BLUEPRINT.route('/journeys')
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
    page = int(request.args.get('page', '1')) - 1
    dep = request.args.get('dep', 'dep')  # enable user to query departure or arrival times
    date = request.args.get('date', '')
    time = request.args.get('time', '')
    concession_type = request.args.get('concession_type', 'ADULT')

    client: Client = g.client
    if not date or not time:
        trips = client.find_trips_for_stop(
            (type_origin, origin), (type_dest, destination), dep
        )
    else:
        trips = client.find_trips_for_stop(
            (type_origin, origin), (type_dest, destination), dep, date_time=(date, time)
        )
        print(date, time)
        print(trips)
    if client.error == 404:
        return render_template("404.jinja2"), 404

    trips = list(trip_journeys_generator(trips.journeys, concession_type))

    return render_template(
        'journeys.jinja2', trip=trips[page], pages=len(trips), page_no=page,
        destination=destination, origin=origin, concession_type=concession_type
    )


@TRIP_BLUEPRINT.route('/planner')
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
        client: Client = g.client
        origins = client.find_stops_by_name('any', origin_stop, True)

        if client.error == 404:
            render_template(
                "trip-planner.jinja2", origins=[], destinations=[], err=404
            )

        destinations = client.find_stops_by_name('any', destination_stop, True)
        if client.error == 404:
            render_template(
                "trip-planner.jinja2", origins=[], destinations=[], err=404
            )

        origins = stop_information_generator(
            origins.locations, [], origin_stop, origin_is_suburb
        )
        destinations = stop_information_generator(
            destinations.locations, [], destination_stop, dest_is_suburb
        )

    return render_template(
        "trip-planner.jinja2", origins=origins, destinations=destinations, err=200
    )

# one post request? save a trip?
@TRIP_BLUEPRINT.route('/save', methods=['POST'])
def save_journey():
    """
    save a journey by name
    :return:
    """
    destination = request.form.get('destination_id', ''), request.form.get('destination_name', '')
    origin = request.form.get('origin_id', ''), request.form.get('origin_name', '')
    if '' not in destination or '' not in origin:
        trip_db: Cache = g.trip_db
        trip_db.read_db()
        trip_db.write_db((origin, destination))
        print(trip_db.data)
    return redirect('/')


@TRIP_BLUEPRINT.teardown_request
def teardown_trips(_):
    """
    remove trips database instance after request completion
    :param _:
    :return:
    """
    g.pop('trips_db', None)
