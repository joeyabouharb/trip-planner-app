"""
responsible for setting up swagger instance
"""

from swagger_client.api import TripPlannerApi
from swagger_client.api_client import ApiClient
from swagger_client import Configuration


def start(api_key) -> TripPlannerApi:
    """
    start an instance of the trip planner api
    :param api_key:
    :return: TripPlannerApi
    """
    def configure_swagger() -> Configuration:
        """
        configure swagger with an API KEY
        :return: Configuration
        """
        conf = Configuration()
        conf.access_token = api_key
        return conf

    config = configure_swagger()
    client = ApiClient(config)
    return TripPlannerApi(client)
