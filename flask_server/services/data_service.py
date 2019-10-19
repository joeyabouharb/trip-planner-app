"""
handles yielding/returning meaningful data to client by
filtering/mapping through data like stop information, departures and journey info
and converting data types
such as dates, etc
"""
from datetime import datetime
from typing import Sequence, Dict

from dateutil import tz
from swagger_client.models import (
    DepartureMonitorResponse, StopFinderLocation,
    TripRequestResponseJourney, AdditionalInfoResponseMessage
)

from flask_server.models.departure_info import DepartureInfo
from flask_server.models.trip_journey import TripJourney


def stop_information_generator(
        locations: Sequence[StopFinderLocation],
        selected_types: Sequence[int], query: str, is_suburb=False
) -> Sequence[tuple]:
    """
    generate information about current stops, filter by suburb and yield
    matching stop names
    :param locations:
    :param selected_types:
    :param query:
    :param is_suburb:
    :return: Sequence[tuple]
    """

    for location in locations:
        # get available transport modes ie, train, bus etc.
        location.modes = (
            location.modes if location.modes is not None else []
        )  # avoid errors by returning an empty array if no modes are found

        # if a transport type was specified filter and return types
        if selected_types:
            if not any(selected_type in location.modes for selected_type in selected_types):
                continue
        # search by suburb if selected
        if is_suburb:
            if location.name.split(' ')[-1] != query.capitalize():
                continue

        yield location.id, location.name, location.coord


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
    try:
        parsed_date = datetime.strptime(
            departure_time, time_format
        ).replace(tzinfo=from_zone).astimezone(to_zone)
    except ValueError as err:
        print(err)
        parsed_date = None
    return parsed_date


def departure_info_generator(
        events: DepartureMonitorResponse, date_time=None
) -> Sequence[DepartureInfo]:
    """## Generate departure information for a stop
    args
    :arg: `events`: `DepartureMonitorResponse` -> stop events for a specified location
    :arg: `of_type`: str -> specified stop type ID to filter. as defined in the API docs
    yields:

    :return DepartureInfo
    """

    for event in events.stop_events:
        route = event.transportation.number
        dest = event.transportation.destination.name
        location = event.location.name
        id_ = event.location.id
        departure_time = event.departure_time_planned
        parsed_date = date_parser(departure_time)
        # ensure datetime is formatted with timezone info
        # convert date to AEST
        if date_time is None:
            planned_date = datetime.now(tz.tzlocal()).astimezone(tz=tz.gettz('Australia/Sydney'))
        else:
            planned_date = datetime.strptime(
                f'{date_time[0]} {date_time[1]}', '%Y/%m/%d %I:%M%p'
            ).replace(tzinfo=tz.gettz('AEST'))
        countdown = parsed_date - planned_date
        # if the train has already passed skip to next data set

        # in order to calculate the hours, minutes and secs, we must
        # divide the total seconds to produce total hours and divide the
        # remainder to find minutes and seconds
        # will return division result , remainder
        hours, remainder = countdown.seconds // 3600, countdown.seconds % 3600
        # decide remainder by 60 remainder which will be seconds
        minutes, seconds = remainder // 60, remainder % 60
        yield DepartureInfo(hours, minutes, seconds, route, dest, location, id_)


def create_date_and_time(
        date: datetime, format_date: str, format_time: str
) -> (str, str):
    """
    returns a tuple of strings containing a formatted
    date and time strings, taking in a datetime object
    and the specified formats for date and time in `format_date` and `format_time`

    Args:

    date: datetime - date to format to str,

    format_date: str - specified date format,

    format_time: str - specified time format,
    """

    today = datetime.strftime(date, format_date)
    time = datetime.strftime(date, format_time)
    return today, time


