async def test_start_and_stop_handelrs(taxi_corp_auth_client):
    await taxi_corp_auth_client.post(
        '/1.0/tracemalloc/start', json={'nframe': 5},
    )
    response = await taxi_corp_auth_client.get('/1.0/tracemalloc/status')

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['status'] == 'enabled'

    await taxi_corp_auth_client.post('/1.0/tracemalloc/stop')
    response = await taxi_corp_auth_client.get('/1.0/tracemalloc/status')

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['status'] == 'disabled'


async def test_take_snapshot_handler(taxi_corp_auth_client):
    await taxi_corp_auth_client.post(
        '/1.0/tracemalloc/start', json={'nframe': 1},
    )
    response = await taxi_corp_auth_client.post('/1.0/tracemalloc/snapshot')
    assert response.status == 200
