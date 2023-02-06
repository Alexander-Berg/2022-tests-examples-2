import pytest


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                CANDIDATES_USE_V2_CHAIN_BUSY_DRIVERS_BULK=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CANDIDATES_USE_V2_CHAIN_BUSY_DRIVERS_BULK=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'chain_classes, found_drivers, skipped_drivers',
    [
        (
            {'__default__': {'__default__': True}},
            ['dbid1_uuid3', 'dbid0_uuid2'],
            [],
        ),
        (
            {
                '__default__': {'__default__': True},
                'moscow': {'__default__': False},
            },
            [],
            ['dbid1_uuid3', 'dbid0_uuid2'],
        ),
        (
            {
                '__default__': {'__default__': True},
                'moscow': {'__default__': True, 'vip': False},
            },
            ['dbid1_uuid3'],
            ['dbid0_uuid2'],
        ),
    ],
)
async def test_filter_fetch_chain_classes(
        chain_classes,
        found_drivers,
        skipped_drivers,
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        taxi_config,
):
    taxi_config.set_values(
        dict(CANDIDATES_FILTER_FETCH_CHAIN_CLASSES=chain_classes),
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'destination': [37.625344, 55.755430],
                'left_distance': 100,
                'left_time': 100,
            },
            {
                'driver_id': 'dbid1_uuid3',
                'destination': [37.625129, 55.757644],
                'left_distance': 10,
                'left_time': 10,
            },
        ],
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [37.625033, 55.761528]},
        ],
    )

    request_body = {
        'limit': 10,
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_route_distance': 100000,
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    response_json = response.json()
    assert 'drivers' in response_json
    drivers = [
        '{}_{}'.format(driver['dbid'], driver['uuid'])
        for driver in response_json['drivers']
    ]
    assert all(driver in drivers for driver in found_drivers)
    assert not any(driver in drivers for driver in skipped_drivers)


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_chain_settings(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        taxi_config,
        dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'ORDER_CHAIN_MAX_LINE_DISTANCE': 2000,
                            'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 3000,
                            'ORDER_CHAIN_MAX_ROUTE_TIME': 300,
                            'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        },
                    },
                ],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'vip',
                'parameters': [
                    {
                        'values': {
                            'ORDER_CHAIN_MAX_LINE_DISTANCE': 20,
                            'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 30,
                            'ORDER_CHAIN_MAX_ROUTE_TIME': 300,
                            'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        },
                    },
                ],
            },
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'destination': [37.625344, 55.755430],
                'left_distance': 100,
                'left_time': 100,
            },
        ],
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid2', 'position': [37.625129, 55.757644]}],
    )

    body = {
        'driver_ids': [{'uuid': 'uuid2', 'dbid': 'dbid0'}],
        'allowed_classes': ['econom', 'vip'],
        'order_id': 'test-order-1',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200
    filters = response.json()['drivers'][0]['details'][
        'efficiency/fetch_chain_classes'
    ]
    assert len(filters) == 1
    assert filters[0] == 'vip by chain settings'
