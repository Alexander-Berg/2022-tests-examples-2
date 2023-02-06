async def test_pong(taxi_exp_client):
    response = await taxi_exp_client.get('/pong')
    assert response.status == 200
    content = await response.text()
    assert content == ''
