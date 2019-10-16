from flask import request, render_template, redirect, Blueprint, g

from flask_server.services.app_locals import VALID_TRANSPORT
from flask_server.services.cache_class import Cache
from flask_server.services.data_service import stop_information_generator, departure_info_generator, \
    status_info_generator

STOP_BLUEPRINT = Blueprint('stops', __name__, url_prefix='/stops')


@STOP_BLUEPRINT.before_request
def create_stop_db():
    g.stop_db = Cache('stops')


@STOP_BLUEPRINT.route('/departures/<id_>')
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
    departures = g.client.find_destinations_for(
        'any', id_, expected_type, date_time=date_time
    )

    departures_info = departure_info_generator(departures, date_time) \
        if departures.stop_events is not None else []
    sorted_departures = {}
    for departure in departures_info:
        location_key = sorted_departures.get(departure.location, False)
        if not location_key:
            sorted_departures[departure.location] = []
        sorted_departures[departure.location].append(departure)
    return render_template(
        "departures.jinja2", departures_info=sorted_departures, id=id_
    )


@STOP_BLUEPRINT.route('/status/<id_>')
def get_status_info(id_):
    """
    get status info from ID
    :param id_:
    :return: View
    """
    statuses = g.client.request_status_info(id_).infos.current
    statuses = status_info_generator(statuses)
    return render_template('statuses.jinja2', statuses=statuses)


@STOP_BLUEPRINT.route('/save', methods=['POST'])
def save_stop():
    stop = request.form.get('id', '')
    if stop:
        g.stop_db.write_db(stop)
    return redirect('/')


@STOP_BLUEPRINT.route('')
def get_stop_information():
    """
    :route: /stops
    returns a list of stops from entered key words
    :return:
    """
    date = request.args.get('date', '')
    time = request.args.get("time", '')
    req = request.args.get('query', False)
    stops = g.client.find_stops_by_name('any', req)
    is_suburb = bool(request.args.get('suburb', False))
    selections = [
        int(request.args.get(str(key), False))
        for key in VALID_TRANSPORT.keys() if int(request.args.get(str(key), False))
    ]

    locations = stops.locations
    data = (
        stop_information_generator(locations, selections, req, is_suburb)
        if req else []
    )  # return an empty list if no location was returned
    return render_template(
        'stops.jinja2', data=data, selected_type=selections,
        date=date, time=time
    )


@STOP_BLUEPRINT.teardown_request
def teardown_stops_db(_):
    g.pop('stop_db', None)
