"""
Defines a client class to handle request from the tripplanner api
hands back data filtered from the trip planner back to
the server. Caching Class 
"""

import client.services.swagger_instance as instance
from datetime import datetime, timedelta
from swagger_client.rest import ApiException
from client.config.environment import JSONFORMAT, COORDINATEFORMAT
from client.models.departure_info import DepartureInfo
from client.services.data_formats import (
    generator_departure_info, create_date_and_time
)


class Client():
    """
    intitialises a swagger client to connect
    to the trip planner api
    """
    def __init__(self):
        self._instance = instance.start()
        self.result = {}
        self.error = None


    def find_stops_by_name(self, _type: str, query: str):
        """
        find a stop from a specified POI, or suburb
        _type: specify type of stop specified by the api docs usually
        `any`, `stop`, `platform`, etc.
        query: search query, usually a stop ID or a name type: (str)
        """
        try:
            req = self._instance.tfnsw_stopfinder_request(
                JSONFORMAT, _type, query, COORDINATEFORMAT
            )
            self.result = req
            self.error = req.error
        except ApiException as err:
            exit(err)

    def find_stops_near_coord(self, *params):
        """
        """


    def find_destinations_for(
        self, _type: str, query: str, exclusions: object, date_time=datetime.today()
    ):
        """
        find destinations for a specified stop taking in
        arrival/departure times, etc
        """
        # formate datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'
        date, time = create_date_and_time(date_time, format_date, format_time)
        # sends a request to the api using the swagger instance
        try:
            # if the user wishes to exclude multiple transport options
            if isinstance(exclusions, dict):
                req = self._instance.tfnsw_dm_request(
                    JSONFORMAT, COORDINATEFORMAT, _type, query,
                    'dep', date, time, exclusions=exclusions, mode='direct',
                    tf_nswdm="true", exclude_means='checkbox'
                )
            else: # otherwise search normally, or just exlude one option
                req = self._instance.tfnsw_dm_request(
                    JSONFORMAT, COORDINATEFORMAT, _type, query,
                    'dep', date, time,
                    mode='direct', tf_nswdm="true", exclude_means=exclusions
                )
        except ApiException as err:
            exit(err)

        self.result = req
        self.error = req.error


    def find_trips_for_stop(
        self, departure, destination,
        dep='dep', calc_number_of_trips='1', date_time=datetime.today()
    ):
        """
        """
        # formate datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'
        date, time = create_date_and_time(date_time, format_date, format_time)
        req = self._instance.tfnsw_trip_request2(
            JSONFORMAT, COORDINATEFORMAT, dep, date, time, *departure,
            *destination, calc_number_of_trips=calc_number_of_trips)
        self.result = req
        self.error = req.error

    def request_status_info(self, *params):
        """
        find detailed status reports on potential, trainworks,
        delays for specified stops
        """
        pass


if __name__ == '__main__':
    """
    for testing only
    """
    client = Client()
    client.find_trips_for_stop(('any','10101112'), ('any', '10101397'))
    input(client.result)
    client.find_stops_by_name('platform', 'Belmore')
    locations = client.result.locations
    if not client.error:
        for i, location in enumerate(locations):
            print(f'{i+1})', location.id, ':', location.name)
        selected = int(input('Select: ')) - 1
        selected_location = locations[selected]
        _id = selected_location.id
        exclusions = 0 # what information to exclude
        client.find_destinations_for('stop', _id, exclusions)
        events = client.result # if no information is available for the searched stop go to next search
        if client.error or not events.stop_events:
            exit('no stop found?')
        departures = []
        for event in generator_departure_info(events):
            # get next event in no data is yielded
            if not event:
                continue
            departure = DepartureInfo(*event)
            print(departure.to_str(selected_location))



