async def test_ping(taxi_billing_calculators_client):
    response = await taxi_billing_calculators_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
