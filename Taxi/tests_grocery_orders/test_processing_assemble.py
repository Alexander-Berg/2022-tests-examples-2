import datetime

import pytest

from . import consts
from . import models


@pytest.mark.parametrize(
    'flow,init_status,status_code',
    [
        ('grocery_flow_v1', 'draft', 409),
        ('grocery_flow_v1', 'reserved', 200),
        ('postponed_order_no_payment_flow_v1', 'postponed', 200),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        init_status,
        status_code,
        grocery_depots,
        overlord_catalog,
        processing,
        flow,
        testpoint,
):
    order = models.Order(pgsql=pgsql, grocery_flow_version=flow)
    order.upsert(status=init_status)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    version = order.order_version
    assert order.status == init_status

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))

    assert response.status_code == status_code
    if status_code == 200:
        assert grocery_wms_gateway.times_assemble_called() == 1
        assert order.status == 'assembling'
        assert order.order_version == version + 1
        assert len(events) == 1
        if flow == 'postponed_order_no_payment_flow_v1':
            assert events[0].payload['reason'] == 'dispatch_track'
        else:
            assert events[0].payload['reason'] == 'dispatch_request'
    else:
        assert grocery_wms_gateway.times_assemble_called() == 0
        assert order.status == init_status
        assert order.order_version == version
        assert events == []


@pytest.mark.parametrize('assembling_eta', [0, 1])
@pytest.mark.now(consts.NOW)
async def test_dispatch_request_without_eta(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        experiments3,
        assembling_eta,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(status='reserved')
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    experiments3.add_config(
        name='grocery_orders_dispatch_general',
        consumers=['grocery-orders/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'assembling_eta': assembling_eta},
            },
        ],
    )

    await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )
    events = list(processing.events(scope='grocery', queue='processing'))
    payload = events[0].payload
    assert payload['order_id'] == order.order_id
    assert payload['reason'] == 'dispatch_request'
    if assembling_eta > 0:
        assert datetime.datetime.fromisoformat(
            payload['due_time_point'],
        ) == consts.NOW_DT + datetime.timedelta(minutes=assembling_eta)


async def test_wms_failed(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(status='reserved')

    version = order.order_version
    grocery_wms_gateway.set_fail_flag(True)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 500
    order.update()
    assert order.order_version == version
    assert order.status == 'reserved'


@pytest.mark.now(consts.NOW)
async def test_wms_request_400(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        processing,
):
    order = models.Order(pgsql=pgsql, status='reserved')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_wms_gateway.set_http_resp(
        '{"code": "WMS_400", "message": "Bad request"}', 400,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 409
    assert grocery_wms_gateway.times_assemble_called() == 1

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 2
    assert events[0].payload['reason'] == 'dispatch_request'
    assert events[1].payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'failure',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'wms bad request',
        'times_called': 0,
    }

    order.update()

    assert order.desired_status == 'canceled'


async def test_desired_status_canceled(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        processing,
):
    order = models.Order(
        pgsql=pgsql, status='reserved', desired_status='canceled',
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 409
    assert grocery_wms_gateway.times_assemble_called() == 0

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events
