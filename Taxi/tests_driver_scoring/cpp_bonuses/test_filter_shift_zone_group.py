import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.parametrize(
    'request_shift,expected_ids',
    [
        (None, ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2']),
        (
            {
                'type': 'unknown',
                'zone_group': {'required_ids': ['123'], 'allow_missing': True},
            },
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {'type': 'eats'},
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'eats',
                'zone_group': {'required_ids': [], 'allow_missing': True},
            },
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'eats',
                'zone_group': {
                    'required_ids': ['123'],
                    'allow_missing': False,
                },
            },
            ['dbid0_uuid0', 'dbid0_uuid3', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'eats',
                'zone_group': {'required_ids': ['123'], 'allow_missing': True},
            },
            ['dbid0_uuid0', 'dbid0_uuid3', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'eats',
                'zone_group': {
                    'required_ids': ['123', '1234'],
                    'allow_missing': True,
                },
            },
            ['dbid0_uuid0', 'dbid0_uuid2', 'dbid0_uuid3', 'dbid0_uuid1'],
        ),
    ],
)
async def test_filter_eats_shift_zone_group(
        taxi_driver_scoring, request_shift, expected_ids,
):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.52449, 52.69810]}},
                },
                'allowed_classes': ['eda'],
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
                    'classes': ['eda'],
                    'eats_shift': {'zone_group_id': '123'},
                },
                {
                    'id': 'dbid0_uuid1',
                    'route_info': {
                        'time': 651,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52321, 52.69234],
                    'classes': ['eda'],
                    'eats_shift': {'no': 'zone'},
                },
                {
                    'id': 'dbid0_uuid2',
                    'route_info': {
                        'time': 652,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['eda'],
                    'eats_shift': {'zone_group_id': '1234'},
                },
                {
                    'id': 'dbid0_uuid3',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['eda'],
                    # no shift
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    if request_shift:
        body['request']['search']['order']['request']['shift'] = request_shift

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200
    actual_ids = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert actual_ids == expected_ids


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.parametrize(
    'request_shift,expected_ids',
    [
        (None, ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2']),
        (
            {
                'type': 'unknown',
                'zone_group': {'required_ids': ['123'], 'allow_missing': True},
            },
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {'type': 'grocery'},
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'grocery',
                'zone_group': {'required_ids': [], 'allow_missing': True},
            },
            ['dbid0_uuid3', 'dbid0_uuid0', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'grocery',
                'zone_group': {
                    'required_ids': ['123'],
                    'allow_missing': False,
                },
            },
            ['dbid0_uuid0', 'dbid0_uuid3', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'grocery',
                'zone_group': {'required_ids': ['123'], 'allow_missing': True},
            },
            ['dbid0_uuid0', 'dbid0_uuid3', 'dbid0_uuid1', 'dbid0_uuid2'],
        ),
        (
            {
                'type': 'grocery',
                'zone_group': {
                    'required_ids': ['123', '1234'],
                    'allow_missing': True,
                },
            },
            ['dbid0_uuid0', 'dbid0_uuid2', 'dbid0_uuid3', 'dbid0_uuid1'],
        ),
    ],
)
async def test_filter_grocery_shift_zone_group(
        taxi_driver_scoring, request_shift, expected_ids,
):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.52449, 52.69810]}},
                },
                'allowed_classes': ['lavka'],
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
                    'classes': ['lavka'],
                    'grocery_shift': {'zone_group_id': '123'},
                },
                {
                    'id': 'dbid0_uuid1',
                    'route_info': {
                        'time': 651,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52321, 52.69234],
                    'classes': ['lavka'],
                    'grocery_shift': {'no': 'zone'},
                },
                {
                    'id': 'dbid0_uuid2',
                    'route_info': {
                        'time': 652,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['lavka'],
                    'grocery_shift': {'zone_group_id': '1234'},
                },
                {
                    'id': 'dbid0_uuid3',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['lavka'],
                    # no shift
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    if request_shift:
        body['request']['search']['order']['request']['shift'] = request_shift

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200
    actual_ids = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert actual_ids == expected_ids
