async def test_pong(taxi_territories_client):
    response = await taxi_territories_client.get('/pong')
    assert response.status == 200
    content = await response.text()
    assert content == ''
