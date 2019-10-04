"""
Flask server app
Initialises Flask Server with routes to:
    - /stop-search
    - /trips
    - /departures
    - /trip-planner
"""


from operator import attrgetter

from flask import (
    Flask, render_template, request
)
from flask_server.client_class import Client
from flask_server.services.app_locals import VALID_TRANSPORT
from flask_server.services.data_factory import (
    generator_departure_info, generator_stop_information, generator_trip_data
)

app = Flask(__name__)
CLIENT = Client()


# get request to get status info? homepage extension
@app.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    return render_template('index.jinja2', dashboard='data')


@app.route('/departures/<id_>')
def get_departures(id_: str):
    """
    get departures for a certain stop ID
    """

    transport_types = request.args.get('type', '').split(' ')

    departures = CLIENT.find_destinations_for(
        'any', id_, transport_types=transport_types
    )

    departures_info = list(generator_departure_info(departures))

    departures_info.sort(key=attrgetter('location'))
    return render_template("departures.jinja2", departures_info=departures_info)


@app.route('/stops')
def get_stop_information():
    """
    """

    req = request.args.get('query', False)
    stops = CLIENT.find_stops_by_name('any', req)
    is_suburb = bool(request.args.get('suburb', False))
    selections = [
        int(request.args.get(str(key), False))
        for key in VALID_TRANSPORT.keys() if int(request.args.get(str(key), False))
    ]
    valid_transports = list(VALID_TRANSPORT.values())
    locations = stops.locations

    data = generator_stop_information(locations, selections, req, is_suburb) if req else []

    return render_template(
        'stops.jinja2', data=data, selected_type=selections,
        type="+".join(valid_transports), valid_transports=VALID_TRANSPORT
    )


@app.route('/journeys')
def get_trip_info():
    """

    :return:
    """
    type_origin, origin = (
        request.args.get('originType', 'any'),
        request.args.get('origin', '')
    )
    type_dest, destination = request.args.get('destType', 'any'), request.args.get('dest', '')
    dep = request.args.get('dep', 'dep')

    if not origin:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )
    if not destination:
        return render_template(
            "trip-planner.jinja2", origins=[], destinations=[]
        )

    trips = CLIENT.find_trips_for_stop(
        (type_origin, origin), (type_dest, destination), dep
    )

    origin_name = CLIENT.find_stops_by_name(
        'stop', origin[1]
    )

    if CLIENT.error == 404:
        return f"{CLIENT.error}"

    destination_name = CLIENT.find_stops_by_name('stop', destination[1])

    if CLIENT.error == 404:
        return f"{CLIENT.error}"

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
        destination_name=destination_name, origin_name=origin_name
    )


@app.route('/trip-planner')
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


if __name__ == '__main__':
    app.run()
