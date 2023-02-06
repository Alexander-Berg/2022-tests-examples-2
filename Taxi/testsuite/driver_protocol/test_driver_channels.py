def test_unathorized(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post('driver/channels')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/channels?db=1488&session=111')
    assert response.status_code == 401


def test_park_not_found(
        taxi_driver_protocol, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('222', 'abc', 'driver')

    response = taxi_driver_protocol.post(
        'driver/channels?db=222&session=abc',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('ParkNotFound.json')


def test_driver_channels(
        taxi_driver_protocol, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/channels?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('AllChannels.json')
