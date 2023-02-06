async def test_enumerate(web_app_client, mockserver, load_json):
    await web_app_client.post(
        '/new-consumer/register/',
        json={
            'service_balancer_hostname': 'new-service',
            'service_tvm_name': 'new-service',
        },
    )

    response = await web_app_client.get('/enumerate_consumers')
    assert response.status == 200
    data = await response.json()
    assert data == ['eda-surge', 'new-consumer', 'taxi-surge']
