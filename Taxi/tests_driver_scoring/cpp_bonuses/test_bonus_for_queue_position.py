import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


TEST_AIRPORT_SETTINGS = {
    'lipetsk_airport': {
        'econom': {
            'ALPHA': 0,
            'BETA': 1,
            'QUEUE_POSITION_WEIGHT': 60,
            'QUEUE_TIME_WEIGHT': 3,
            'MAX_ROBOT_TIME_SCORE_ENABLED': False,
            'MAX_ROBOT_TIME_SCORE': 0,
        },
    },
}

QUEUED = datetime.datetime(2020, 5, 18).strftime('%Y-%m-%dT%H:%M:%SZ')

BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {'source': {'geopoint': [39.52449, 52.69810]}},
                'nearest_zone': 'lipetsk_airport',
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 120,
                    'distance': 1450,
                    'approximate': False,
                },
                'position': [39.52449, 52.69810],
                'classes': ['econom', 'business'],
                'metadata': {
                    'airport_queue': {'position': 1, 'queued': QUEUED},
                },
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 100,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.524234, 52.69800],
                'classes': ['econom', 'business'],
                'metadata': {
                    'airport_queue': {'position': 2, 'queued': QUEUED},
                },
            },
            {
                'id': 'dbid2_uuid2',
                'route_info': {
                    'time': 300,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.51453, 52.69891],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.config(DRIVER_SCORING_AIRPORT_SETTINGS={**TEST_AIRPORT_SETTINGS})
async def test_bonus_for_queue_position(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )

    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 3
    assert candidates[0]['id'] == 'dbid0_uuid0'
    assert candidates[0]['score'] == 180.0
    assert candidates[1]['id'] == 'dbid1_uuid1'
    assert candidates[1]['score'] == 220.0
    assert candidates[2]['id'] == 'dbid2_uuid2'
    assert candidates[2]['score'] == 300.0
