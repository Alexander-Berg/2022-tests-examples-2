async def test_ping(taxi_sm_monitor_client):
    response = await taxi_sm_monitor_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
