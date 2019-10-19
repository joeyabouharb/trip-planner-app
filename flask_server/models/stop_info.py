"""
stop info class model for mapping data onto sqlite Database
"""
from flask_server.server import DB


class StopInfo(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    stop_id = DB.Column(DB.String(100), unique=True, nullable=False)
    stop_name = DB.Column(DB.String(50), nullable=False)
    coord = DB.Column(DB.ARRAY(DB.String))

    def __repr__(self):
        return f'{self.__dict__}'
