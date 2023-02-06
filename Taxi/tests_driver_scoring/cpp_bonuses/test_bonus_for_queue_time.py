import datetime

import pytest

import tests_driver_scoring.dispatch_settings as dispatch_settings
import tests_driver_scoring.tvm_tickets as tvm_tickets


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

NOW = datetime.datetime(2020, 5, 18)


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.config(DRIVER_SCORING_AIRPORT_SETTINGS={**TEST_AIRPORT_SETTINGS})
@pytest.mark.dispatch_settings(
    settings=dispatch_settings.get_airport_dispatch_settings(),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('queue_time', [0, 10, 60, 3600])
async def test_bonus_for_queue_time(taxi_driver_scoring, queue_time):
    queued_time = NOW - datetime.timedelta(seconds=queue_time)

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
                    'position': [39.52111, 52.69642],
                    'classes': ['econom', 'business'],
                    'metadata': {
                        'airport_queue': {
                            'class': 'econom',
                            'queued': queued_time.strftime(
                                '%Y-%m-%dT%H:%M:%SZ',
                            ),
                            'position': 0,
                        },
                    },
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 100,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['econom', 'business'],
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

    weight = TEST_AIRPORT_SETTINGS['lipetsk_airport']['econom'][
        'QUEUE_TIME_WEIGHT'
    ]
    expected = -(weight * queue_time)

    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 2
    assert candidates[0]['id'] == 'dbid0_uuid0'
    assert candidates[0]['score'] == expected
    assert candidates[1]['id'] == 'dbid1_uuid1'
    assert candidates[1]['score'] == 100.0
