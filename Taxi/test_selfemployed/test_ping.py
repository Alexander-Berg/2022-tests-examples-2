async def test_ping(se_client):
    response = await se_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
