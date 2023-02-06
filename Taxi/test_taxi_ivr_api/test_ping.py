async def test_ping(ivr_api_client):
    response = await ivr_api_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == '{}'
