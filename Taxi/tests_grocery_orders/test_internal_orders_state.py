import datetime

import pytest

from . import models


# we have to use actual now here,
# because we use PG's NOW() in cache and it's not mockable
NOW_FOR_CACHE = datetime.datetime.now()

TIME_NOW = '2020-05-25T17:43:43+00:00'
TIME_START_DELIVERY = '2020-05-25T17:40:45+00:00'
TIME_PASSED = 2
DEPOT_LOCATION = [13.0, 37.0]


@pytest.mark.translations(
    grocery_orders={
        'order_remaining_time': {
            'ru': 'Ещё примерно %(minutes)s минут',
            'en': '%(minutes)s more minutes',
        },
    },
)
@pytest.mark.now(TIME_NOW)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        testpoint,
        grocery_depots,
        grocery_cart,
        cargo,
):
    delivery_eta = 5

    order_ids = []

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id in order_ids
        return '2020-05-25T17:43:45+00:00'

    def add_order(yandex_uid):
        order = models.Order(
            pgsql=pgsql,
            status='assembled',
            yandex_uid=yandex_uid,
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
        return order

    def assert_contains(response, orders):
        assert response.status_code == 200
        assert len(response.json()['grocery_orders']) == len(orders)

        for response_order in response.json()['grocery_orders']:
            print(response_order)
            order = next(
                order
                for order in orders
                if order.order_id == response_order['order_id']
            )
            assert order is not None
            assert response_order['short_order_id'] == order.short_order_id
            assert response_order['status'] == order.status
            assert response_order['order_source'] == 'yango'
            assert (
                response_order['delivery_eta_min']
                == delivery_eta - TIME_PASSED
            )
            assert response_order['cart_id'] == order.cart_id
            assert (
                response_order['client_price_template']
                == '1000 $SIGN$$CURRENCY$'
            )
            assert response_order['depot_location'] == DEPOT_LOCATION
            assert response_order['courier_info']['name'] == 'Ivan'
            assert response_order['courier_info']['transport_type'] == 'car'
            assert response_order['location'] == [10.0, 20.0]
            assert response_order['address'] == {
                'country': 'order_country',
                'city': 'order_city',
                'street': 'order_street',
                'house': 'order_building',
                'left_at_door': False,
                'meet_outside': False,
                'no_door_call': False,
                'floor': 'order_floor',
                'flat': 'order_flat',
                'doorcode': 'order_doorcode',
                'place_id': 'place-id',
                'country_iso2': 'country_iso2',
            }
            assert response_order['localized_promise'].startswith(
                'Заказ приедет к ~',
            )
            assert 'promise_max' in response_order
            assert response_order['status_updated'] == str(TIME_NOW)
            assert response_order['tracking_info']['title'].startswith(
                'Ещё примерно ',
            )
            assert 'actions' in response_order

    yandex_uid_1 = 'yandex_uid_1'
    order_1 = add_order(yandex_uid_1)
    order_ids.append(order_1.order_id)

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state', json={'yandex_uid': yandex_uid_1},
    )
    assert_contains(response, [order_1])

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state',
        json={
            'yandex_uid': 'other_yandex-uid',
            'bound_yandex_uids': [yandex_uid_1],
        },
    )
    assert_contains(response, [order_1])

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state', json={'yandex_uid': 'other_yandex-uid'},
    )
    assert response.status_code == 200
    assert not response.json()['grocery_orders']

    yandex_uid_2 = 'yandex_uid_2'
    order_2 = add_order(yandex_uid_2)
    order_ids.append(order_2.order_id)
    await taxi_grocery_orders.invalidate_caches()

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state',
        json={'yandex_uid': yandex_uid_1, 'bound_yandex_uids': [yandex_uid_2]},
    )
    assert_contains(response, [order_1, order_2])

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state',
        json={
            'yandex_uid': 'fake_yandex_uid',
            'order_ids': [order_1.order_id],
        },
    )
    assert_contains(response, [])

    response = await taxi_grocery_orders.post(
        'internal/v1/orders-state',
        json={
            'yandex_uid': 'yandex_uid_1',
            'order_ids': [order_1.order_id, order_2.order_id],
        },
    )
    assert_contains(response, [order_1])

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders-state',
        json={'order_ids': [order_1.order_id, order_2.order_id]},
    )
    assert_contains(response, [order_1, order_2])
