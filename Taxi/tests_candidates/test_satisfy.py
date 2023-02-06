import pytest


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_satisfy(taxi_candidates, driver_positions):
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid1', 'dbid': 'dbid0'},
            {'uuid': 'uuid3', 'dbid': 'dbid1'},
            {'uuid': 'uuid8', 'dbid': 'dbid0'},
        ],
        'allowed_classes': ['econom'],
        'order_id': 'test-order-1',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200
    drivers = sorted(response.json()['drivers'], key=lambda x: x['uuid'])
    # too volatile value
    for driver in drivers:
        del driver['details']

    assert drivers == [
        {'dbid': 'dbid0', 'uuid': 'uuid0', 'is_satisfied': True},
        {
            'dbid': 'dbid0',
            'uuid': 'uuid1',
            'is_satisfied': False,
            'reasons': {'infra/fetch_profile_classes': []},
        },
        {
            'dbid': 'dbid1',
            'uuid': 'uuid3',
            'is_satisfied': False,
            'reasons': {'infra/deactivated_park_v2': []},
        },
        {
            'dbid': 'dbid0',
            'uuid': 'uuid8',
            'is_satisfied': False,
            'reasons': {
                'infra/fetch_position_timestamps': [],
                'infra/meta_status_searchable': [],
                'infra/fetch_driver': [],
            },
        },
    ]


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_satisfy_payment_methods(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid3', 'dbid': 'dbid1'},
        ],
        'allowed_classes': ['econom'],
        'order_id': 'test-order-1',
        'zone_id': 'moscow',
        'payment_methods': ['cash', 'card'],
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200
    drivers = sorted(response.json()['drivers'], key=lambda x: x['uuid'])
    # too volatile value
    for driver in drivers:
        del driver['details']

    assert drivers == [
        {
            'dbid': 'dbid0',
            'uuid': 'uuid0',
            'is_satisfied': False,
            'reasons': {'infra/all_of_payment_methods': []},
        },
        {
            'dbid': 'dbid1',
            'uuid': 'uuid3',
            'is_satisfied': False,
            'reasons': {
                'infra/deactivated_park_v2': [],
                'infra/all_of_payment_methods': [],
            },
        },
    ]
