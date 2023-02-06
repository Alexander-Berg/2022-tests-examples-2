async def test_pong(scripts_client):
    response = await scripts_client.get('/pong')
    assert response.status == 200
    content = await response.text()
    assert content == ''
