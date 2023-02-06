# pylint: disable=invalid-name
async def test_ping(taxi_billing_buffer_proxy_client):
    response = await taxi_billing_buffer_proxy_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
