import datetime

import pytest

from . import consts
from . import helpers
from . import models
from . import processing_noncrit

POSTPONE_TIME = (consts.NOW_DT + datetime.timedelta(minutes=30)).isoformat()


@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.config(GROCERY_ORDERS_PICKUP_CLOSE_INTERVAL_SECONDS=1800)
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'init_status, result_status, status_code, order_version_delta,'
    'delivery_type',
    [
        ('draft', 'draft', 409, 0, 'pickup'),
        ('checked_out', 'checked_out', 409, 0, 'pickup'),
        ('reserved', 'reserved', 409, 0, 'pickup'),
        ('canceled', 'canceled', 409, 0, 'pickup'),
        ('assembled', 'assembled', 200, 0, 'pickup'),
        ('assembling', 'assembling', 409, 0, 'pickup'),
        ('closed', 'closed', 409, 0, 'pickup'),
        ('delivering', 'delivering', 409, 0, 'pickup'),
        ('delivering', 'delivering', 409, 0, 'courier'),
        ('assembled', 'delivering', 200, 1, 'courier'),
    ],
)
async def test_response_by_status(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        init_status,
        result_status,
        status_code,
        order_version_delta,
        delivery_type,
        grocery_wms_gateway,
        testpoint,
):
    order = models.Order(pgsql=pgsql, status=init_status)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(delivery_type)

    expected_eda_status = (
        'PICKUP' if delivery_type == 'pickup' else 'WAITING_ASSIGNMENTS'
    )
    grocery_wms_gateway.check_set_eda_status(expected_eda_status)

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == status_code

    order_version = order.order_version
    order.update()

    assert order.order_version == order_version + order_version_delta
    assert order.status == result_status

    if status_code != 200:
        events = list(processing.events(scope='grocery', queue='processing'))
        assert not events
    elif delivery_type == 'courier':
        events = list(processing.events(scope='grocery', queue='processing'))
        assert not events

        non_critical_events = list(
            processing.events(
                scope='grocery', queue='processing_non_critical',
            ),
        )
        assert len(non_critical_events) == 1
        payload = {}
        if result_status == 'delivering':
            payload['delivery_type'] = delivery_type
        processing_noncrit.check_push_notification(
            non_critical_events[0].payload,
            {
                'order_id': order.order_id,
                'reason': 'order_notification',
                'code': 'ready_for_dispatch',
                'payload': payload,
            },
        )

        assert grocery_wms_gateway.times_set_eda_status_called() == 1
    else:
        basic_events = list(
            processing.events(scope='grocery', queue='processing'),
        )
        assert len(basic_events) == 1
        assert basic_events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'idempotency_token': '{}-close-due'.format(
                order.idempotency_token,
            ),
        }
        assert basic_events[0].due == POSTPONE_TIME

        non_critical_events = list(
            processing.events(
                scope='grocery', queue='processing_non_critical',
            ),
        )
        assert len(non_critical_events) == 1
        processing_noncrit.check_push_notification(
            non_critical_events[0].payload,
            {
                'order_id': order.order_id,
                'reason': 'order_notification',
                'code': 'ready_for_pickup',
                'payload': {},
            },
        )

        assert grocery_wms_gateway.times_set_eda_status_called() == 1


@pytest.mark.parametrize('with_tristero_parcels', [True, False])
@pytest.mark.parametrize(
    'init_status, result_status, delivery_type',
    [
        ('assembled', 'assembled', 'pickup'),
        ('assembled', 'delivering', 'courier'),
    ],
)
async def test_tristero_parcels_updated(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        with_tristero_parcels,
        init_status,
        result_status,
        delivery_type,
):
    order = models.Order(pgsql=pgsql, status=init_status)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    item_id = (
        '98765432-10ab-cdef-0000-00020001:st-pa'
        if with_tristero_parcels
        else '98765432-10ab-cdef-0000-00020001'
    )

    grocery_cart.set_items([models.GroceryCartItem(item_id=item_id)])

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(delivery_type)

    await taxi_grocery_orders.post(
        '/processing/v1/dispatch',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    order.update()

    assert order.status == result_status

    setstate_event = processing_noncrit.check_noncrit_event(
        processing, order.order_id, 'tristero_setstate',
    )
    if delivery_type == 'pickup' or not with_tristero_parcels:
        assert setstate_event is None
    elif with_tristero_parcels:
        assert setstate_event is not None

        body = setstate_event['parcels_body']
        assert body['state'] == 'ready_for_delivery'
        assert body['state_meta']['order_id'] == order.order_id
        assert body['parcel_wms_ids'][0] == item_id


async def test_stop_after(
        _retry_after,
        grocery_depots,
        grocery_cart,
        processing,
        mocked_time,
        pgsql,
):
    mocked_time.set(consts.NOW_DT)

    order = models.Order(pgsql=pgsql, status='assembled')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    # try again later, after "stop_after".
    await _retry_after(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy={
            'stop_retry_after': helpers.skip_minutes(
                consts.STOP_AFTER_MINUTES,
            ),
        },
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


@pytest.fixture
def _retry_after(mocked_time, taxi_grocery_orders):
    return helpers.retry_processing(
        '/processing/v1/dispatch', mocked_time, taxi_grocery_orders,
    )
