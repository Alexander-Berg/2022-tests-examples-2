import pytest

import tests_driver_orders_app_api.redis_helpers as rh

CONTENT_HEADER = {'Content-Type': 'application/json'}

PARK_ID = '7f7a2770b74443c1be43b495e043b577'
ORDER_ID = 'order_id'
DRIVER_ID = 'driver_id'
SOME_DATE = '2020-06-24T16:18:00.000000Z'
CATEGORY = 1234456
COST_PAY = 123.456789


@pytest.mark.parametrize('data', [{'apikey': 'apikey', 'id': ORDER_ID}])
@pytest.mark.parametrize('has_order_in_pg', [True, False])
@pytest.mark.parametrize('has_apikey_in_redis', [True, False])
async def test_external_order_status(
        taxi_driver_orders_app_api,
        redis_store,
        fleet_parks_shard,
        driver_orders,
        data,
        has_order_in_pg,
        has_apikey_in_redis,
):
    if has_order_in_pg:
        driver_orders.park_id = PARK_ID
        driver_orders.order_id = ORDER_ID
        driver_orders.provider = 2
        driver_orders.driver_id = DRIVER_ID
        driver_orders.status = 50
        driver_orders.cost_pay = str(COST_PAY)
        driver_orders.category = CATEGORY

    if has_apikey_in_redis:
        rh.create_apikey(redis_store, 'apikey', PARK_ID)

    code = 200 if (has_order_in_pg and has_apikey_in_redis) else 400
    url = '/external/v1/order/status?{}'.format(
        '&'.join(['{}={}'.format(k, v) for k, v in data.items()]),
    )
    response = await taxi_driver_orders_app_api.get(
        url, headers={**CONTENT_HEADER},
    )
    assert response.status_code == code
    if code == 200:
        assert response.json() == {
            'category': CATEGORY,
            'driver_id': DRIVER_ID,
            'status': 50,
            'cost_pay': COST_PAY,
        }
