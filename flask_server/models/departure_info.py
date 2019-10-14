"""
class model for departure information for a particular stop
"""


class DepartureInfo:
    """
    contains the information about departure information such as:

    Props:

    `hours`: int -> hours to departure,

    `minutes`: int -> minutes to departure,

    `seconds` int -> seconds to departure,

    `route`: str -> route origin,
    
    `dest`: str -> route destination,
    """
    def __init__(self, *props):
        hours, minutes, seconds, route, dest, location, type_, _id = props
        self.time_to_arrive = hours, minutes, seconds
        self.route = route
        self.dest = dest
        self.id = _id
        self.location = location
        self.type_ = type_

    def __repr__(self) -> str:
        """
        returns departure information as a string message,
        """
        hours, minutes, seconds = self.time_to_arrive
        return (
            f'-{self.type_}\n'
            f' {hours} hours, {minutes} minutes and {seconds} '
            f'seconds from {self.location}\n {self.route} to {self.dest}'
        )

    def to_dict(self) -> dict:
        """
        returns class properties as dict, reserved for api usage
        """
        return self.__dict__
