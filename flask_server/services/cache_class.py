"""
contains definition to our cache class (json stub file)
"""
from pathlib import Path
import json


class Cache:
    """
    Cache service class that handles reading and writing
    from a json database
        :var filename
        :methods
            read_db
            write_db
    """
    def __init__(self, filename):
        self.filename = filename + '.json'
        self.data = []
        path = Path(self.filename)
        if not path.is_file():
            self.write_db(self.data, update=False)

    def write_db(self, data, update=True):
        """
        update json contents with new item
        :param data: item to append to json file
        :param update: check whether database must be updated
        :return:
        """
        if update:
            self.read_db()
            self.data.append(data)
        try:
            with open(self.filename, 'w+') as database:
                json.dump(self.data, database, indent=2)
        except json.JSONDecodeError as err:
            raise err

    def read_db(self):
        """
        read our database and store the results in our class object
        :return:
        """
        with open(self.filename, 'r') as database:
            data = json.load(database)
        self.data = data
