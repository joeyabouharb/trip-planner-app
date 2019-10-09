"""
data that can be used in the api
"""

VALID_EXCLUSIONS = {
    'trains': 'exclMOT_1', 'light_rail': 'exclMOT_4', 'bus': 'exclMOT_5',
    'coach': 'exclMOT_7', 'ferry': 'exclMOT_9', 'school_bus': 'exclMOT_11'
}

VALID_TRANSPORT = {
    1: 'trains', 4: 'light_rail', 5: 'bus', 7: 'coach', 9: 'ferry', 11: 'school_bus', 99: 'walk', 100: 'walk'
}

VALID_PERSONS = ['ADULT', 'CHILD', 'SENIOR', 'SCHOLAR', ]

JSON_FORMAT = "rapidJSON"
COORDINATE_FORMAT = "EPSG:4326"

DEPARTURE_DB = 'departures'
TRIPS_DB = 'trips'
