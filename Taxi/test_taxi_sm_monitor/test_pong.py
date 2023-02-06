async def test_pong(taxi_sm_monitor_client):
    response = await taxi_sm_monitor_client.get('/pong')
    assert response.status == 200
    content = await response.text()
    assert content == ''
