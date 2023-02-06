import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

NOW = datetime.datetime(2020, 5, 18)

TEST_AIRPORT_SETTINGS = {
    'lipetsk_airport': {
        'econom': {
            'ALPHA': 1,
            'BETA': 0,
            'QUEUE_POSITION_WEIGHT': 60,
            'QUEUE_TIME_WEIGHT': 3,
            'MAX_ROBOT_TIME_SCORE_ENABLED': False,
            'MAX_ROBOT_TIME_SCORE': 0,
        },
    },
}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.config(DRIVER_SCORING_AIRPORT_SETTINGS={**TEST_AIRPORT_SETTINGS})
@pytest.mark.now(NOW.isoformat())
async def test_bonus_for_queue_time_filter(taxi_driver_scoring):
    body = {
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
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52321, 52.69234],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 60,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52222, 52.69350],
                    'classes': ['econom', 'business'],
                    'metadata': {
                        'airport_queue': {
                            'position': 1,
                            'queued': NOW.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        },
                    },
                },
                {
                    'id': 'dbid3_uuid3',
                    'route_info': {
                        'time': 120,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52222, 52.69350],
                    'classes': ['econom', 'business'],
                    'metadata': {
                        'airport_queue': {
                            'filtered': {'reason': 'user_cancel'},
                        },
                    },
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 4
    assert candidates[0]['id'] == 'dbid2_uuid2'
    assert candidates[0]['score'] == 0.0
    assert candidates[1]['id'] == 'dbid1_uuid1'
    assert candidates[1]['score'] == 124.0
    assert candidates[2]['id'] == 'dbid0_uuid0'
    assert candidates[2]['score'] == 650.0
    assert candidates[3]['id'] == 'dbid3_uuid3'
    assert candidates[3]['score'] == 920.0
