async def test_ping(taxi_corp_admin_client):
    response = await taxi_corp_admin_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
