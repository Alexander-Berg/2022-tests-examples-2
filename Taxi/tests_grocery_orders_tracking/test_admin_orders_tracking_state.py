import datetime

import pytest

from tests_grocery_orders_tracking import models


# we have to use actual now here,
# because we use PG's NOW() in cache and it's not mockable
NOW_FOR_CACHE = datetime.datetime.now()

TIME_NOW = '2020-05-25T17:43:43+00:00'
TIME_START_DELIVERY = '2020-05-25T17:40:45+00:00'
TIME_PASSED = 2
DEPOT_LOCATION = [13.0, 37.0]


@pytest.mark.parametrize('status', ['assembled', 'closed'])
@pytest.mark.now(TIME_NOW)
async def test_basic(
        taxi_grocery_orders_tracking,
        pgsql,
        testpoint,
        grocery_depots,
        grocery_cart,
        cargo,
        status,
):
    delivery_eta = 5

    order = models.Order(
        pgsql=pgsql,
        status=status,
        yandex_uid='yandex_uid',
        client_price=1100,
        status_updated=TIME_NOW,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
            dispatch_delivery_eta=delivery_eta,
            dispatch_start_delivery_ts=TIME_START_DELIVERY,
            dispatch_transport_type='car',
            dispatch_courier_first_name='Ivan',
            dispatch_driver_id='any_not_null_id',
        ),
        created=NOW_FOR_CACHE,
    )
    grocery_cart.set_order_conditions(delivery_cost=10, max_eta=15)
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        location=DEPOT_LOCATION,
        country_iso2='country_iso2',
    )

    response = await taxi_grocery_orders_tracking.post(
        '/admin/orders-tracking/v1/state', json={'order_id': order.order_id},
    )

    assert response.status_code == 200

    response_order = response.json()['grocery_order']
    assert response_order['order_id'] == order.order_id
    assert response_order['status'] == order.status
    if status == 'assembled':
        assert response_order['delivery_eta_min'] == delivery_eta - TIME_PASSED
    else:
        assert 'delivery_eta_min' not in response_order
