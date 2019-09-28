"""
handles yielding meaningful data to client by
filtering and using algorithms
"""
from datetime import datetime
from dateutil import tz
from swagger_client.models import (
    DepartureMonitorResponse
)
from client.services.app_locals import VALID_TRANSPORT


def date_parser(departure_time, time_format="%Y-%m-%dT%H:%M:%SZ"):
    """
    parses a date string using the specified date_time_format,
    and converts it to Australian Time localtime
    """
    # Specify Timezone to convert to and from ie UTC -> Sydney localtime
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')

    # replace will specify the date format to convert from
    # and astimezone will convert it to Australian GMT
    parsed_date = datetime.strptime(
        departure_time, time_format
    ).replace(tzinfo=from_zone).astimezone(to_zone)


    return parsed_date


def generator_departure_info(
        events: DepartureMonitorResponse
) -> (int, int, int, str, str):
    """
    yields departure information as
    hours: int
    minutes: int
    seconds: int
    routenumber: str
    destination: str
    """
    for event in events.stop_events:
        transportation = event.transportation
        route = transportation.number
        dest = transportation.destination.name
        # location = event.location

        departure_time = event.departure_time_planned
        parsed_date = date_parser(departure_time)
        today = datetime.now().astimezone(tz.gettz('Australia/Sydney'))
        countdown = parsed_date - today

        # if the train has already passed skip to next data set
        if countdown.total_seconds() < 0:
            continue
        # in order to calculate the hours, mins and secs, we must
        # divide the total seconds to produce total hours and divide the
        # remainder to find minutes and seconds

        # will return division result + remainder
        hours, remainder = divmod(countdown.seconds, 3600)
        # devide remainder by 60 remainder which will be seconds
        minutes, seconds = divmod(remainder, 60)
        yield (
            hours, minutes, seconds, route, dest
        )


def create_date_and_time(
        date: datetime, format_date: str, format_time: str
):
    """
    returns a tuple of strings containing a formatted
    date and time strings, taking in a datetime object
    and the specified formats for date and time in `format_date` and `format_time`
        Args:
            date: datetime - date to format to str
            format_date: str - specified date format
            format_time: str - specified time format
    """

    today = datetime.strftime(date, format_date)
    time = datetime.strftime(date, format_time)
    return today, time


def generator_trip_data(journeys):
    """
    create trip date. TBD
    """

    def get_stop_info(stops, legs):
        """
        """
        for leg in legs:
            for seq_num, sequence in enumerate(leg.stop_sequence):
                if seq_num == 0:
                    # create new key entry for each leg
                    type_ = (
                        leg.transportation.name
                        if leg.transportation.name is not None else 'walk'
                    )
                    stops[type_] = []

                # attempt to get live updates/ est. otherwise get planned dep/arrival times
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
                stops[type_].append(f'{sequence.name} arrives: {departure}')

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

        yield (
            total_fare, total_duration, summary, depart_day, depart_time,
            arrive_day, arrive_time, stops
        )

