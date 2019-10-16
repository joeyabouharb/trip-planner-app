from flask import request, render_template, Blueprint, g, redirect

from flask_server.services.cache_class import Cache
from flask_server.services.data_service import trip_journeys_generator, stop_information_generator

TRIP_BLUEPRINT = Blueprint('trips', __name__, url_prefix='/trip')


@TRIP_BLUEPRINT.before_request
def load_trips():
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

    dep = request.args.get('dep', 'dep')
    concession_type = request.args.get('concession_type', 'ADULT')

    if not origin:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    if not destination:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[],
        )

    trips = g.client.find_trips_for_stop(
        (type_origin, origin), (type_dest, destination), dep
    )

    origin_name = g.client.find_stops_by_name(
        'any', origin
    )

    if g.client.error == 404:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    destination_name = g.client.find_stops_by_name('any', destination)

    if g.client.error == 404:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )
    origin = next(
        stop_information_generator(
            origin_name.locations, [], ''), False
    )
    if g.client.error == 404:
        return f"{g.client.error}"

    destination = next(
        stop_information_generator(
            destination_name.locations, [], ''), False
    )
    trips = trip_journeys_generator(trips.journeys, concession_type)
    return render_template(
        'journeys.jinja2', trips=trips,
        destination=destination, origin=origin,
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

        origins = g.client.find_stops_by_name('any', origin_stop, True)
        if g.client.error == 404:
            render_template(
                "trip-planner.jinja2", origins=[], destinations=[], err=404
            )

        destinations = g.client.find_stops_by_name('any', destination_stop, True)
        if g.client.error == 404:
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
    destination = request.form.get('destination', ''), request.form.get('destination_name', '')
    origin = request.form.get('origin', ''), request.form.get('origin_name', '')
    if '' not in destination or '' not in origin:
        g.trip_db.write_db((origin, destination))
    return redirect('/')


@TRIP_BLUEPRINT.teardown_request
def teardown_trips(_):
    g.pop('trips_db', None)
    print('hello?')
