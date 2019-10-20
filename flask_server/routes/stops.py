"""
/stops route
"""
from flask import request, render_template, redirect, Blueprint, g
from flask_server.services.app_locals import VALID_TRANSPORT
from flask_server.services.cache_class import Cache
from flask_server.services.data_service import (
    stop_information_generator, departure_info_generator,
    status_info_generator,
    validate_date_time)
from flask_server.client_class import Client

STOP_BLUEPRINT = Blueprint('stops', __name__, url_prefix='/stops')


@STOP_BLUEPRINT.before_request
def create_stop_db():
    """
    instantiate cache connection to stops.json (stub)
    :return:
    """
    g.stop_db = Cache('stops')


@STOP_BLUEPRINT.route('/departures/<id_>')
def get_departures(id_: str):
    """
    get departures for a certain stop ID
    """
    client: Client = g.client

    date = request.args.get('date', '')
    time = request.args.get("time", '')

    date_time = validate_date_time(date, time)

    expected_type = request.args.get('expected_type', 'dep')
    departures = client.find_destinations_for(
        'any', id_, expected_type, date_time=date_time
    )
    if client.error == 404:
        return render_template("404.jinja2")
    departures_info = departure_info_generator(departures, date_time)
    sorted_departures = {}
    for departure in departures_info:
        location_key = sorted_departures.get(departure.location, False)
        if not location_key:
            sorted_departures[departure.location] = []
        sorted_departures[departure.location].append(departure)
    name = client.find_stops_by_name('any', id_, is_id=True).locations[0].name

    return render_template(
        "departures.jinja2", departures_info=sorted_departures, id=id_, name=name,
        date_time=date_time
    )


@STOP_BLUEPRINT.route('/status/<id_>')
def get_status_info(id_):
    """
    get status info from ID
    :param id_:
    :return: View
    """
    client: Client = g.client
    statuses = client.request_status_info(id_).infos.current
    if client.error == 404:
        return render_template('statuses.jinja2', statuses=[])

    statuses = status_info_generator(statuses)
    return render_template('statuses.jinja2', statuses=statuses)


@STOP_BLUEPRINT.route('/save', methods=['POST'])
def save_stop():
    """
    save stop information into db
    :return:
    """
    stop_id, stop_name = request.form.get('id', ''), request.form.get('name', '')
    if stop_id and stop_name:
        g.stop_db.write_db((stop_id, stop_name))
    return redirect('/')


@STOP_BLUEPRINT.route('')
def get_stop_information():
    """
    :route: /stops
    returns a list of stops from entered key words
    :return:
    """
    client: Client = g.client

    date = request.args.get('date', '')
    time = request.args.get("time", '')
    req = request.args.get('query', '')
    stops = client.find_stops_by_name('any', req)

    if client.error == 404:
        return render_template(
            'stops.jinja2', data=[], selected_type=[],
            date=False, time=False
        ), 404

    is_suburb = bool(request.args.get('suburb', False))  # convert input to boolean
    selections = [
        int(request.args.get(str(key), False))
        for key in VALID_TRANSPORT if int(request.args.get(str(key), False))
    ]

    locations = stops.locations
    data = stop_information_generator(locations, selections, req, is_suburb)
    return render_template(
        'stops.jinja2', data=data, selected_type=selections,
        date=date, time=time
    )


@STOP_BLUEPRINT.teardown_request
def teardown_stops_db(_):
    """
    delete connection to db after request
    :param _: request context: usually NoneType
    :return:
    """
    g.pop('stop_db', None)
