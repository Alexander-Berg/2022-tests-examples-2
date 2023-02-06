async def test_ping(taxi_exp_client):
    response = await taxi_exp_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
