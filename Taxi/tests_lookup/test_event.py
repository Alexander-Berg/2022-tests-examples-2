async def test_event_200(taxi_lookup):
    response = await taxi_lookup.post(
        'v2/event',
        params={'order_id': 'id1', 'generation': 1, 'version': 1, 'wave': 1},
        json={'status': 'aborted'},
    )
    body = response.json()
    assert (response.status_code, body) == (200, {'success': False})


async def test_event_400(taxi_lookup):
    response = await taxi_lookup.post(
        'v2/event',
        params={'order_id': 'id1', 'generation': 1, 'version': 1, 'wave': 1},
        json={},
    )
    body = response.json()
    assert response.status_code == 400
    assert body['code'] == '400'

    response = await taxi_lookup.post(
        'v2/event', params={'order_id': 'id1'}, json={'status': 'aborted'},
    )
    body = response.json()
    assert response.status_code == 400
    assert body['code'] == '400'
