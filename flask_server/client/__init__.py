from flask import current_app

from flask_server.client.client_class import Client
from flask_server.services import swagger_instance


def init_app(app):
    """
    Handles the loading and teardowns of our instantiated swagger
    instance stored inside our current app context
    """
    app.before_request(load_client)
    app.teardown_appcontext(teardown)

def load_client():
    """
    loads swagger client as an extension to our current app
    using our key loading into our environment, during the lifetime of a
    request
    :return:
    """
    current_app.extensions['swagger_client'] =\
        swagger_instance.start(current_app.config['TRIP_PLANNER_API_KEY'])


def teardown(_):
    """
    pop our swagger client from the application context stack after a request is completed
    :param _:
    :return:
    """
    current_app.extensions.pop('swagger_client', None)


def connection() -> Client:
    """
    build and return our Client connection to be used during a request
    :return: Client configured with a swagger instance to interact with our API
    """
    return Client(
        current_app.extensions['swagger_client']
    )

