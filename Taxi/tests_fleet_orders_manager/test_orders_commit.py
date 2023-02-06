import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/orders/commit'
REQUEST_BODY = {'phone_pd_id': 'id_+7123', 'order_id': 'order_id'}


@pytest.mark.parametrize(
    'orders_commit_response, expected_code, expected_body',
    [
        pytest.param(
            {
                'json': {'orderid': 'order_id', 'status': 'search'},
                'status': 200,
            },
            200,
            {'order_id': 'order_id'},
            id='200',
        ),
        pytest.param(
            {
                'json': {},
                'status': 202,
                'headers': {'Retry-After': 'some seconds'},
            },
            202,
            {},
            id='202',
        ),
    ],
)
async def test_ok(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        orders_commit_response,
        expected_code,
        expected_body,
):
    @mockserver.json_handler('/integration-api/v1/orders/commit')
    def _mock_orders_commit(request):
        return mockserver.make_response(**orders_commit_response)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body

    assert _mock_orders_commit.times_called == 1
    orders_commit_request = _mock_orders_commit.next_call()['request']
    assert orders_commit_request.json == {
        'userid': 'user_id_id_+7123',
        'orderid': 'order_id',
    }
    assert (
        orders_commit_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )
    assert orders_commit_request.headers['Accept-Language'] == 'de'


@pytest.mark.parametrize(
    'orders_draft_response, expected_code, expected_body',
    [
        pytest.param(
            {'json': {'error': {'text': 'blocked user'}}, 'status': 403},
            400,
            {'code': 'BLOCKED_USER', 'message': 'BLOCKED_USER'},
            id='404',
        ),
        pytest.param(
            {'json': {'error': {'text': 'order not found'}}, 'status': 404},
            400,
            {'code': 'ORDER_NOT_FOUND', 'message': 'ORDER_NOT_FOUND'},
            id='404',
        ),
        pytest.param(
            {'json': {'code': 'PREORDER_UNAVAILABLE'}, 'status': 406},
            400,
            {
                'code': 'PREORDER_UNAVAILABLE',
                'message': 'PREORDER_UNAVAILABLE',
            },
            id='406',
        ),
        pytest.param(
            {'json': {'code': 'TOO_MANY_CONCURRENT_ORDERS'}, 'status': 429},
            400,
            {
                'code': 'TOO_MANY_CONCURRENT_ORDERS',
                'message': 'TOO_MANY_CONCURRENT_ORDERS',
            },
            id='429',
        ),
    ],
)
async def test_4xx_from_commit(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        orders_draft_response,
        expected_code,
        expected_body,
):
    @mockserver.json_handler('/integration-api/v1/orders/commit')
    def _mock_phones_store(request):
        return mockserver.make_response(**orders_draft_response)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body
