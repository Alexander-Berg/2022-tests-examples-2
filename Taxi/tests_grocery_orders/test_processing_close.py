import json
import uuid

import pytest

from . import headers
from . import models


NOW = '2020-03-13T07:19:00+00:00'
DISPATCH_ID = str(uuid.uuid4())


@pytest.mark.parametrize(
    'init_status',
    ['closed', 'delivering', 'checked_out', 'canceled', 'reserved'],
)
async def test_successful_close(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        cargo,
        init_status,
        tristero_parcels,
):
    orderstate = models.OrderState(
        wms_reserve_status='success', hold_money_status='success',
    )

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id='dispatch_id_1234',
        dispatch_status='created',
        dispatch_cargo_status='new',
    )
    cargo.set_data(dispatch_id=dispatch_status_info.dispatch_id)

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=orderstate,
        dispatch_status_info=dispatch_status_info,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    version = order.order_version

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'times_called': 1,
            'payload': {},
        },
    )

    order.update()

    want_status = init_status
    if init_status not in 'canceled':
        want_status = 'closed'

    something_must_change = init_status != want_status

    assert response.status_code == 200
    if something_must_change:
        assert order.status == want_status
        assert order.order_version == version + 1
    else:
        assert order.status == init_status


async def test_billing_flow(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
):
    orderstate = models.OrderState(
        wms_reserve_status='success', hold_money_status='success',
    )

    order = models.Order(pgsql=pgsql, status='reserved', state=orderstate)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'times_called': 1,
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_payments.times_cancel_called() == 1


@pytest.mark.parametrize('has_dispatch_status_info', [True, False])
@pytest.mark.parametrize(
    'init_status',
    ['closed', 'delivering', 'checked_out', 'canceled', 'reserved'],
)
async def cancel_close(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        cargo,
        init_status,
        has_dispatch_status_info,
        tristero_parcels,
):
    orderstate = models.OrderState(
        wms_reserve_status='success', hold_money_status='success',
    )

    if has_dispatch_status_info:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='dispatch_id_1234',
            dispatch_status='created',
            dispatch_cargo_status='new',
        )
        cargo.set_data(dispatch_id=dispatch_status_info.dispatch_id)
    else:
        dispatch_status_info = models.DispatchStatusInfo()

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=orderstate,
        dispatch_status_info=dispatch_status_info,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    version = order.order_version

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'times_called': 1,
            'payload': {},
        },
    )

    order.update()

    want_status = init_status
    if init_status not in ('closed', 'canceled'):
        want_status = 'canceled'

    something_must_change = init_status != want_status

    assert response.status_code == 200
    if something_must_change:
        assert order.status == want_status
        assert order.order_version == version + 1

        if has_dispatch_status_info:
            assert cargo.times_cancel_called() == 1
            assert order.dispatch_status_info.dispatch_status == 'revoked'
        else:
            assert cargo.times_cancel_called() == 0
    else:
        assert order.status == init_status
        assert cargo.times_cancel_called() == 0


async def test_ignore_not_found_from_money(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        grocery_wms_gateway,
):
    depot_id = '1234'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    state = models.OrderState(
        wms_reserve_status='success', close_money_status='success',
    )

    order = models.Order(
        pgsql=pgsql, status='delivering', state=state, depot_id=depot_id,
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v3',
            'is_canceled': True,
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == 200
    assert grocery_payments.times_cancel_called() == 1


async def test_tristero_no_cancel_money(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        grocery_wms_gateway,
):
    depot_id = '1234'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    state = models.OrderState(wms_reserve_status='success')
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        state=state,
        grocery_flow_version='tristero_flow_v1',
        depot_id=depot_id,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'tristero_flow_v1',
            'is_canceled': True,
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == 200

    # because it's without payment
    assert grocery_payments.times_cancel_called() == 0


async def test_delivering_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        grocery_dispatch,
        processing,
):
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
        ),
        order_version=1,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(dispatch_id=DISPATCH_ID, order_id=order.order_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    assert grocery_dispatch.times_cancel_called() == 1

    assert order.dispatch_status_info.dispatch_status == 'revoked'
    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    assert events[0].payload['order_id'] == order.order_id
    assert events[0].payload['reason'] == 'finish'


async def test_retry_on_dispatch_cancel_409(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        grocery_dispatch,
        processing,
):
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
        ),
        order_version=1,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID,
        order_id=order.order_id,
        cancel_error_code=409,
        status='canceled',
    )

    idempotency_token = 'token'
    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'payload': {},
            'idempotency_token': idempotency_token,
            'event_policy': {'retry_count': 0, 'retry_interval': 15},
        },
    )

    assert response.status_code == 200

    order.update()

    assert grocery_dispatch.times_cancel_called() == 1
    assert grocery_dispatch.times_info_called() == 1
    # 'canceled' from g-dispatch is converted to 'revoked' in g-orders
    assert order.dispatch_status_info.dispatch_status == 'revoked'

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    assert events[0].idempotency_token == '{}retry-policy-1'.format(
        idempotency_token,
    )
    payload = events[0].payload
    assert payload['order_id'] == order.order_id
    assert payload['reason'] == 'close'
    assert 'event_policy' in payload
