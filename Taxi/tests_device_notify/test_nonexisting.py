async def test_nonexisting_url(taxi_device_notify):
    response = await taxi_device_notify.get('nonexisting')
    assert response.status_code == 404
    assert response.content == b''
