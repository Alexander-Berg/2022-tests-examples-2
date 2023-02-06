from tests_grocery_eats_gateway import configs
from tests_grocery_eats_gateway import headers


@configs.GROCERY_FEEDBACK_PREDEFINED_COMMENTS
async def test_order_not_found(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_response(
        status_code=404,
        body={'error_code': 'invalid_evaluation', 'error_message': ''},
    )
    response = await taxi_grocery_eats_gateway.post(
        '/orders/v1/feedback?order_id=order-id',
        json={
            'type': 2,
            'comment': 'Hello there',
            'predefined_comment_ids': [1, 2],
            'contact_requested': False,
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 404
    assert grocery_orders.order_feedback_times_called() == 1


@configs.GROCERY_FEEDBACK_PREDEFINED_COMMENTS
async def test_invalid_ids(taxi_grocery_eats_gateway, grocery_orders):
    response = await taxi_grocery_eats_gateway.post(
        '/orders/v1/feedback?order_id=order-id',
        json={
            'type': 2,
            'comment': 'Hello there',
            'predefined_comment_ids': [1337],
            'contact_requested': False,
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.order_feedback_times_called() == 0
    assert response.status_code == 400


@configs.GROCERY_FEEDBACK_PREDEFINED_COMMENTS
async def test_400_from_orders(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_response(
        status_code=400,
        body={'error_code': 'invalid_evaluation', 'error_message': ''},
    )
    response = await taxi_grocery_eats_gateway.post(
        '/orders/v1/feedback?order_id=order-id',
        json={
            'type': 2,
            'comment': 'Hello there',
            'predefined_comment_ids': [1],
            'contact_requested': False,
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.order_feedback_times_called() == 1
    assert response.status_code == 400


@configs.GROCERY_FEEDBACK_PREDEFINED_COMMENTS
async def test_basic(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_response(status_code=200, body={})
    order_id = 'order-1'
    grocery_orders.add_order(order_id=order_id)
    comment = 'Hello there'
    evaluation = 2

    grocery_orders.check_feedback_request(
        order_id=order_id,
        refused_feedback=False,
        feedback={
            'comment': comment,
            'evaluation': evaluation,
            'predefined_comments': [
                {'comment_id': 'comment_id_1'},
                {'comment_id': 'comment_id_2'},
            ],
        },
    )

    response = await taxi_grocery_eats_gateway.post(
        f'/orders/v1/feedback?order_id={order_id}',
        json={
            'type': evaluation,
            'comment': comment,
            'predefined_comment_ids': [1, 2],
            'contact_requested': False,
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.order_feedback_times_called() == 1
    assert response.status_code == 200
