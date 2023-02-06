async def test_ping(scripts_client):
    response = await scripts_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
