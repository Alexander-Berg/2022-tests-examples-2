import pytest

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-Ya-User-Ticket': 'user_ticket',
}


async def test_clientgeo_bad_request(taxi_geosharing):
    response = await taxi_geosharing.post(
        '3.0/clientgeo', {'key': 'request_body_malformed'}, headers=PA_HEADERS,
    )
    assert response.status_code == 400


async def test_clientgeo_disabled(mockserver, taxi_geosharing):
    response = await taxi_geosharing.post(
        '3.0/clientgeo',
        {
            'id': USER_ID,
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'enabled': False}


@pytest.mark.experiments3(filename='exp3_enable_geosharing.json')
async def test_clientgeo_enabled(mockserver, taxi_geosharing):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/user-tracker/user/position/store')
    def position_store(request):
        assert request.args['sync'] == '0'
        assert request.args['accuracy'] == '5'
        assert request.args['lat'] == '55.000000'
        assert request.args['lon'] == '37.000000'
        assert request.args['timestamp'] == '1534953085'
        assert request.args['user_id'] == USER_ID
        return {}

    response = await taxi_geosharing.post(
        '3.0/clientgeo',
        {
            'id': USER_ID,
            'geo_position': {
                'lon': 37.0,
                'lat': 55.0,
                'accuracy': 5.0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
        headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'clientgeo_disable_distance': 900.0,
        'enabled': True,
        'false_count': 10,
        'request': {'max_requests': 3, 'show': True, 'version': 'v1.0'},
        'track_in_background': False,
        'tracking_rate_battery_state': {'empty': 30, 'full': 10, 'half': 20},
    }
