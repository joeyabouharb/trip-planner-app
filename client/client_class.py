"""
Defines a client class to handle request from the tripplanner api
hands back data filtered from the trip planner back to
the server. Caching Class
"""

import sys
from datetime import datetime
from swagger_client.rest import ApiException
import client.services.swagger_instance as instance
from client.config.environment import JSONFORMAT, COORDINATEFORMAT
from client.models.departure_info import DepartureInfo
from client.services.data_factory import (
    generator_departure_info, create_date_and_time, generator_trip_data
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
            sys.exit(err)

    def find_stops_near_coord(self, *params):
        """
        not implemented
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
            sys.exit(err)

        self.result = req
        self.error = req.error


    def find_trips_for_stop(
            self, departure, destination,
            dep='dep', date_time=datetime.today()
    ):
        """
        find trips () for a stop by taking in the departure origin and destination
        and a specified time and saves the result to the client `result` property
            Args:
                departure: tuple -> location of origin  - ID or coordinates
                    specify ID with ('any', 'ID')
                    or coordinates with ('coord', [long, lat])
                destination: tuple -> location of destination - ID or coordinates
                    specify ID with ('any', 'ID')
                    or coordinates with ('coord', [long, lat])
                dep: str -> specify whether you are requesting departure times or arrival times
                datetime: datetime -> defaults to today, get trip information for a specific time
        """

        calc_number_of_trips = '6'
        # formate datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'
        date, time = create_date_and_time(date_time, format_date, format_time)
        req = self._instance.tfnsw_trip_request2(
            JSONFORMAT, COORDINATEFORMAT, dep, date, time, *departure,
            *destination, tf_nswtr="true", calc_number_of_trips=calc_number_of_trips)
        self.result = req
        self.error = req.error

    def request_status_info(self, *params):
        """
        find detailed status reports on potential, trainworks,
        delays for specified stops. Not implemented
        """



if __name__ == '__main__':

    CLIENT = Client()
    CLIENT.find_trips_for_stop(('any', '10101398'), ('any', '10101112'))
    generator_trip_data(CLIENT.result.journeys)

    CLIENT.find_stops_by_name('platform', 'North Sydney')
    LOCATIONS = CLIENT.result.locations
    if not CLIENT.error:
        for i, location in enumerate(LOCATIONS):
            print(f'{i+1})', location.id, ':', location.name)
        SELECTED = int(input('Select: ')) - 1
        SELECTED_LOCATION = LOCATIONS[SELECTED]
        ID = SELECTED_LOCATION.id
        EXCLUSIONS = 0 # what information to exclude
        CLIENT.find_destinations_for('any', ID, EXCLUSIONS)
        EVENTS = CLIENT.result
        # if no information is available for the searched stop go to next search
        if CLIENT.error or not EVENTS.stop_events:
            sys.exit('no stop found?')

        DEPARTURES = []
        for event in generator_departure_info(EVENTS):
            # get next event in no data is yielded
            if not event:
                continue
            DEPARTURE = DepartureInfo(*event)
            print(DEPARTURE.to_str(SELECTED_LOCATION))