def get_stop_info(legs) -> (Dict, Sequence[float]):
    """
    gets stop information in all legs of the current trip journey as dictionary
    as well as the coordinates in the list as coords
    :return: result, coords
    """
    result = {}
    coords = []
    type_ = ''
    for leg in legs:
        if leg.stop_sequence is None:
            continue
        for seq_num, sequence in enumerate(leg.stop_sequence):
            if seq_num == 0:
                # create new key entry for each leg/ network change in journey
                # Note that the Api returns None when it means a walking trip
                type_ = (
                    leg.transportation.name
                    if leg.transportation.name is not None else 'Walking'
                )
                result[type_] = []

            # attempt to get live updates/ estimated otherwise get planned dep/arrival times
            if sequence.departure_time_estimated is not None:
                departure_time = date_parser(sequence.departure_time_estimated)
            elif sequence.arrival_time_estimated is not None:
                departure_time = date_parser(sequence.arrival_time_estimated)
            elif sequence.departure_time_planned is not None:
                departure_time = date_parser(sequence.departure_time_planned)
            elif sequence.arrival_time_planned is not None:
                departure_time = date_parser(sequence.arrival_time_planned)
            else:
                # if no information is available output message:
                departure_time = 'Unavailable'
            if departure_time != 'Unavailable':
                # parse dates and return the formatted time string only
                _, departure_time = create_date_and_time(departure_time, '', '%H:%M')
            coords.append(sequence.coord)
            result[type_].append((sequence.name, departure_time))
    return result, coords


def trip_journeys_generator(
        journeys: Sequence[TripRequestResponseJourney], concession_type: str
) -> Sequence[TripJourney]:
    """
    ## yields trip information from journeys.
    Args:
    journeys: list -> list of journeys, received from the API Call

    Yields:
    total_fare: float -> cost of journey,
    total_duration: float -> duration (in minutes) of journey,
    summary: list -> types of transport used in journey,
    depart_day, depart_time: tuple -> (str, str) -> departure day/time information,
    arrive_day, arrive_time: tuple -> (str, str) -> arrival day/time information,
    stops: dict -> all stops in journey
    """
    for journey in journeys:
        fares = journey.fare.tickets
        total_fare = sum(
            float(fare.properties.price_total_fare)
            for fare in fares if fare.person == concession_type
        )  # Sum of fare
        total_fare = round(total_fare, 2)
        # calculate total duration in minutes and round up 2 decimal places
        total_duration = sum(leg.duration for leg in journey.legs) / 60
        total_duration = round(total_duration, 2)
        origin, dest = journey.legs[0].origin.name, journey.legs[-1].destination.name
        depart = date_parser(journey.legs[0].origin.departure_time_estimated)
        depart_day, depart_time = create_date_and_time(depart, '%A,  %d-%m-%Y', '%H:%M%Z')

        arrive = date_parser(journey.legs[-1].destination.arrival_time_estimated)
        arrive_day, arrive_time = create_date_and_time(arrive, '%A,  %d-%m-%Y', '%H:%M%Z')
        stops, coords = get_stop_info(journey.legs)  # get list of stops in legs as dict
        yield TripJourney(
            total_fare, total_duration,
            depart_day, depart_time,
            arrive_day, arrive_time, stops, coords, origin, dest
        )


def status_info_generator(current_infos: Sequence[AdditionalInfoResponseMessage]):
    """
    generates status info for a stop
    :param current_infos:
    :return: tuple( priority, title, content, from_time, to )
    """

    for message in current_infos:
        title = message.subtitle
        content = message.content
        priority = message.priority
        timestamp = message.timestamps
        from_time = date_parser(timestamp.creation)
        date, time = create_date_and_time(from_time, "%Y-%m-%d", "%H:%M")
        from_time = f'{date} {time}'
        to_date = date_parser(timestamp.validity[-1].to)
        date, time = create_date_and_time(to_date, "%Y-%m-%d", "%H:%M")
        to_date = f'{date} {time}'
        yield priority, title, content, from_time, to_date
