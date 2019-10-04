"""
handles yielding/returning meaningful data to client by
filtering/mapping through data like stop information, departures and journey info
and converting data types
such as dates, etc
"""

from datetime import datetime
from typing import Sequence

from dateutil import tz
from swagger_client.models import (
    DepartureMonitorResponse, StopFinderLocation, TripRequestResponseJourney,
    TripRequestResponseJourneyLeg
)

from flask_server.models.departure_info import DepartureInfo
from flask_server.models.trip_journey import TripJourney
from flask_server.services.app_locals import VALID_TRANSPORT


def generator_stop_information(
        locations: Sequence[StopFinderLocation],
        selected_types: Sequence[int], query: str, is_suburb=False
) -> Sequence[tuple]:
    """
    get stop information
    """
    print(selected_types)
    for location in locations:
        location.modes = location.modes if location.modes is not None else []
        if selected_types:
            if not any(selected_type in location.modes for selected_type in selected_types):
                continue
            else:
                print(location.modes)
        if is_suburb:
            if location.name.split(' ')[-1] != query.capitalize():
                continue
        yield location.id, location.name




def date_parser(
        departure_time: str, time_format="%Y-%m-%dT%H:%M:%SZ"
) -> datetime:
    """
    parses a date string using the specified date_time_format
    and converts it to Australian Time localtime
        args:
            `departure_time`: str -> time of departure in string format, implied UTC format
            `time_format`: str -> format to aid in parsing string to datetime
        :rtype: datetime
    """
    # Specify Timezone to convert to and from ie UTC -> Sydney localtime
    # this pulls localtime information from `/usr/share/zoneinfo` (linux sys)
    # this includes daylight savings info eg. AEST-10AEDT,M10.1.0,M4.1.0/3
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    # replace will specify the date format to convert from (UTC)
    # and `as times zone` will convert it to specified timezone eg. Australian EST
    parsed_date = datetime.strptime(
        departure_time, time_format
    ).replace(tzinfo=from_zone).astimezone(to_zone)

    return parsed_date


def generator_departure_info(
        events: DepartureMonitorResponse
) -> Sequence[DepartureInfo]:
    """## Generate departure information for a stop
    \nArgs:
        \n- `events`: `DepartureMonitorResponse` -> stop events for a specified location
        \n- `of_type`: str -> specified stop type ID to filter. as defined in the API docs
    \nyields:
        \n- `hours`: int,
        \n- `minutes`: int,
        \n- `seconds`: int,
        \n- `route`: str,
        \n- `dest`: str,
        \n- `location`: str
    """
    if events.stop_events is None:
        return False
    for event in events.stop_events:
        transport_type = event.transportation.product.icon_id
        transportation = event.transportation
        route = transportation.number
        dest = transportation.destination.name
        location = event.location.name
        id_ = event.location.id
        type_ = VALID_TRANSPORT[transport_type]
        departure_time = event.departure_time_planned
        parsed_date = date_parser(departure_time)
        # ensure datetime is formatted with timezone info
        today = datetime.now(tz=tz.gettz('Australia/Sydney'))
        countdown = parsed_date - today

        # if the train has already passed skip to next data set
        if countdown.total_seconds() < 0:
            continue
        # in order to calculate the hours, mins and secs, we must
        # divide the total seconds to produce total hours and divide the
        # remainder to find minutes and seconds
        # will return division result + remainder
        hours, remainder = divmod(countdown.seconds, 3600)
        # decide remainder by 60 remainder which will be seconds
        minutes, seconds = divmod(remainder, 60)
        yield DepartureInfo(hours, minutes, seconds, route, dest, location, type_, id_)


def create_date_and_time(
        date: datetime, format_date: str, format_time: str
) -> (str, str):
    """
    returns a tuple of strings containing a formatted
    date and time strings, taking in a datetime object
    and the specified formats for date and time in `format_date` and `format_time`
        \nArgs:
            \ndate: datetime - date to format to str,
            \nformat_date: str - specified date format,
            \nformat_time: str - specified time format,
    """

    today = datetime.strftime(date, format_date)
    time = datetime.strftime(date, format_time)
    return today, time


def generator_trip_data(
        journeys: Sequence[TripRequestResponseJourney]
) -> Sequence[TripJourney]:
    """
    yields trip information from journeys:
        \nArgs:
            \njourneys: list -> list of journeys, received from the API Call\n
        \nYields:
            \ntotal_fare: float -> cost of journey,
            \ntotal_duration: float -> duration (in minutes) of journey,
            \nsummary: list -> types of transport used in journey,
            \ndepart_day, depart_time: tuple -> (str, str) -> departure day/time information,
            \narrive_day, arrive_time: tuple -> (str, str) -> arrival day/time information,
            \nstops: dict -> all stops in journey
    """

    def get_stop_info(
            stops_info: dict, legs_data: Sequence[TripRequestResponseJourneyLeg]
    ):
        """
        modifies existing dictionary and appends
        new stopping information for each 'leg' in a journey
            \nArgs:
                \n`stops`: dict -> containing information about stops,
                \n`legs`: JourneyLegs -> all legs in a journey. ie. transport and network changes,
        """
        type_ = ''
        for leg in legs_data:
            if leg.stop_sequence is None:
                continue
            for seq_num, sequence in enumerate(leg.stop_sequence):
                if seq_num == 0:
                    # create new key entry for each leg/ network change in journey
                    type_ = (
                        leg.transportation.name
                        if leg.transportation.name is not None else 'walk'  # trip is walk if None
                    )
                    stops_info[type_] = []

                # attempt to get live updates/ estimated otherwise get planned dep/arrival times
                if sequence.departure_time_estimated is not None:
                    departure = date_parser(sequence.departure_time_estimated)
                elif sequence.arrival_time_estimated is not None:
                    departure = date_parser(sequence.arrival_time_estimated)
                elif sequence.departure_time_planned is not None:
                    departure = date_parser(sequence.departure_time_planned)
                elif sequence.arrival_time_planned is not None:
                    departure = date_parser(sequence.arrival_time_planned)
                else:
                    # if no information is available output message:
                    departure = 'Unavailable'
                if departure != 'Unavailable':
                    # parse dates and return the formatted time string
                    _, departure = create_date_and_time(departure, '', '%H:%M')
                stops_info[type_].append(f'{sequence.name} arrives: {departure}')

    # end of function

    for journey in journeys:
        legs = journey.legs
        fares = journey.fare.tickets

        total_fare = sum(
            float(fare.properties.price_total_fare)
            for fare in fares if fare.person == 'SCHOLAR'
        )
        total_duration = sum(leg.duration for leg in legs) / 60
        total_duration = round(total_duration, 2)

        summary = [
            VALID_TRANSPORT[leg.transportation.product.icon_id]
            for leg in legs
        ]

        depart = date_parser(legs[0].origin.departure_time_estimated)
        depart_day, depart_time = create_date_and_time(depart, '%A,  %d-%m-%Y', '%H:%M%Z')

        arrive = date_parser(legs[-1].destination.arrival_time_estimated)
        arrive_day, arrive_time = create_date_and_time(arrive, '%A,  %d-%m-%Y', '%H:%M%Z')

        stops = {}
        get_stop_info(stops, legs)

        yield TripJourney(
            total_fare, total_duration, summary, depart_day, depart_time,
            arrive_day, arrive_time, stops
        )