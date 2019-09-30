"""
Trip Journey Class Model Object
"""


class TripJourney():
    """
    model class defining properties for a single journey,
    including total fares, duration, stop info and departure / arrival times,
        \nProperties:
            \n`total_fare`: float -> stores fare cost (USD),
            \n`total_duration`: float -> stores duration of journey,
            \n`summary`: list -> contains a list to summize the transort types used in journey,
            \n`departure`: tuple -> contains a tuple of strs describing departure time (day, time),
            \n`arrival`: tuple -> contains tuple of time(str) of arrival (day, time),
            \n`stops`s: dict -> describes all stop information of trip, containing times and trip network,
    """
    def __init__(self, *args):

        total_fare, total_duration, summary,\
        depart_day, depart_time,\
        arrive_day, arrive_time, stops = args

        self.total_fare = total_fare
        self.total_duration = total_duration
        self.summary = summary
        self.departure = depart_day, depart_time
        self.arrival = arrive_day, arrive_time
        self.stops = stops

    def to_str(self):
        """
        return a meaningful string message containing information
        about the particular journey to serve to the client
        """
        pass
        # for trip_info, stop_data in stops.items():
        #     trip_str += f"\n\n{trip_info}\n"
        #     trip_str += "\n".join(stop_data)
        # print(
        #     f"{depart_day} - {depart_time}" ' to ' f"{arrive_day} - {arrive_time}\n"
        #     f' Trip Duration: {total_duration} minutes Cost: {total_fare}\n'
        #     "transport used: ",
        #     " -> ".join(summary), '\n',
        #     trip_str
        # )


    def to_dict(self):
        """
        turn to a class object to a dictionary
        """
        pass


    def number_of_stops(self):
        """
        get the total number of stops / trip changes in a journey
        """
        pass