async def test_ping(taxi_driver_metrics):
    response = await taxi_driver_metrics.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
