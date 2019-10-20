"""# startup wsgi container
Flask server app wsgi container (to be used by gunicorn, etc)
This works by connecting to our flask app by proxy
"""

from flask_server import create_app

APP = create_app()

if __name__ == '__main__':
    APP.run()
