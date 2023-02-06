async def test_ping(support_info_client):
    response = await support_info_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
