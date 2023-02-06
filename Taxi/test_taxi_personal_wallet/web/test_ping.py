async def test_ping(test_wallet_client, client_experiments3):
    response = await test_wallet_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
