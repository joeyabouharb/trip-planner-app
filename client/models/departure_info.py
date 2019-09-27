class DepartureInfo():
    """
    contains the information about departure information
    """
    def __init__(self, *args):
        hours, minutes, seconds, route, dest = args
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.route = route
        self.dest = dest

    def to_str(self, location):
        """
        returns departure information as a string message,
        """
        return (
            f'{self.hours} hours, {self.minutes} minutes and {self.seconds} '
            f'seconds from {location.name}\n{self.route} to {self.dest}'
        )


    def to_dict(self):
        """
        returns class properties as dict, reserved for api usage
        """
        return self.__dict__
