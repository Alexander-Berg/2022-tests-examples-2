import pytest


@pytest.mark.parametrize(
    [
        'service',
        'flavor',
        'upstream_resp_code',
        'upstream_times_called',
        'expected_resp_code',
        'expected_resp',
    ],
    [
        ('taxi', None, 204, {'ridehistory': 1}, 200, {}),
        (
            'taxi',
            None,
            404,
            {'ridehistory': 1},
            404,
            {'code': 'ORDER_NOT_FOUND', 'message': 'No such order'},
        ),
        (
            'taxi',
            None,
            500,
            {'ridehistory': 1},
            500,
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {
                    'reason': (
                        'ridehistory response, status: 500, body: '
                        'Error(code=\'ridehistory_code\', '
                        'message=\'ridehistory_message\')'
                    ),
                },
                'message': 'Internal server error',
            },
        ),
        ('taxi', 'delivery', 200, {'cargo_c2c': 1}, 200, {}),
        (
            'taxi',
            'delivery',
            404,
            {'cargo_c2c': 1},
            404,
            {'code': 'ORDER_NOT_FOUND', 'message': 'No such order'},
        ),
        (
            'taxi',
            'delivery',
            500,
            {'cargo_c2c': 1},
            500,
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {
                    'reason': (
                        'Not defined in schema cargo-c2c response, '
                        'status: 500, body: b\'{"code": "cargo_c2c_code", '
                        '"message": "cargo_c2c_message"}\''
                    ),
                },
                'message': 'Internal server error',
            },
        ),
        ('delivery', None, 200, {'cargo_c2c': 1}, 200, {}),
        (
            'delivery',
            None,
            404,
            {'cargo_c2c': 1},
            404,
            {'code': 'ORDER_NOT_FOUND', 'message': 'No such order'},
        ),
        (
            'delivery',
            None,
            500,
            {'cargo_c2c': 1},
            500,
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {
                    'reason': (
                        'Not defined in schema cargo-c2c response, '
                        'status: 500, body: b\'{"code": "cargo_c2c_code", '
                        '"message": "cargo_c2c_message"}\''
                    ),
                },
                'message': 'Internal server error',
            },
        ),
    ],
)
async def test_remove(
        taxi_orderhistory_web,
        mockserver,
        mock_ridehistory,
        mock_cargo_c2c,
        service,
        flavor,
        upstream_resp_code,
        upstream_times_called,
        expected_resp_code,
        expected_resp,
):
    @mock_ridehistory('/v2/remove')
    async def handler_ridehistory(request):
        assert request.headers['X-Yandex-UID'] == 'uid0'

        if upstream_resp_code == 204:
            return mockserver.make_response(status=204)

        return mockserver.make_response(
            status=upstream_resp_code,
            json={
                'code': 'ridehistory_code',
                'message': 'ridehistory_message',
            },
        )

    @mock_cargo_c2c('/orderhistory/v1/remove')
    async def handler_cargo_c2c(request):
        assert request.headers['X-Yandex-UID'] == 'uid0'

        if upstream_resp_code == 200:
            return mockserver.make_response(status=200, json={})

        return mockserver.make_response(
            status=upstream_resp_code,
            json={'code': 'cargo_c2c_code', 'message': 'cargo_c2c_message'},
        )

    request_params = {'service': service, 'order_id': '777'}
    if flavor:
        request_params['flavor'] = flavor

    response = await taxi_orderhistory_web.delete(
        '/4.0/orderhistory/v2/remove',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android,app_brand=some_brand',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        params=request_params,
    )

    assert response.status == expected_resp_code
    assert await response.json() == expected_resp

    assert handler_ridehistory.times_called == upstream_times_called.get(
        'ridehistory', 0,
    )
    assert handler_cargo_c2c.times_called == upstream_times_called.get(
        'cargo_c2c', 0,
    )


@pytest.mark.parametrize(
    ['resp_code', 'expected_resp'],
    [
        (200, {}),
        (404, {'code': 'ORDER_NOT_FOUND', 'message': 'No such order'}),
    ],
)
async def test_remove_shuttle(
        taxi_orderhistory_web, mockserver, resp_code, expected_resp,
):
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/remove',
    )
    async def handler_shuttle_control(request):
        assert request.json == {'order_id': '777'}
        if resp_code == 200:
            return mockserver.make_response(status=200, json={})

        return mockserver.make_response(
            status=resp_code,
            json={'code': '404', 'message': 'There is no such order'},
        )

    request_params = {'service': 'shuttle', 'order_id': '777'}
    response = await taxi_orderhistory_web.delete(
        '/4.0/orderhistory/v2/remove',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android,app_brand=some_brand',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        params=request_params,
    )

    assert response.status == resp_code
    assert await response.json() == expected_resp

    assert handler_shuttle_control.times_called == 1
