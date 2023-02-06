import pytest


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
@pytest.mark.parametrize(
    ('headers', 'params', 'expected_status'),
    [
        ({'X-Yandex-Login': 'username'}, {'comment_id': 'comment_1'}, 404),
        ({'X-Yandex-Login': 'username'}, {'comment_id': 'not found'}, 404),
        ({'X-Yandex-Login': 'username'}, {'comment_id': 'comment_2'}, 200),
        ({'X-Yandex-Login': 'other_user'}, {'comment_id': 'comment_3'}, 403),
    ],
)
async def test_admin_order_comment_delete(
        taxi_eats_corp_orders_web,
        headers,
        params,
        expected_status,
        web_context,
):
    start_count = len(
        await web_context.queries.admin_comments.get_by_filters(),
    )

    response = await taxi_eats_corp_orders_web.delete(
        '/v1/admin/order/comment', headers=headers, params=params,
    )
    assert response.status == expected_status

    finish_count = len(
        await web_context.queries.admin_comments.get_by_filters(),
    )
    if response.status == 200:
        assert start_count - finish_count == 1
    else:
        assert start_count - finish_count == 0
