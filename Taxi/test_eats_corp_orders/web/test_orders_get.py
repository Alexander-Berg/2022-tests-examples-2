import pytest


@pytest.mark.pgsql(
    'eats_corp_orders',
    files=['pg_eats_corp_orders.sql', 'orders_and_places.sql'],
)
async def test_orders_get(taxi_eats_corp_orders_web, eats_user, load_json):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/orders', headers={'X-Eats-User': eats_user},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('response.json')


async def test_orders_get_401(taxi_eats_corp_orders_web):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/orders', headers={'X-Eats-User': ''},
    )
    assert response.status == 401
