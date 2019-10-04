"""
Defines a client class to handle request from the trip planner api
hands back data filtered from the trip planner back to
the server. Caching Class
"""

import sys
from datetime import datetime

from dateutil import tz
from swagger_client.models.departure_monitor_response import DepartureMonitorResponse
from swagger_client.models.stop_finder_response import StopFinderResponse
from swagger_client.models.trip_request_response import TripRequestResponse
from swagger_client.rest import ApiException

import flask_server.services.swagger_instance as instance
from flask_server.services.app_locals import (
    VALID_EXCLUSIONS, JSON_FORMAT, COORDINATE_FORMAT
)
from flask_server.services.data_factory import (
    create_date_and_time
)


class Client:
    """# Client API Class for Trip Planner
    \ninitialises a swagger client to connect\
    to the trip planner api
    \n- `_instance` *protected* : TripPlannerAPI -> initialises swagger client instance
    \n- `result`: TripPlannerResponse -> Response from API server
    \n- `error`: int -> http error code / msg
    """

    def __init__(self):
        self._instance = instance.start()
        self.result = None
        self.error = None
        self.version = '10.2.1.42'  # stable version

    def find_stops_by_name(
            self, _type: str, query: str, is_id=False
    ) -> StopFinderResponse:
        """### Find Stop by name
        \nfind a stop from a specified POI, or suburb
        \nArgs:
            \n_type: specify type of stop specified by the api docs usually\
            `any`, `stop`, `platform`, etc.
            \nquery: search query, usually a stop ID or a name type: (str)
        """
        # if search based on trip_id. returns the best match on true
        tf_nswsf = "true" if is_id else ""
        try:
            req = self._instance.tfnsw_stopfinder_request(
                JSON_FORMAT, _type, query, COORDINATE_FORMAT, version=self.version, tf_nswsf=tf_nswsf
            )
            self.error = 404 if req is None else 200
            return req
        except ApiException as err:
            sys.exit(err)

    def find_stops_near_coord(self, *params):
        """
        """

    def find_destinations_for(
            self, _type: str, query: str, transport_types: list,
            date_time=datetime.today()
    ) -> DepartureMonitorResponse:
        """### find destinations for specific stop/location
        find destinations for a specified stop taking in
        arrival/departure times, etc
            \nArgs:
                \n- `_type`: str -> type of stop to be searched,\
                usually any or stop, refer to the API docs for more info
                \n- `query`: str -> station to search, can be key words, suburbs, IDs, etc
        """

        exclusions = {
            'exclMOT_1': '1', 'exclMOT_4': '1', 'exclMOT_5': '1',
            'exclMOT_7': '1', 'exclMOT_9': '1', 'exclMOT_11': '1'
        }
        for key, value in VALID_EXCLUSIONS.items():
            if any(transport_type == key for transport_type in transport_types):
                exclusions.pop(value)
        if not transport_types[0] and len(transport_types) == 1:
            exclusions = 0
        # format datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'

        date_str, time = create_date_and_time(date_time, format_date, format_time)
        # sends a request to the api using the swagger instance
        try:
            # if the user wishes to exclude multiple transport options
            if isinstance(exclusions, dict):

                req = self._instance.tfnsw_dm_request(
                    JSON_FORMAT, COORDINATE_FORMAT, _type, query,
                    'dep', date_str, time, exclusions=exclusions, mode='direct',
                    tf_nswdm="true", exclude_means='checkbox', version=self.version
                )
            else:  # otherwise search normally, or just exclude one option
                req = self._instance.tfnsw_dm_request(
                    JSON_FORMAT, COORDINATE_FORMAT, _type, query,
                    'dep', date_str, time,
                    mode='direct', tf_nswdm="true", exclude_means=exclusions, version=self.version
                )
        except ApiException as err:
            sys.exit(err)

        self.error = 404 if req.stop_events is None else 200
        return req

    def find_trips_for_stop(
            self, *args, **kwargs
    ) -> TripRequestResponse:
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
        # format datetime to a string
        format_date = '%Y%m%d'
        format_time = '%H%M'
        date_str, time = create_date_and_time(date_time, format_date, format_time)
        try:
            req = self._instance.tfnsw_trip_request2(
                JSON_FORMAT, COORDINATE_FORMAT, dep, date_str, time, *departure,
                *destination, tf_nswtr="true", calc_number_of_trips=calc_number_of_trips, version=self.version)
            self.error = 404 if req.journeys is None else 200
            return req
        except ApiException as err:
            sys.exit(err)

    def request_status_info(self, *params):
        """
        find detailed status reports on potential, train works,
        delays for specified stops. Not implemented
        """
