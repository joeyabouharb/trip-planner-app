from flask import current_app

from flask_server.client.client_class import Client
from flask_server.services import swagger_instance


class __ClientFactory(object):
    """
    class factory (private) for building Swagger Client Classes during a Flask request
    """
    def init_app(self, app):
        self.__start(app)

    @staticmethod
    def __start(app):
        """
        Handles the loading and teardowns of our instantiated swagger
        instance stored inside our current app context
        :return:
        """
        @app.before_request
        def load_client():
            """
            loads swagger client as an extension to our current app
            using our key loading into our environment, during the lifetime of a
            request
            :return:
            """
            app.extensions['swagger_client'] =\
                swagger_instance.start(app.config['TRIP_PLANNER_API_KEY'])

        @app.teardown_appcontext
        def teardown(_):
            """
            pop our swagger client from the application context after a request is completed
            :param _:
            :return:
            """
            app.extensions.pop('swagger_client', None)

    @property
    def connection(self):
        """
        build and return our Client connection to be used during a request
        :return: Client configured with a swagger instance to interact with our API
        """
        return Client(
            current_app.extensions['swagger_client']
        )


# public interface for building Client connections during a request
CLIENT = __ClientFactory()
