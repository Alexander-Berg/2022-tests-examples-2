async def test_ping(taxi_territories_client):
    response = await taxi_territories_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
