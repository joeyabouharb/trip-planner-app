"""
data that can be used in the api
"""

VALID_EXCLUSIONS = {
    'trains': 'exclMOT_1', 'light rail': 'exclMOT_4', 'bus': 'exclMOT_5',
    'coach': 'exclMOT_7', 'ferry': 'exclMOT_9', 'school bus': 'exclMOT_11'
}

VALID_TRANSPORT = {
    1: 'Train', 4: 'Light Rail', 5: 'Bus', 7: 'Coach', 9: 'Ferry', 11: 'School Bus', 99: 'Walk', 100: 'Walk'
}

VALID_PERSONS = ['ADULT', 'CHILD', 'SENIOR', 'SCHOLAR', ]