import datetime

import pytest

import tests_driver_scoring.dispatch_settings as dispatch_settings
import tests_driver_scoring.tvm_tickets as tvm_tickets


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
                    'time': 650,
                    'distance': 1450,
                    'approximate': False,
                },
                'position': [39.51992, 52.68912],
                'classes': ['econom', 'business'],
                'metadata': {
                    'airport_queue': {
                        'position': 1,
                        'class': 'econom',
                        'queued': '2020-05-17T23:58:00+00:00',
                    },
                },
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 124,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.50992, 52.67999],
                'classes': ['econom', 'business'],
                'metadata': {
                    'airport_queue': {
                        'position': 2,
                        'class': 'econom',
                        'queued': '2020-05-17T23:59:00Z',
                    },
                },
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

NOW = datetime.datetime(2020, 5, 18)


@pytest.mark.experiments3(filename='airport_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'weights,queue_position,queue_time,expected',
    [
        (
            {
                'ALPHA': 0.5,
                'BETA': 0.1,
                'QUEUE_POSITION_WEIGHT': 50,
                'QUEUE_TIME_WEIGHT': 2,
            },
            1,
            60,
            327.5,
        ),
        (
            {
                'ALPHA': 0.2,
                'BETA': 0.3,
                'QUEUE_POSITION_WEIGHT': 20,
                'QUEUE_TIME_WEIGHT': 3,
            },
            2,
            120,
            287,
        ),
        (
            {
                'ALPHA': 0.7,
                'BETA': 0.6,
                'QUEUE_POSITION_WEIGHT': 70,
                'QUEUE_TIME_WEIGHT': 5,
            },
            3,
            150,
            264,
        ),
    ],
)
@pytest.mark.dispatch_settings(
    settings=dispatch_settings.get_airport_dispatch_settings(),
)
async def test_driver_scoring_airport(
        taxi_driver_scoring,
        taxi_config,
        weights,
        queue_position,
        queue_time,
        expected,
):
    taxi_config.set_values(
        dict(
            DRIVER_SCORING_AIRPORT_SETTINGS={
                'lipetsk_airport': {
                    'econom': {
                        **weights,
                        **{
                            'MAX_ROBOT_TIME_SCORE_ENABLED': False,
                            'MAX_ROBOT_TIME_SCORE': 0,
                        },
                    },
                },
            },
        ),
    )

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
                    'position': [39.52484, 52.68810],
                    'classes': ['econom', 'business'],
                    'metadata': {
                        'airport_queue': {
                            'position': queue_position,
                            'class': 'econom',
                            'queued': queued_time.strftime(
                                '%Y-%m-%dT%H:%M:%SZ',
                            ),
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
    assert len(candidates) == 1
    assert candidates[0]['score'] == expected


@pytest.mark.experiments3(filename='airport_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.dispatch_settings(
    settings=dispatch_settings.get_airport_dispatch_settings(
        dispatch_max_positive_bonus_seconds=599,
        dispatch_min_negative_bonus_seconds=-59,
    ),
)
async def test_driver_scoring_airport_non_airport_order(
        taxi_driver_scoring, taxi_config,
):
    taxi_config.set_values(
        dict(
            DRIVER_SCORING_AIRPORT_SETTINGS={
                'lipetsk_airport': {
                    'econom': {
                        'ALPHA': 1,
                        'BETA': 0,
                        'QUEUE_POSITION_WEIGHT': 30,
                        'QUEUE_TIME_WEIGHT': 5,
                        'MAX_ROBOT_TIME_SCORE_ENABLED': False,
                        'MAX_ROBOT_TIME_SCORE': 0,
                    },
                },
            },
        ),
    )

    body = BODY
    body['request']['search']['order']['request']['source']['geopoint'] = [
        39.82449,
        52.98102,
    ]

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )

    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 2
    assert candidates[0]['id'] == 'dbid1_uuid1'
    assert candidates[0]['score'] == 124
    assert candidates[1]['id'] == 'dbid0_uuid0'
    assert candidates[1]['score'] == 650
