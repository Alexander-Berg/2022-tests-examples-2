import pytest


@pytest.fixture
def weather_service_clear(mockserver):
    @mockserver.json_handler('/data/2.5/weather')
    def mock_get_weather(request):
        return {
            'coord': {'lon': 37.616667, 'lat': 55.75},
            'weather': [
                {
                    'id': 800,
                    'main': 'Clear',
                    'description': 'clear sky',
                    'icon': '01d',
                },
            ],
            'base': 'stations',
            'main': {
                'temp': 311.258,
                'pressure': 960.1,
                'humidity': 19,
                'temp_min': 311.258,
                'temp_max': 311.258,
                'sea_level': 1016.51,
                'grnd_level': 960.1,
            },
            'wind': {'speed': 2.31, 'deg': 66.0012},
            'clouds': {'all': 0},
            'dt': 1499172066,
            'sys': {
                'message': 0.0603,
                'country': 'IR',
                'sunrise': 1499130056,
                'sunset': 1499182914,
            },
            'id': 129512,
            'name': 'Kalaleh',
            'cod': 200,
        }


def test_weathersuggest_simple(taxi_protocol, weather_service_clear):
    response = taxi_protocol.post(
        '3.0/weathersuggest', {'ll': [37.58790291786, 55.73422146890]},
    )
    assert response.status_code == 200

    data = response.json()
    assert data == {}


def test_weathersuggest_empty_data(taxi_protocol, weather_service_clear):

    response = taxi_protocol.post('3.0/weathersuggest', {})
    assert response.status_code == 400


def test_weathersuggest_incorrect_data(taxi_protocol, weather_service_clear):

    response = taxi_protocol.post(
        '3.0/weathersuggest', {'some_field': 'some_data'},
    )
    assert response.status_code == 400


@pytest.fixture
def weather_service_snow(mockserver):
    @mockserver.json_handler('/data/2.5/weather')
    def mock_get_weather(request):
        return {
            'coord': {'lon': 37.616667, 'lat': 55.75},
            'weather': [
                {
                    'id': 601,
                    'main': 'Snow',
                    'description': 'Snow',
                    'icon': '01d',
                },
            ],
            'base': 'stations',
            'main': {
                'temp': 311.258,
                'pressure': 960.1,
                'humidity': 19,
                'temp_min': 311.258,
                'temp_max': 311.258,
                'sea_level': 1016.51,
                'grnd_level': 960.1,
            },
            'wind': {'speed': 2.31, 'deg': 66.0012},
            'clouds': {'all': 0},
            'dt': 1499172066,
            'sys': {
                'message': 0.0603,
                'country': 'IR',
                'sunrise': 1499130056,
                'sunset': 1499182914,
            },
            'id': 129512,
            'name': 'Kalaleh',
            'cod': 200,
        }


def test_weathersuggest_snow(taxi_protocol, weather_service_snow):
    response = taxi_protocol.post(
        '3.0/weathersuggest', {'ll': [37.58790291786, 55.73422146890]},
    )
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'base_weather_code': 'snow',
        'message': (
            'Due to heavy snow, the demand for '
            'taxi services is higher than usual.'
        ),
    }


@pytest.mark.now('2017-07-20T11:30:00+0300')
@pytest.mark.redis_store(
    [
        'hset',
        'weather_positions',
        'ucftp',
        '{"code":601,"timestamp":"2017-07-20T11:36:30+0000"}',
    ],
)
def test_weathersuggest_redis(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/weathersuggest', {'ll': [37.58790291786, 55.73422146890]},
    )
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'base_weather_code': 'snow',
        'message': (
            'Due to heavy snow, the demand for taxi '
            'services is higher than usual.'
        ),
    }
