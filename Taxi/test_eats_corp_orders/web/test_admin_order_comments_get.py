import pytest


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'order_id': 'order_1'},
            200,
            {
                'comments': [
                    {
                        'author': 'username',
                        'comment': 'hello world',
                        'created_at': '2022-02-01T03:03:00+03:00',
                        'id': 'comment_3',
                    },
                    {
                        'author': 'username',
                        'comment': 'hello world',
                        'created_at': '2022-02-01T03:02:00+03:00',
                        'id': 'comment_2',
                    },
                ],
                'has_more': False,
            },
        ),
        ({'order_id': 'not fount'}, 200, {'comments': [], 'has_more': False}),
    ],
)
async def test_admin_order_comments_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/order/comments', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
