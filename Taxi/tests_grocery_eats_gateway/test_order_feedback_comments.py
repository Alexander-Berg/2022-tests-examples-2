from tests_grocery_eats_gateway import configs
from tests_grocery_eats_gateway import headers


async def test_order_not_found(taxi_grocery_eats_gateway, grocery_orders):
    grocery_orders.set_feedback_comments_response(
        status_code=404,
        body={'error_code': 'invalid_evaluation', 'error_message': ''},
    )
    response = await taxi_grocery_eats_gateway.get(
        '/orders/v1/feedback/comments?order_id=order-id',
        json={},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 404
    assert grocery_orders.feedback_comments_times_called() == 1


@configs.GROCERY_FEEDBACK_PREDEFINED_COMMENTS
async def test_basic(taxi_grocery_eats_gateway, grocery_orders):
    comment_text_1 = 'long delivery'
    comment_text_2 = 'expensive'
    grocery_orders.set_feedback_comments_response(
        status_code=200,
        body={
            'comments': [
                {
                    'evaluation': 1,
                    'title': 'плохой фидбэк',
                    'predefined_comments': [
                        {'comment_id': 'comment_id_1', 'text': comment_text_1},
                    ],
                },
                {
                    'evaluation': 4,
                    'title': 'так себе фидбэк',
                    'predefined_comments': [
                        {'comment_id': 'comment_id_2', 'text': comment_text_2},
                    ],
                },
            ],
        },
    )

    order_id = 'order-1'
    grocery_orders.add_order(order_id=order_id)

    grocery_orders.check_feedback_request(
        order_id=order_id, refused_feedback=True,
    )

    response = await taxi_grocery_eats_gateway.get(
        f'/orders/v1/feedback/comments?order_id={order_id}',
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.feedback_comments_times_called() == 1
    assert response.status_code == 200

    assert response.json() == {
        'dislike_option_ids': [{'comment': comment_text_1, 'id': 1}],
        'like_option_ids': [{'comment': comment_text_2, 'id': 2}],
    }
