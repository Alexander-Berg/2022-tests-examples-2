async def test_status_searchable(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 10,
                'left_distance': 10,
                'destination': [55, 35],
                'approximate': False,
            },
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/meta_status_searchable'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2


async def test_status_searchable_one(
        taxi_candidates, driver_positions, chain_busy_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 1000,
                'left_distance': 1000,
                'destination': [0.0, 0.0],
                'approximate': False,
            },
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/meta_status_searchable'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 1
