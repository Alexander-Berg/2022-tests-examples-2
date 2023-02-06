async def test_hello(monitoring_client):
    response = await monitoring_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
