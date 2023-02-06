from tests_grocery_eats_gateway import headers


async def test_order_not_found(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_response(
        status_code=404,
        body={'error_code': 'invalid_evaluation', 'error_message': ''},
    )
    response = await taxi_grocery_eats_gateway.post(
        '/orders/v1/feedback/cancel?order_id=order-id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 404
    assert grocery_orders.order_feedback_times_called() == 1


async def test_basic(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_response(status_code=200, body={})
    order_id = 'order-1'
    grocery_orders.add_order(order_id=order_id)

    grocery_orders.check_feedback_request(
        order_id=order_id, refused_feedback=True,
    )

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/feedback/cancel?order_id={order_id}',
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.order_feedback_times_called() == 1
    assert response.status_code == 204
