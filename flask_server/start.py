"""# startup wsgi container
Flask server app wsgi container (to be used by gunicorn, etc)
This works by connecting to our flask app by proxy
"""


from flask import render_template
from flask_server import create_app

APP = create_app()

@APP.errorhandler(404)
def not_found(_):
    """
    not found error
    """
    return render_template("404.jinja2"), 404


@APP.errorhandler(500)
def service_unavailable(_):
    """
    500 error handler
    """
    return "Service Unavailable :(", 500


if __name__ == '__main__':
    APP.run()
