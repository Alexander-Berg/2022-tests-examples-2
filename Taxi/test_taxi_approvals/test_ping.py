async def test_ping(taxi_approvals_client):
    response = await taxi_approvals_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
