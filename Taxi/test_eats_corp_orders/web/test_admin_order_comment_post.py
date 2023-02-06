import pytest


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
async def test_admin_order_comment_post(
        taxi_eats_corp_orders_web, web_context,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/admin/order/comment',
        headers={'X-Yandex-Login': 'username', 'X-Idempotency-Token': 'ik_4'},
        json={'comment': 'hello world', 'order_id': 'order_1'},
    )
    assert response.status == 200

    new_comment_id = (await response.json())['id']
    new_comment = await web_context.queries.admin_comments.get_by_id(
        new_comment_id,
    )

    assert new_comment.order_id == 'order_1'
    assert new_comment.author == 'username'
    assert new_comment.comment == 'hello world'
    assert new_comment.idempotency_key == 'ik_4'


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
async def test_admin_order_comment_post_idempotency(taxi_eats_corp_orders_web):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/admin/order/comment',
        headers={'X-Yandex-Login': 'username', 'X-Idempotency-Token': 'ik_3'},
        json={'comment': 'hello world', 'order_id': 'order_1'},
    )
    assert response.status == 200

    comment_id = (await response.json())['id']
    assert comment_id == 'comment_3'


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'admin_comments.sql'],
)
async def test_admin_order_comment_post_404(taxi_eats_corp_orders_web):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/admin/order/comment',
        headers={'X-Yandex-Login': 'username', 'X-Idempotency-Token': 'ik_4'},
        json={'comment': 'hello world', 'order_id': 'order_2'},
    )
    assert response.status == 404
