import pytest

HEADERS = {'X-Eats-User': 'user_id=177043222', 'X-Idempotency-Token': '1'}


@pytest.mark.parametrize(
    ('r_headers', 'r_body', 'expected_status'),
    [
        (HEADERS, {'order_id': 'order_id', 'feedback': {}}, 400),
        (
            HEADERS,
            {'order_id': 'order_id', 'feedback': {'comment': 'text'}},
            200,
        ),
        (HEADERS, {'order_id': 'order_id', 'feedback': {'rating': 5}}, 200),
        (
            {'X-Eats-User': 'user_id=0', 'X-Idempotency-Token': '1'},
            {'order_id': 'order_id', 'feedback': {'comment': 'text'}},
            401,
        ),
        (
            HEADERS,
            {'order_id': 'not_found', 'feedback': {'comment': 'text'}},
            404,
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'orders.sql'],
)
async def test_order_feedback_post(
        taxi_eats_corp_orders_web, r_headers, r_body, expected_status,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/order/feedback', headers=r_headers, json=r_body,
    )
    assert response.status == expected_status


@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'orders.sql'],
)
async def test_order_feedback_post_409(taxi_eats_corp_orders_web):
    headers = dict(HEADERS)
    body = {'order_id': 'order_id', 'feedback': {'comment': 'text'}}
    response = await taxi_eats_corp_orders_web.post(
        '/v1/user/order/feedback', headers=headers, json=body,
    )
    assert response.status == 200

    headers['X-Idempotency-Token'] = '2'
    response_2 = await taxi_eats_corp_orders_web.post(
        '/v1/user/order/feedback', headers=headers, json=body,
    )
    assert response_2.status == 409
