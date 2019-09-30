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
from dateutil import tz

class Client():
    """# Client API Class for Trip Planner
    \nintitialises a swagger client to connect\
    to the trip planner api
    \n- `_instance` *protected* : TripPlannerAPI -> initialises swagger client instance
    \n- `result`: TripPlannerResponse -> Response from API server
    \n- `error`: int -> http error code / msg
    """
    def __init__(self):
        self._instance = instance.start()
        self.result = {}
        self.error = None
        self.version = '10.2.1.42' # stable version


    def find_stops_by_name(self, _type: str, query: str):
        """### Find Stop by name
        \nfind a stop from a specified POI, or suburb
        \nArgs:
            \n_type: specify type of stop specified by the api docs usually\
            `any`, `stop`, `platform`, etc.
            \nquery: search query, usually a stop ID or a name type: (str)
        """
        try:
            req = self._instance.tfnsw_stopfinder_request(
                JSONFORMAT, _type, query, COORDINATEFORMAT, version=self.version
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
            self, _type: str, query: str, exclusions: object,
            date_time=datetime.today()
    ):
        """### find destinations for specific stop/location
        find destinations for a specified stop taking in
        arrival/departure times, etc
            \nArgs:
                \n- `_type`: str -> type of stop to be searched,\
                usually any or stop, refer to the API docs for more info
                \n- `query`: str -> station to search, can be key words, suburbs, IDs, etc
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
                    tf_nswdm="true", exclude_means='checkbox', version=self.version
                )
            else: # otherwise search normally, or just exlude one option
                req = self._instance.tfnsw_dm_request(
                    JSONFORMAT, COORDINATEFORMAT, _type, query,
                    'dep', date, time,
                    mode='direct', tf_nswdm="true", exclude_means=exclusions, version=self.version
                )
        except ApiException as err:
            sys.exit(err)

        self.result = req
        self.error = req.error


    def find_trips_for_stop(
            self, *args, **kwargs
    ):
        """\n### Find Trips For Stop
        \nfind trips (possible departures) for a stop by taking in the departure origin and destination
        and a specified time and saves the result to the client `self.result` property
            \n*Args:
                \ndeparture: tuple -> location of origin  - ID or coordinates,
                    \n- specify ID with ('any', 'ID'),
                    \n- coordinates with ('coord', [long, lat]),
                \ndestination: tuple -> location of destination - ID or coordinates
                    \n- specify ID with ('any', 'ID')
                    \n- coordinates with ('coord', [long, lat])
            \n**kwargs:-> containing additional information like:
                \n- `date_time`: datetime: specified time
                \n- `calc_num_of_trips`: total number of trips to be returned
                \n- `wheelchair`: str -> default set to 'off'.
                set 'on' to return wheelchair accessible options
        """
        departure, destination, dep = args
        date_time = (
            datetime.now(tz=tz.gettz('Australia/Sydney'))
            if not kwargs.get('date_time', False) else kwargs['date_time']
        )
        calc_number_of_trips = (
            5 if not kwargs.get('calc_number_of_trips', False)
            else kwargs['calc_number_of_trips']
        )
        # formate datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'
        date, time = create_date_and_time(date_time, format_date, format_time)
        req = self._instance.tfnsw_trip_request2(
            JSONFORMAT, COORDINATEFORMAT, dep, date, time, *departure,
            *destination, tf_nswtr="true", calc_number_of_trips=calc_number_of_trips, version=self.version)
        self.result = req
        self.error = req.error

    def request_status_info(self, *params):
        """
        find detailed status reports on potential, trainworks,
        delays for specified stops. Not implemented
        """

