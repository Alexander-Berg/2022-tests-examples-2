async def test_filter_configs(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/driver_id'],
        'point': [37.625344, 55.755430],
        'zone_id': 'moscow',
        'excluded_ids': ['clid0_uuid0'],
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert response.json()['drivers']
