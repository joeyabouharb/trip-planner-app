"""
set up configuration for swagger
set up your api as per instruction in the README
"""


from client.config.environment import API_KEY
from swagger_client import Configuration


def configure_swagger()\
-> (Configuration):
    """
    returns a configured swagger, with APIKEY set
    """
    config = Configuration()
    config.access_token = API_KEY

    return config
