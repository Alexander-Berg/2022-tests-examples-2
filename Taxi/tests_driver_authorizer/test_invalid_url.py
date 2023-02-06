async def test_nonexisting_url(taxi_driver_authorizer):
    response = await taxi_driver_authorizer.get('nonexisting')
    assert response.status_code == 404
    assert response.content == b''
