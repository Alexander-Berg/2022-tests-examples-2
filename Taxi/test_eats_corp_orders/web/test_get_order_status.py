import pytest


@pytest.mark.config(
    EATS_CORP_ORDERS_TIMEOUT_SETTINGS={'order_status_polling_interval': 5.5},
)
async def test_no_order(
        taxi_eats_corp_orders_web, eats_authproxy_headers, load_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/get-order-status', headers=eats_authproxy_headers,
    )

    assert response.status == 200
    body = await response.json()
    assert body == {}
    assert response.headers['X-Polling-Delay'] == '5.5'


@pytest.mark.redis_store(file='redis_order_created')
@pytest.mark.parametrize('status', ('new', 'completed', 'failed'))
async def test_different_order_statuses(
        taxi_eats_corp_orders_web,
        eats_authproxy_headers,
        load_json,
        fill_db,
        status,
):
    fill_db(f'{status}_order.sql')

    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/get-order-status', headers=eats_authproxy_headers,
    )

    assert response.status == 200
    body = await response.json()
    assert body == load_json(f'response_for_{status}.json')
    assert response.headers['X-Polling-Delay'] == '1.0'
