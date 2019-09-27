"""
responsible for setting up swagger instance
"""

from swagger_client.api import TripPlannerApi
from swagger_client.api_client import ApiClient
from client.config.config import configure_swagger

def start() -> (TripPlannerApi):
    """
    start a swagger instance
    """
    config = configure_swagger()
    client = ApiClient(config)
    return TripPlannerApi(client)

