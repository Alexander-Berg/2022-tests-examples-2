async def test_child_chair(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.559667, 55.685688]},
        ],
    )
    request_body = {
        'tl': [37.308020, 55.903174],
        'br': [37.921881, 55.565338],
        'allowed_classes': ['econom', 'vip'],
        'zone_id': 'moscow',
        'requirements': {'childchair': True},
    }
    response = await taxi_candidates.post('count', json=request_body)
    assert response.status_code == 200
    assert 'total' in response.json()
    assert response.json()['total'] == 1  # dbid0_uuid0
