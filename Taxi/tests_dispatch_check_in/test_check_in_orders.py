import pytest


@pytest.mark.pgsql(
    'dispatch_check_in', files=['check_in_orders_fixed_time.sql'],
)
async def test_check_in_orders_cache(taxi_dispatch_check_in, load_json):
    response = await taxi_dispatch_check_in.get('/internal/check-in-orders')
    assert response.status_code == 200

    def key(x):
        return x['order_id']

    assert sorted(response.json(), key=key) == load_json('cache_etalon.json')
