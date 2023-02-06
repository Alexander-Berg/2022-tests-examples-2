async def test_no_multioffers(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/multioffer_orders'],
        'point': [55, 35],
        'order': {'id': 'bla-bla-bla'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2


async def test_filter_by_multioffer(
        taxi_candidates, driver_positions, contractor_orders_multioffer,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    contractor_orders_multioffer(
        [
            {
                'drivers': [
                    {'driver_profile_id': 'uuid0', 'park_id': 'dbid0'},
                    {'driver_profile_id': 'uuid2', 'park_id': 'dbid0'},
                ],
                'order_id': 'bla-bla-bla',
            },
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/multioffer_orders'],
        'point': [55, 35],
        'order_id': 'bla-bla-bla',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 1


async def test_non_filter_by_another_order(
        taxi_candidates, driver_positions, contractor_orders_multioffer,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    contractor_orders_multioffer(
        [
            {
                'drivers': [
                    {'driver_profile_id': 'uuid0', 'park_id': 'dbid0'},
                    {'driver_profile_id': 'uuid2', 'park_id': 'dbid0'},
                ],
                'order_id': 'one-two-three',
            },
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/multioffer_orders'],
        'point': [55, 35],
        'order': {'id': 'bla-bla-bla'},
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2


async def test_filter_by_multioffer_auction(
        taxi_candidates, driver_positions, contractor_orders_multioffer,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )

    contractor_orders_multioffer(
        [
            {
                'drivers': [
                    {
                        'driver_profile_id': 'uuid0',
                        'park_id': 'dbid0',
                        'auction_iteration': 0,
                    },
                    {
                        'driver_profile_id': 'uuid1',
                        'park_id': 'dbid0',
                        'auction_iteration': 0,
                    },
                    {
                        'driver_profile_id': 'uuid2',
                        'park_id': 'dbid0',
                        'auction_iteration': 0,
                    },
                ],
                'order_id': 'bla-bla-bla',
            },
        ],
    )
    await taxi_candidates.invalidate_caches()

    # Test iterative cache update with auction iterations changes
    contractor_orders_multioffer(
        [
            {
                'drivers': [
                    {
                        'driver_profile_id': 'uuid0',
                        'park_id': 'dbid0',
                        'auction_iteration': 3,
                    },
                    {
                        'driver_profile_id': 'uuid1',
                        'park_id': 'dbid0',
                        'auction_iteration': 3,
                    },
                    {
                        'driver_profile_id': 'uuid1',
                        'park_id': 'dbid0',
                        'auction_iteration': 4,
                    },
                    {
                        'driver_profile_id': 'uuid2',
                        'park_id': 'dbid0',
                        'auction_iteration': 5,
                    },
                ],
                'order_id': 'bla-bla-bla',
            },
        ],
    )
    await taxi_candidates.invalidate_caches(
        clean_update=False, cache_names=['multioffer-orders-cache'],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/multioffer_orders'],
        'point': [55, 35],
        'order_id': 'bla-bla-bla',
        'zone_id': 'moscow',
        'auction': {'iteration': 4},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert response.json()['drivers'] == [
        {'position': [55, 35], 'dbid': 'dbid0', 'uuid': 'uuid0'},
    ]
