async def test_ping(taxi_billing_orders_client):
    response = await taxi_billing_orders_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
