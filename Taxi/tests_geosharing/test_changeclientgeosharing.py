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


@pytest.mark.parametrize('code', [200, 404, 409, 500])
async def test_changeclientgeosharing(taxi_geosharing, mockserver, code):
    @mockserver.json_handler('/order-core/v1/tc/change-client-geo-sharing')
    def upstream(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        if code != 200:
            return mockserver.make_response(
                '{"code":"CODE","message": "MSG"}', status=code,
            )
        return {
            'result': {
                'change_id': 'some change id',
                'status': 'something',
                'client_status': 'success',
                'name': 'client_geo_sharing',
                'last_orders_modified': '2018-08-22T18:51:25+0300',
            },
        }

    request = {
        'orderid': 'some order id',
        'created_time': '2018-08-22T18:51:25+0300',
        'id': USER_ID,
        'client_geo_sharing_enabled': True,
    }
    response = await taxi_geosharing.post(
        '3.0/changeclientgeosharing', request, headers=PA_HEADERS,
    )
    assert upstream.has_calls
    assert response.status_code == code
    if code == 200:
        assert response.json() == {
            'change_id': 'some change id',
            'name': 'client_geo_sharing',
            'status': 'success',
            'value': True,
        }
        last_modified = response.headers['Last-Orders-Modified']
        assert last_modified == '2018-08-22T15:51:25+0000'
    elif code == 500:
        assert response.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }
    else:
        assert response.json() == {'code': 'CODE', 'message': 'MSG'}
