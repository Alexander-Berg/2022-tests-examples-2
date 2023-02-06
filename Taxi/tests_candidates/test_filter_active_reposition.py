import pytest


@pytest.mark.parametrize(
    'request_override,' 'expected_drivers',
    [
        (
            {
                'order': {
                    'request': {
                        'source': {'geopoint': [55, 35]},
                        'destinations': [
                            {'geopoint': [55, 35.01]},
                            {'geopoint': [55, 35.02]},
                            {'geopoint': [55, 35.03]},
                        ],
                    },
                },
            },
            ['uuid0', 'uuid1'],
        ),
    ],
)
async def test_active_reposition_has_destinaion(
        taxi_candidates,
        driver_positions,
        request_override,
        expected_drivers,
        mock_reposition_index,
):
    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid0',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': True,
            },
            {
                'driver_id': 'uuid1',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': False,
            },
        ],
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['efficiency/active_reposition'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    request_body.update(request_override)

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    drivers = set(d['uuid'] for d in response.json()['drivers'])
    assert sorted(drivers) == expected_drivers


@pytest.mark.parametrize(
    'request_override,' 'expected_drivers', [({'order': {}}, ['uuid1'])],
)
async def test_active_reposition_no_destination(
        taxi_candidates,
        driver_positions,
        request_override,
        expected_drivers,
        mock_reposition_index,
):
    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid0',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': True,
            },
            {
                'driver_id': 'uuid1',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': False,
            },
        ],
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['efficiency/active_reposition'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    request_body.update(request_override)

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    drivers = set(d['uuid'] for d in response.json()['drivers'])
    assert sorted(drivers) == expected_drivers
