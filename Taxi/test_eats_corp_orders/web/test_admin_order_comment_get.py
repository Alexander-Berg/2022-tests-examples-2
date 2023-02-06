import pytest


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        ({'comment_id': 'comment_1'}, 404, {}),
        ({'comment_id': 'not found'}, 404, {}),
        (
            {'comment_id': 'comment_2'},
            200,
            {
                'id': 'comment_2',
                'comment': 'hello world',
                'author': 'username',
                'created_at': '2022-02-01T03:02:00+03:00',
            },
        ),
    ],
)
async def test_admin_order_comment_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/order/comment', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
