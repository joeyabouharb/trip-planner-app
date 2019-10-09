"""
responsible for setting up swagger instance. to be injected in our client class
"""

from swagger_client.api import TripPlannerApi
from swagger_client.api_client import ApiClient
from swagger_client import Configuration


def start(api_key) -> TripPlannerApi:
    """
    start an instance of the trip planner api
    :param api_key: trip planner api key
    :return: TripPlannerApi
    """
    config = Configuration()
    config.access_token = api_key
    client = ApiClient(config)
    return TripPlannerApi(client)
