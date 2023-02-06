import pytest

from tests_grocery_eats_gateway import headers

GROCERY_ORDER_CYCLE_ENABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-eats-gateway/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_basic(taxi_grocery_eats_gateway, load_json, mockserver):
    order_log_orders = load_json('grocery_orders_map.json')

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_orders(request):
        assert request.json['range']['order_id']
        return {'orders': order_log_orders[request.json['range']['order_id']]}

    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/batch-orders',
        json={'order_nrs': ['order_1', 'order_2', 'order_3']},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert mock_grocery_orders.times_called == 3
    assert response.json() == load_json('expected_test_basic_response.json')


@GROCERY_ORDER_CYCLE_ENABLED
async def test_orders_not_found(
        taxi_grocery_eats_gateway, load_json, mockserver,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_orders(request):
        assert request.json['range']['order_id']
        return mockserver.make_response(json={}, status=404)

    # overlord_depots_cache
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/batch-orders',
        json={'order_nrs': ['order_1', 'order_2', 'order_3']},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status == 200, response
    assert mock_grocery_orders.times_called == 3
    assert response.json() == []
