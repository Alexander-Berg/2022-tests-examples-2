async def test_ping(billing_subventions_client):
    response = await billing_subventions_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
