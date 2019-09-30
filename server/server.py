from flask import Flask, render_template, request, Response, stream_with_context
from client.client_class import Client
from client.services.data_factory import generator_departure_info, generator_stop_information
from client.models.departure_info import DepartureInfo
from client.services.app_locals import VALID_EXCLUSIONS, VALID_TRANSPORT
from operator import attrgetter
app = Flask(__name__)
CLIENT = Client()
# get request to get status info? homepage extention
@app.route('/')
def home():
    """## Home Page Route
    Dashboard with sitemap
    """
    return render_template('index.html', dashboard='data')

@app.route('/departures/<id_>')
def get_departures(id_: str):
    """
    get departures for a certain stop ID
    """
    exclusions = {
    'exclMOT_1': '1', 'exclMOT_4': '1', 'exclMOT_5': '1',
    'exclMOT_7': '1', 'exclMOT_9': '1', 'exclMOT_11': '1'
    }
    transport_type = request.args.get('type', '')
    print(transport_type)
    for key, value in VALID_EXCLUSIONS.items():
        if transport_type == key:
            exclusions.pop(value)
            break
    else:
        exclusions = 0

    CLIENT.find_destinations_for('stop', id_, exclusions=exclusions)
    departures = CLIENT.result
    departures_info = []
    for departure in generator_departure_info(departures):
        departures_info.append(departure)
    departures_info.sort(key=attrgetter('location'))
    return render_template("departures.html", departures_info=departures_info)


@app.route('/stops')
def get_stop_information():
    """
    """

    req = request.args.get('query', False)
    CLIENT.find_stops_by_name('any', req)
    selected_types = int(request.args.get('types', '0   '))
    data = list(generator_stop_information(CLIENT, selected_types, req)) if req else []
    return render_template('stops.html', data=data, type=VALID_TRANSPORT.get(selected_types, ''))


@app.route('/trips')
def get_trip_info():
    origin = request.args.get('origin', '')
    destination = request.args.get('origin', '')
    return 'bla'


# one post request? save a trip?


if __name__ == '__main__':
    app.run()
