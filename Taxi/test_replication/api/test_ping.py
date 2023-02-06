async def test_ping(replication_client):
    response = await replication_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
