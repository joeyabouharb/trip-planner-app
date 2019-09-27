"""
handles data formatting and algorithms
"""
from collections import namedtuple
from datetime import datetime, timedelta
from swagger_client.models import (
    DepartureMonitorResponse, StopFinderResponse, StopFinderLocation
)


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
        location = event.location
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        time = event.departure_time_planned
        parsed_date = datetime.strptime(time, time_format)
        countdown = parsed_date - datetime.now()
        # if the train has already passed skip to next data set
        if countdown.total_seconds() < 0:
            continue
        # in order to calculate the hours, mins and secs, we must
        # divide the total seconds to produce total hours and divide the
        # remainder to find minutes and seconds
        hours, remainder = divmod(countdown.seconds, 3600) # will return division result + remainder
        minutes, seconds = divmod(remainder, 60) # devide remainder by 60 remainder which will be seconds
        yield (
                hours, minutes, seconds, route, dest
            )

def create_date_and_time(
    date: datetime, format_date: str, format_time
):
    """

    """
    # api usually returns a schedule 10 hours behind,
    # adds 10 hours to specified time
    fixed_date = date + timedelta(hours=10)
    today = datetime.strftime(fixed_date, format_date)
    time = datetime.strftime(fixed_date, format_time)
    return today, time
