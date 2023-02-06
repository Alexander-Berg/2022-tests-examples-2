import bson
import pytest

ENDPOINT = '/fleet/fleet-orders-manager/v1/current-price'
ORDER_CORE_FIELDS = {
    'fields': [
        'order.pricing_data.published.taximeter.cost.driver.total',
        'order.pricing_data.published.fixed.cost.driver.total',
    ],
}

HEADERS = {
    'X-Ya-User-Ticket': 'ticket_valid1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': '1',
    'X-Park-ID': 'park_id',
}

PARAMS = {'order_id': 'order_id'}


def _make_order_core_response(fixed, taximeter):
    def _make_cost(key, value):
        return (
            {key: {'cost': {'driver': {'total': value}}}}
            if value is not None
            else {}
        )

    return {
        'document': {
            'processing': {'version': 20},
            '_id': 'd2651f7dfa4bcf16a5be8906cae7a4e8',
            'order': {
                'pricing_data': {
                    'published': {
                        **_make_cost('fixed', fixed),
                        **_make_cost('taximeter', taximeter),
                    },
                },
            },
        },
    }


@pytest.mark.parametrize(
    ('order_core_response', 'service_response', 'status'),
    [
        (
            _make_order_core_response(20.35, 12.12),
            {'taximeter': '12.12', 'fixed': '20.35'},
            200,
        ),
        (_make_order_core_response(None, 13.02), {'taximeter': '13.02'}, 200),
    ],
)
async def test_success(
        taxi_fleet_orders_manager,
        mockserver,
        order_core_response,
        service_response,
        status,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        return mockserver.make_response(
            bson.BSON.encode(order_core_response), status=200,
        )

    response = await taxi_fleet_orders_manager.get(
        ENDPOINT, params=PARAMS, headers=HEADERS,
    )

    assert response.status_code == status
    assert response.json() == service_response


async def test_404(taxi_fleet_orders_manager, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        return mockserver.make_response(
            status=404, json={'code': 'no_such_order', 'message': 'something'},
        )

    response = await taxi_fleet_orders_manager.get(
        ENDPOINT, params=PARAMS, headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {'message': 'Order not found', 'code': '404'}


async def test_no_prices(taxi_fleet_orders_manager, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        return mockserver.make_response(
            bson.BSON.encode(_make_order_core_response(None, None)),
            status=200,
        )

    response = await taxi_fleet_orders_manager.get(
        ENDPOINT, params=PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
