import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/active-orders/terminate'
REQUEST_BODY = {'order_id': 'order_alias_id'}


@pytest.mark.parametrize(
    'ordercore_response, driver_orders_app_api_response, expected_status_code',
    [
        pytest.param(
            'order_core_assigned.json',
            'driver_orders_app_api_200.json',
            200,
            id='terminate 200',
        ),
        pytest.param(
            'order_core_assigned.json',
            'driver_orders_app_api_406.json',
            409,
            id='terminate 409 outdated',
        ),
        pytest.param(
            'order_core_search.json',
            'driver_orders_app_api_200.json',
            409,
            id='terminate 409 wrong status',
        ),
        pytest.param(
            'order_core_assigned_other_park.json',
            'driver_orders_app_api_200.json',
            404,
            id='terminate 404 other park',
        ),
    ],
)
async def test_ok(
        load_json,
        mockserver,
        taxi_fleet_orders_manager,
        ordercore_response,
        driver_orders_app_api_response,
        expected_status_code,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        response_and_code = load_json(ordercore_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/complete',
    )
    def _mock_driver_orders_app_api(request):
        assert request.headers.get('X-Yandex-Login') == 'dispatch_login'
        assert request.json.get('park_id') == 'park_id'
        assert request.json.get('origin') == 'yandex_dispatch'
        response_and_code = load_json(driver_orders_app_api_response)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'park_id',
        'X-Yandex-Login': 'dispatch_login',
    }
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status == expected_status_code
