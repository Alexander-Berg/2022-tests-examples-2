import datetime

import pytest

from . import consts
from . import experiments
from . import models

AFTER_NOW_DT = consts.NOW_DT + datetime.timedelta(minutes=10)
AFTER_NOW = AFTER_NOW_DT.isoformat()


@pytest.mark.now(consts.NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
async def test_coupons_fault(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        experiments3,
        processing,
):
    phone_id = 'ndajkscs'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'
    compensation_id = 'some_id'

    coupons.set_generate_error_code(code=500)

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    event_policy = {
        'retry_count': 1,
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
    }
    request_json = {
        'order_id': order.order_id,
        'compensation_id': compensation_id,
        'promocode_type': 'fixed',
        'promocode_value': 200,
        'promocode_value_numeric': '200',
        'compensation_type': 'promocode',
        'event_policy': event_policy,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/promocode', request_json,
    )
    assert response.status_code == 200

    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )
    events_non_critical = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events_compensations) == 1
    assert not events_non_critical

    # Check retry
    event = events_compensations[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['compensation_id'] == compensation_id
    assert event.payload['reason'] == 'compensation_promocode'


@pytest.mark.now(consts.NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
@pytest.mark.parametrize('need_send_notification', [True, False])
async def test_processing_events(
        taxi_grocery_orders,
        pgsql,
        coupons,
        grocery_cart,
        grocery_depots,
        experiments3,
        processing,
        need_send_notification,
):
    phone_id = 'ndajkscs'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'
    compensation_id = 'some_id'

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    coupons.check_request(
        token=f'{order.order_id}-fixed-195.4375-{compensation_id}',
        value=196,
        value_numeric='195.4375',
    )

    request_json = {
        'order_id': order.order_id,
        'compensation_id': compensation_id,
        'promocode_type': 'fixed',
        'promocode_value': 196,
        'promocode_value_numeric': '195.4375',
        'compensation_type': 'promocode',
        'need_send_notification': need_send_notification,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/promocode', request_json,
    )

    assert response.status_code == 200

    events_non_critical = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )

    if need_send_notification:
        assert len(events_non_critical) == 1
    else:
        assert not events_non_critical
    assert len(events_compensations) == 1

    event = events_compensations[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['compensation_id'] == compensation_id
    assert event.payload['payload'] == 'SOME_PROMOCODE'
    assert event.payload['state']


@pytest.mark.now(consts.NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
async def test_missing_series(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        experiments3,
        processing,
):
    phone_id = 'ndajkscs'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'
    compensation_id = 'some_id'

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    coupons.check_request(value=500, value_numeric='500.0')

    request_json = {
        'order_id': order.order_id,
        'compensation_id': compensation_id,
        'promocode_type': 'fixed',
        'promocode_value': 500,
        'promocode_value_numeric': '500',
        'compensation_type': 'promocode',
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/promocode', request_json,
    )

    assert response.status_code == 400

    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )
    events_non_critical = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events_compensations) == 1
    assert not events_non_critical

    event = events_compensations[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['compensation_id'] == compensation_id
    assert event.payload['reason'] == 'set_compensation_state'
    assert not event.payload['state']


@pytest.mark.now(consts.NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
@pytest.mark.parametrize(
    'phone, yandex_id, coupon_request, payload_state, error_code',
    [
        ('1232146712', 'ndajkscs', 200, True, None),
        ('1232146712', None, 400, False, 'bad_request'),
        (None, 'ndajkscs', 400, False, 'no_phone_id'),
        (None, None, 400, False, 'bad_request'),
    ],
)
async def test_bad_request(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        experiments3,
        processing,
        phone,
        yandex_id,
        coupon_request,
        payload_state,
        error_code,
):
    phone_id = phone
    personal_phone_id = 'azsa'
    yandex_uid = yandex_id
    compensation_id = 'some_id'

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    coupons.check_request(
        token=f'{order.order_id}-fixed-200-{compensation_id}',
        value=200,
        value_numeric='200',
    )

    request_json = {
        'order_id': order.order_id,
        'compensation_id': compensation_id,
        'promocode_type': 'fixed',
        'promocode_value': 200,
        'promocode_value_numeric': '200.0',
        'compensation_type': 'promocode',
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/compensation/promocode', request_json,
    )

    assert response.status_code == coupon_request

    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )

    assert len(events_compensations) == 1

    event = events_compensations[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['compensation_id'] == compensation_id
    assert event.payload['reason'] == 'set_compensation_state'
    assert event.payload['state'] == payload_state
    if coupon_request != 200:
        assert event.payload['error_code'] == error_code
