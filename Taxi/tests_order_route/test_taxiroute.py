import pytest


REQUIRED_HEADERS = {
    'User-Agent': 'some_agent',
    'Accept-Language': 'en',
    'X-Remote-IP': '1.2.3.4',
}
DEFAULT_HEADERS = {
    'X-YaTaxi-PhoneId': 'phone_pd_id',
    'X-YaTaxi-UserId': 'some_user_id',
    'X-Yandex-UID': 'yandex_uid',
    'X-Request-Language': 'en',
}
DEFAULT_HEADERS.update(REQUIRED_HEADERS)
DEFAULT_REQUEST = {
    'id': 'user_id',
    'orderid': 'order_id',
    'authkey': 'authkey',
    'timestamp': 'timestamp',
    'coordinates': [1, 2],
    'use_history': True,
    'float_timestamp': True,
    'build_route': False,
}


@pytest.mark.parametrize(
    'protocol_status_code, expected_status_code',
    [
        pytest.param('200', 200, id='ok'),
        pytest.param('304', 304, id='not_modified'),
        pytest.param('400', 400, id='bad'),
        pytest.param('401', 401, id='unauth'),
        pytest.param('404', 404, id='not_found'),
        pytest.param('network', 500, id='network_error'),
        pytest.param('timeout', 500, id='timeout_error'),
    ],
)
async def test_proxy(
        taxi_order_route,
        mockserver,
        protocol_status_code,
        expected_status_code,
):
    @mockserver.json_handler('protocol-order-route/3.0/taxiroute')
    def _mock_protocol_taxiroute(request):
        for key, value in REQUIRED_HEADERS.items():
            assert request.headers[key] == value
        assert request.json == DEFAULT_REQUEST
        if protocol_status_code == 'network':
            raise mockserver.NetworkError()
        if protocol_status_code == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=int(protocol_status_code), json={'any': 'json'},
        )

    response = await taxi_order_route.post(
        '/3.0/taxiroute', json=DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == expected_status_code
    assert _mock_protocol_taxiroute.times_called == 1
    if protocol_status_code in ['network', 'timeout']:
        assert response.json() == {'error': {'text': 'Internal server error'}}
    elif protocol_status_code == '304':
        return
    else:
        assert response.json() == {'any': 'json'}
