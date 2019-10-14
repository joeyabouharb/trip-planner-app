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
from swagger_client.models.additional_info_response import AdditionalInfoResponse
from swagger_client.rest import ApiException

import flask_server.services.swagger_instance as instance
from flask_server.services.app_locals import (
   JSON_FORMAT, COORDINATE_FORMAT
)
from flask_server.services.data_factory import (
    create_date_and_time, date_parser
)


class Client:
    """# Client API Class for Trip Planner

    initialises a swagger client to connect\
    to the trip planner api

    - `_instance` *protected* : TripPlannerAPI -> initialises swagger client instance

    - `result`: TripPlannerResponse -> Response from API server

    - `error`: int -> http error code / msg
    """

    def __init__(self, key):
        # start up swagger client instance upon initialisation
        self._instance = instance.start(key)
        self.error = None
        self.version = '10.2.1.42'  # stable version

    def find_stops_by_name(
            self, _type: str, query: str, is_id=False
    ) -> StopFinderResponse:
        """### Find Stop by name
        find a stop from a specified POI, or suburb
        Args:

        _type: specify type of stop specified by the api docs usually\
        `any`, `stop`, `platform`, etc.

        query: search query, usually a stop ID or a name type: (str)
        """
        # if search based on trip_id. returns the best match on true
        tf_nswsf = "true" if is_id else ""
        try:
            req = self._instance.tfnsw_stopfinder_request(
                JSON_FORMAT, _type, query, COORDINATE_FORMAT,
                version=self.version, tf_nswsf=tf_nswsf
            )
            self.error = 404 if req is None else 200
        except Exception as err:
            print(err)
            req = None
            self.error = 500
        return req

    def find_stops_near_coord(self, *params):
        """
        """

    def find_destinations_for(
            self, _type: str, query: str, request_type: str,
            date_time=None
    ) -> DepartureMonitorResponse:
        """### find destinations for specific stop/location
        find destinations for a specified stop taking in arrival/departure times, etc

        Args:

        - `_type`: str -> type of stop to be searched,\
        usually any or stop, refer to the API docs for more info

        - `query`: str -> station to search, can be key words, suburbs, IDs, etc
        """
        format_date = '%Y%m%d'
        format_time = '%H%M'
        if date_time is None:
            date_time = datetime.now(tz.tzlocal()).astimezone(tz.gettz("Australia/Sydney"))
            # format datetime to a string
            date_str, time = create_date_and_time(date_time, format_date, format_time)
        else:
            date_str, time = date_time
            is_date = date_parser(f'{date_str} {time}', '%Y/%m/%d %I:%M%p')
            if is_date:
                date_str, time = create_date_and_time(is_date, format_date, format_time)
        # sends a request to the api using the swagger instance
        try:
            req = self._instance.tfnsw_dm_request(
                JSON_FORMAT, COORDINATE_FORMAT, _type, query,
                request_type, date_str, time,
                mode='direct', tf_nswdm="true", version=self.version
            )
            self.error = 404 if req.stop_events is None else 200
        except Exception as err:
            print(err)
            req = None
            self.error = 500

        return req

    def find_trips_for_stop(
            self, *args, **kwargs
    ) -> TripRequestResponse:
        """### Find Trips For Stop
        find trips (possible departures) for a stop by taking in the departure origin and destination
        and a specified time and saves the result to the client `self.result` property

        *Args:

        departure: tuple -> location of origin  - ID or coordinates,

        - specify ID with ('any', 'ID'),

        - coordinates with ('coord', [long, lat]),

        destination: tuple -> location of destination - ID or coordinates

        - specify ID with ('any', 'ID')

        - coordinates with ('coord', [long, lat])

        **kwargs:-> containing additional information like:

        - `date_time`: datetime: specified time

        - `calc_num_of_trips`: total number of trips to be returned

        - `wheelchair`: str -> default set to 'off'.

        set 'on' to return wheelchair accessible options
        """
        departure, destination, dep = args

        date_time = (
            datetime.now(tz.tzlocal()).astimezone(tz=tz.gettz('Australia/Sydney'))
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
        except Exception as err:
            print(err)
            req = None
            self.error = 500
        return req

    def request_status_info(self, stop, publication_status="current") -> AdditionalInfoResponse:
        """
        find detailed status reports on potential, train works, delays for specified stops.
        
        Not implemented
        """
        req = self._instance.tfnsw_addinfo_request(
            JSON_FORMAT, itd_l_pxx_sel_stop=stop, filter_publication_status=publication_status
        )
        return req
