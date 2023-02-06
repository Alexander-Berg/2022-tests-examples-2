async def test_serializer(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'driver_ids': ['dbid0_uuid0'],
        'zone_id': 'moscow',
        'data_keys': ['car_id'],
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert drivers[0]['car_id'] == 'car_id0'
