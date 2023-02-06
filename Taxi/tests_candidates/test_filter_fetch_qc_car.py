async def test_block_if_no_qc_info(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/fetch_qc_car'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 1
