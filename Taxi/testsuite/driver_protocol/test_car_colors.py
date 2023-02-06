import pytest


@pytest.fixture(scope='function', autouse=True)
def parks_client(mockserver, load_json):
    @mockserver.json_handler('/parks/car-colors')
    def car_colors(request):
        return load_json('car_colors.json')


@pytest.mark.config(CAR_CACHE_COLORS_UPDATE_ENABLED=True)
def test_car_colors(
        taxi_driver_protocol,
        parks_client,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.get(
        '/driver/car/colors',
        params={'db': '777', 'session': 'session_1'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('expected_response.json')
    response_json['colors'] = sorted(
        response_json['colors'], key=lambda x: x['id'],
    )
    expected_response['colors'] = sorted(
        expected_response['colors'], key=lambda x: x['id'],
    )
    assert response_json == expected_response
