async def test_ping(taxi_driver_support_client):
    response = await taxi_driver_support_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
