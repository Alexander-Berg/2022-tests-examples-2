import copy

import pytest


DEFAULT_USER_AGENT = 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)'
DEFAULT_HEADERS = {
    'X-Yandex-UID': '999',
    'X-YaTaxi-UserId': 'test_user_id_xxx',
    'User-Agent': DEFAULT_USER_AGENT,
}
TOTW_RESPONSE = {'any': 'json'}


def _build_request(order_count):
    orders = [
        {'orderid': str(idx), 'tag': 'timestamp'} for idx in range(order_count)
    ]
    return {'orders': orders}


@pytest.mark.parametrize('order_count', [0, 1, 2])
async def test_taxi_orders_state(taxi_order_parts, mockserver, order_count):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        assert request.headers['User-Agent'] == DEFAULT_USER_AGENT
        assert request.json['format_currency']
        return TOTW_RESPONSE

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(order_count),
        headers=DEFAULT_HEADERS,
    )
    assert mock_api_proxy.times_called == order_count
    assert response.status == 200
    assert response.json() == {
        'orders': [TOTW_RESPONSE for idx in range(order_count)],
    }


@pytest.mark.parametrize(
    'totw_status_code, totw_response_json',
    [
        (400, {'error': {'text': 'any text'}}),
        (401, {'error': {'text': 'any text'}}),
        (501, None),
        (500, None),
    ],
)
async def test_unavailable(
        taxi_order_parts, mockserver, totw_status_code, totw_response_json,
):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        return mockserver.make_response(
            status=totw_status_code, json=totw_response_json,
        )

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(1),
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 500
    expected_times_call = 2 if totw_status_code >= 500 else 1
    assert mock_api_proxy.times_called == expected_times_call


@pytest.mark.parametrize(
    'totw_status_code, totw_response_json, expected_update_status',
    [(404, {'error': {'text': 'any text'}}, 'expired'), (500, None, 'stale')],
)
async def test_error_handling(
        taxi_order_parts,
        mockserver,
        totw_status_code,
        totw_response_json,
        expected_update_status,
):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        if request.json['orderid'] == '1':
            return mockserver.make_response(
                status=totw_status_code, json=totw_response_json,
            )
        return TOTW_RESPONSE

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(order_count=2),
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    assert response.json() == {
        'orders': [
            TOTW_RESPONSE,
            {'error': {'update_status': expected_update_status}},
        ],
    }
    expected_times_call = 2 if totw_status_code == 404 else 3
    assert mock_api_proxy.times_called == expected_times_call


async def test_timeout(taxi_order_parts, mockserver):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        if request.json['orderid'] == '1':
            raise mockserver.TimeoutError()
        return TOTW_RESPONSE

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(order_count=2),
        headers=DEFAULT_HEADERS,
    )

    assert mock_api_proxy.times_called == 3
    assert response.status == 200
    assert response.json() == {
        'orders': [TOTW_RESPONSE, {'error': {'update_status': 'stale'}}],
    }


async def test_network_problem(taxi_order_parts, mockserver):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        if request.json['orderid'] == '1':
            raise mockserver.NetworkError()
        return TOTW_RESPONSE

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(order_count=2),
        headers=DEFAULT_HEADERS,
    )

    assert mock_api_proxy.times_called == 3
    assert response.status == 200
    assert response.json() == {
        'orders': [TOTW_RESPONSE, {'error': {'update_status': 'stale'}}],
    }


async def test_proxy_request(taxi_order_parts, mockserver):
    payload = {'supported': ['feature']}

    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        for key, value in payload.items():
            assert request.json[key] == value
        assert request.json['orderid'] == 'id'
        return {}

    request = copy.deepcopy(payload)
    request['orders'] = [{'orderid': 'id', 'tag': 'timestamp'}]
    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=request,
        headers=DEFAULT_HEADERS,
    )
    assert mock_api_proxy.times_called == 1
    assert response.status == 200


@pytest.mark.parametrize(
    'order_count, call_count, expected_code', [(3, 3, 200), (4, 0, 400)],
)
async def test_received_order_limit(
        taxi_order_parts, mockserver, order_count, call_count, expected_code,
):
    @mockserver.json_handler('/api-proxy-critical/3.0/taxiontheway')
    def mock_api_proxy(request):
        assert request.json['format_currency']
        return TOTW_RESPONSE

    response = await taxi_order_parts.post(
        '/4.0/mlutp/v1/taxi/v1/orders/state',
        json=_build_request(order_count),
        headers=DEFAULT_HEADERS,
    )
    assert mock_api_proxy.times_called == call_count
    assert response.status == expected_code
