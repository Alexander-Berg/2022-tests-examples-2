import datetime

import pytest

from . import consts
from . import models

MAX_ETA = 50
CREATED = models.DEFAULT_CREATED
PROMISED_AT = CREATED + datetime.timedelta(minutes=MAX_ETA)
FINISH_STARTED_IN_TIME = PROMISED_AT - datetime.timedelta(minutes=10)
FINISH_STARTED_LATE = PROMISED_AT + datetime.timedelta(minutes=10)

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'  # example: 2020-03-10T00:50:00+00:00


@pytest.mark.parametrize(
    'status, finish_started',
    [
        ('delivering', None),
        ('closed', FINISH_STARTED_IN_TIME),
        ('closed', FINISH_STARTED_LATE),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        status,
        finish_started,
        antifraud,
):
    country_iso3 = 'RUS'
    order = models.Order(
        pgsql,
        order_id='order_id',
        status=status,
        created=CREATED,
        finish_started=finish_started,
        short_order_id='short_order_id',
        country='Russia',
        city='Москва',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='revoked',
            dispatch_cargo_status='delivered',
        ),
        dispatch_performer=models.DispatchPerformer(
            driver_id='test-driver-id',
        ),
        cancel_reason_type='user_request',
        cancel_reason_message='message',
    )
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    item = models.GroceryCartItem(item_id=consts.ITEM_ID)
    grocery_cart.set_items(items=[item])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_promocode(
        code='PROMO', valid=True, discount='33', source='eats',
    )
    max_eta = MAX_ETA
    grocery_cart.set_order_conditions(
        delivery_cost='100', max_eta=max_eta, min_eta=max_eta,
    )

    tin = 'tin-for-depot'
    region_id = 213
    city = 'Москва'  # derived from region_id
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        tin=tin,
        country_iso3=country_iso3,
        region_id=region_id,
    )

    antifraud.set_is_fraud(False)
    antifraud.set_is_suspicious(True)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200
    order_meta = response.json()

    assert order_meta['order_id'] == order.order_id
    assert order_meta['short_order_id'] == order.short_order_id
    assert order_meta['app_info'] == order.app_info
    assert order_meta['yandex_uid'] == order.yandex_uid
    assert order_meta['taxi_user_id'] == order.taxi_user_id
    assert order_meta['order_status'] == order.status
    assert order_meta['depot_id'] == order.depot_id
    assert (
        datetime.datetime.fromisoformat(order_meta['created']) == order.created
    )

    assert order_meta['payment_type'] == 'card'
    assert order_meta['was_used_promocode'] is True
    assert order_meta['surge_additional_delivery_amount'] == '100'
    assert order_meta['country_label'] == order.country
    assert order_meta['country_iso3'] == country_iso3
    assert order_meta['city_label'] == city
    assert order_meta['courier_id'] == order.dispatch_performer.driver_id

    assert order_meta['items'] == [
        {'id': consts.ITEM_ID, 'title': 'title', 'quantity': '3'},
    ]

    order_promised_at = order.created + datetime.timedelta(minutes=max_eta)
    if status == 'delivering':
        time_interval = consts.NOW_DT - order_promised_at
    elif status == 'closed':
        time_interval = order.finish_started - order_promised_at
    order_delay_minutes = time_interval / datetime.timedelta(minutes=1)

    order_promised_at_str = order_promised_at.strftime(TIME_FORMAT)
    order_promised_at_str = (
        order_promised_at_str[:-2] + ':' + order_promised_at_str[-2:]
    )
    assert order_meta['order_promised_at'] == order_promised_at_str

    if order_delay_minutes >= 0:
        assert order_meta['order_delay_minutes'] == order_delay_minutes
    else:
        assert 'order_delay_minutes' not in order_meta

    assert order_meta['cancel_reason_type'] == 'user_request'
    assert order_meta['cancel_reason_message'] == 'message'
    assert order_meta['user_fraud'] == 'Unsure'
    assert order_meta['order_fraud'] == 'Unsure'


@pytest.mark.now(consts.NOW)
async def test_pickup(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, antifraud,
):
    order = models.Order(
        pgsql, order_id='order_id', short_order_id='short_order_id',
    )

    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )

    grocery_cart.set_delivery_type('pickup')

    tin = 'tin-for-depot'
    grocery_depots.add_depot(legacy_depot_id=order.depot_id, tin=tin)

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200
    order_meta = response.json()

    assert 'order_delay_minutes' not in order_meta
