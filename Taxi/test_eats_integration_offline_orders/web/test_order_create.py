import pytest

HEADERS = {'X-Eats-User': '123', 'X-Idempotency-Token': 'X-Idempotency-Token'}
JSON = {'uuid': 'uuid__1', 'items': [{'id': 'item_id_1', 'quantity': 1}]}


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'restaurants_options.sql'],
)
async def test_order_create_success(web_app_client, patch):
    @patch(
        'eats_integration_offline_orders.components.pos.iiko_client'
        '.IIKOClient.order_create',
    )
    async def _order_create(*args, **kwargs):
        return 'order_id'

    response = await web_app_client.post(
        f'/v1/order/create', json=JSON, headers=HEADERS,
    )
    assert response.status == 200


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'restaurants_options.sql'],
)
async def test_order_create_too_many_requests(web_app_client, patch):
    @patch(
        'eats_integration_offline_orders.components.pos.iiko_client'
        '.IIKOClient.order_create',
    )
    async def _order_create(*args, **kwargs):
        return 'order_id'

    response = await web_app_client.post(
        f'/v1/order/create', json=JSON, headers=HEADERS,
    )
    assert response.status == 200
    headers = dict(HEADERS)
    headers['X-Idempotency-Token'] += 'tail'
    response = await web_app_client.post(
        f'/v1/order/create', json=JSON, headers=headers,
    )
    assert response.status == 429
