# pylint: disable=too-many-lines
import uuid

import pytest

from . import consts
from . import experiments
from . import headers
from . import models

NOW_TIME = '2020-05-25T17:43:45+00:00'
POSTPONE_TIME = '2020-05-25T18:03:45+00:00'

DISPATCH_ID = str(uuid.uuid4())

TIMEOUT_CANCEL_ACTION_CONFIG = pytest.mark.experiments3(
    name='lavka_timeout_cancel_action',
    consumers=['grocery-orders/cancel'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'postpone',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'common',
                                'arg_name': 'timeout_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'delivering',
                                'arg_name': 'order_status',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'accepted',
                                'arg_name': 'order_dispatch_status',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'performer_draft',
                                'arg_name': 'order_dispatch_cargo_status',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'type': 'postpone', 'minutes_count': 20},
        },
        {
            'title': 'ignore',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'common',
                                'arg_name': 'timeout_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'delivering',
                                'arg_name': 'order_status',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'accepted',
                                'arg_name': 'order_dispatch_status',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'type': 'ignore'},
        },
        {
            'title': 'postpone',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'payment',
                                'arg_name': 'timeout_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'lte',
                            'init': {
                                'value': 5,
                                'arg_name': 'minutes_after_last_update',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'type': 'postpone', 'minutes_count': 20},
        },
    ],
    is_config=True,
)


DISPATCH_STATUS_CONVERTER = {
    'idle': 'created',
    'scheduled': 'created',
    'rescheduling': 'accepted',
    'matching': 'accepted',
    'offered': 'accepted',
    'matched': 'accepted',
    'delivering': 'delivering',
    'delivery_arrived': 'delivering',
    'delivered': 'closed',
    'finished': 'closed',
    'canceling': 'revoked',
    'canceled': 'revoked',
    'revoked': 'failed',
}


@pytest.mark.config(GROCERY_ORDERS_WRITE_TO_STATUS_CHANGED_TOPIC=True)
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'init_status,expected_status,is_already_closed,status_code,reason_type',
    [
        ('closed', 'pending_cancel', True, 200, 'admin_request'),
        ('closed', 'closed', True, 200, 'timeout'),
        ('canceled', 'canceled', True, 200, 'timeout'),
        ('pending_cancel', 'pending_cancel', False, 200, 'timeout'),
        ('reserved', 'pending_cancel', False, 200, 'timeout'),
        ('reserved', 'pending_cancel', False, 200, 'failure'),
        ('draft', 'pending_cancel', False, 200, 'fraud'),
        ('checked_out', 'pending_cancel', False, 200, 'timeout'),
        ('checked_out', 'pending_cancel', False, 200, 'failure'),
        ('draft', 'pending_cancel', False, 200, 'invalid_payment_method'),
        ('checked_out', 'pending_cancel', False, 200, 'dispatch_failure'),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        testpoint,
        init_status,
        expected_status,
        is_already_closed,
        status_code,
        taxi_grocery_orders_monitor,
        reason_type,
):
    @testpoint('order_already_is_closed')
    def order_already_is_closed(_):
        return True

    cancel_reason_message = 'smth failed'
    cancel_reason_type = reason_type
    cancel_reason_meta = {'any': 'json'}

    order = models.Order(
        pgsql=pgsql, status=init_status, session='uber_eats:1',
    )
    assert order.status == init_status
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    metrics_before = await taxi_grocery_orders_monitor.get_metric('metrics')

    @testpoint('status_changed_event')
    def order_commit(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': expected_status,
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

    @testpoint('uber_order_status_changed_event')
    def uber_order_commit(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': expected_status,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'cancel_reason_meta': cancel_reason_meta,
            'payload': {},
        },
    )

    if init_status == expected_status:
        assert order_commit.times_called == 0
        assert uber_order_commit.times_called == 0
    else:
        assert order_commit.times_called == 1
        assert uber_order_commit.times_called == 1

    assert response.status_code == status_code

    order.update()

    assert order.status == expected_status

    if cancel_reason_type == 'admin_request' and is_already_closed:
        assert order.cancel_reason_type == cancel_reason_type
        assert order.cancel_reason_message == cancel_reason_message
        assert order.cancel_reason_meta == cancel_reason_meta
        assert order_already_is_closed.times_called == 0
    else:
        assert order.cancel_reason_type == (
            cancel_reason_type if not is_already_closed else None
        )
        assert order.cancel_reason_message == (
            cancel_reason_message if not is_already_closed else None
        )
        assert order.cancel_reason_meta == (
            cancel_reason_meta if not is_already_closed else None
        )

        assert order_already_is_closed.times_called == (
            1 if is_already_closed else 0
        )

    events = list(processing.events(scope='grocery', queue='processing'))

    idempotency_token = '{}-close'.format(order.idempotency_token)
    if cancel_reason_type == 'admin_request':
        idempotency_token += '-admin'
    if expected_status == 'pending_cancel':
        assert len(events) == 1
        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'idempotency_token': idempotency_token,
        }

    metrics_after = await taxi_grocery_orders_monitor.get_metric('metrics')

    notification_events_count = len(
        list(
            processing.events(
                scope='grocery', queue='processing_non_critical',
            ),
        ),
    )

    if (not is_already_closed) or (
            cancel_reason_type == 'admin_request'
            and expected_status == 'pending_cancel'
            and is_already_closed
    ):
        assert (
            metrics_after['processing_events']
            - metrics_before['processing_events']
            - notification_events_count
            == 1
        )
        assert (
            metrics_after['fail_orders'] - metrics_before['fail_orders'] == 1
        )
    else:
        assert (
            metrics_after['processing_events']
            - metrics_before['processing_events']
            == 0
        )
        assert (
            metrics_after['fail_orders'] - metrics_before['fail_orders'] == 0
        )


@pytest.mark.now(NOW_TIME)
@TIMEOUT_CANCEL_ACTION_CONFIG
@pytest.mark.parametrize(
    'status,dispatch_status,dispatch_cargo_status,action',
    [
        ('delivering', 'accepted', 'performer_draft', 'postpone'),
        ('delivering', 'accepted', 'performer_lookup', 'ignore'),
        ('delivering', 'created', 'new', 'cancel'),
    ],
)
async def test_timeout_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        processing,
        grocery_depots,
        status,
        dispatch_status,
        dispatch_cargo_status,
        action,
):
    cancel_reason_type = 'timeout'
    cancel_reason_message = 'Timed out'

    order = models.Order(
        pgsql=pgsql,
        status=status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status=dispatch_status,
            dispatch_cargo_status=dispatch_cargo_status,
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID, order_id=order.order_id, status='delivering',
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'times_called': 0,
            'payload': {},
        },
    )
    order.update()

    assert response.status_code == 200

    if action == 'postpone':
        events = list(processing.events(scope='grocery', queue='processing'))

        assert len(events) == 1

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': 'timeout',
            'payload': {
                'event_created': NOW_TIME,
                'initial_event_created': NOW_TIME,
            },
            'cancel_reason_message': cancel_reason_message,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        assert events[0].due == POSTPONE_TIME

    elif action == 'ignore':
        assert order.status == status
    else:
        assert order.status == 'pending_cancel'


@pytest.mark.now(NOW_TIME)
@TIMEOUT_CANCEL_ACTION_CONFIG
@pytest.mark.parametrize(
    'updated, action',
    [
        ('2020-05-25T17:40:45+00:00', 'postpone'),
        ('2020-05-25T17:38:45+00:00', 'postpone'),
        ('2020-05-25T17:36:45+00:00', 'cancel'),
    ],
)
async def test_payment_timeout_postpone(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        cargo,
        processing,
        grocery_depots,
        updated,
        action,
):
    cancel_reason_type = 'payment_timeout'
    cancel_reason_message = 'Payment timed out'

    order = models.Order(pgsql=pgsql, status='checked_out', updated=updated)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'times_called': 0,
            'payload': {},
        },
    )
    order.update()

    assert response.status_code == 200

    if action == 'postpone':
        events = list(processing.events(scope='grocery', queue='processing'))

        assert len(events) == 1

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': cancel_reason_type,
            'payload': {
                'event_created': NOW_TIME,
                'initial_event_created': NOW_TIME,
            },
            'cancel_reason_message': cancel_reason_message,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        assert events[0].due == POSTPONE_TIME
    else:
        assert order.status == 'pending_cancel'


@pytest.mark.now(consts.NOW)
async def test_delivered_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        taxi_grocery_orders_monitor,
        grocery_dispatch,
        processing,
        grocery_depots,
):

    cancel_reason_message = 'Timed out'
    cancel_reason_type = 'timeout'

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID, order_id=order.order_id, status='finished',
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'payload': {},
        },
    )

    assert response.status_code == 409

    order.update()

    assert order.dispatch_status_info.dispatch_status == 'closed'
    assert (
        order.dispatch_status_info.dispatch_cargo_status == 'delivered_finish'
    )

    events = list(processing.events(scope='grocery', queue='processing'))

    assert len(events) == 1
    assert events[0].payload == {
        'order_id': order.order_id,
        'reason': 'close',
        'flow_version': 'grocery_flow_v1',
        'is_canceled': False,
        'idempotency_token': '{}-close'.format(order.idempotency_token),
    }


@pytest.mark.parametrize(
    'response_dispatch_status, order_cargo_revision, up_version',
    [('delivering', 1, 1)],
    # [('delivery_arrived', 0, 2), ('delivering', 1, 1)],
)
@pytest.mark.now(consts.NOW)
async def test_delivering_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        taxi_grocery_orders_monitor,
        grocery_dispatch,
        processing,
        grocery_depots,
        response_dispatch_status,
        order_cargo_revision,
        up_version,
):

    cancel_reason_message = 'Timed out'
    cancel_reason_type = 'timeout'

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='delivering',
            dispatch_cargo_status='pickuped',
            dispatch_cargo_revision=order_cargo_revision,
            dispatch_delivery_eta=10,
        ),
        order_version=1,
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID,
        order_id=order.order_id,
        status=response_dispatch_status,
        eta=10 * 60,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.order_version == 1 + up_version

    assert order.dispatch_status_info.dispatch_status == 'delivering'
    assert (
        order.dispatch_status_info.dispatch_status
        == DISPATCH_STATUS_CONVERTER[response_dispatch_status]
    )

    events = list(processing.events(scope='grocery', queue='processing'))

    assert len(events) == 1
    assert events[0].payload == {
        'order_id': order.order_id,
        'reason': 'close',
        'flow_version': 'grocery_flow_v1',
        'is_canceled': True,
        'idempotency_token': '{}-close'.format(order.idempotency_token),
    }


@pytest.mark.parametrize('hold_money_status', ['success', 'failed'])
@pytest.mark.parametrize(
    'init_status,expected_status,should_cancel',
    [
        ('closed', 'closed', False),
        ('canceled', 'canceled', False),
        ('pending_cancel', 'pending_cancel', False),
        ('reserved', 'pending_cancel', True),
        ('checked_out', 'pending_cancel', True),
        ('assembling', 'assembling', False),
        ('assembled', 'assembled', False),
        ('delivering', 'delivering', False),
        ('draft', 'pending_cancel', True),
        ('reserving', 'pending_cancel', True),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_payment_timeout(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        init_status,
        expected_status,
        should_cancel,
        taxi_grocery_orders_monitor,
        hold_money_status,
):

    cancel_reason_message = 'payment timed out'
    cancel_reason_type = 'payment_timeout'

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=models.OrderState(hold_money_status=hold_money_status),
    )
    assert order.status == init_status

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    if hold_money_status == 'success':
        assert order.status == init_status
    elif should_cancel:
        assert order.status == expected_status
        assert order.cancel_reason_type == cancel_reason_type
        assert order.cancel_reason_message == cancel_reason_message

        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }


@pytest.mark.parametrize(
    'wms_reserve_status, init_status, should_cancel',
    [
        ('success', 'assembling', False),
        ('failed', 'checked_out', True),
        ('cancelled', 'checked_out', True),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_wms_reserve_timeout(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        init_status,
        wms_reserve_status,
        should_cancel,
        taxi_grocery_orders_monitor,
):

    cancel_reason_message = 'timed out'
    cancel_reason_type = 'timeout'

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=models.OrderState(wms_reserve_status=wms_reserve_status),
    )

    assert order.status == init_status

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'cancel_reason_meta': {'type': 'wms'},
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    if should_cancel:
        assert order.status == 'pending_cancel'
        assert order.cancel_reason_type == cancel_reason_type
        assert order.cancel_reason_message == cancel_reason_message

        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'close',
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        }
    else:
        assert order.status == init_status


@pytest.mark.parametrize('hold_money_status', ['success', 'failed'])
@pytest.mark.now(consts.NOW)
async def test_payment_timeout_dispatch_status(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        cargo,
        taxi_grocery_orders_monitor,
        hold_money_status,
):

    cancel_reason_message = 'payment timed out'
    cancel_reason_type = 'payment_timeout'
    init_status = 'created'

    order = models.Order(
        pgsql=pgsql,
        status='reserved',
        state=models.OrderState(hold_money_status='success'),
    )

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id='dispatch_id_1234',
        dispatch_status=init_status,
        dispatch_cargo_status='new',
    )

    order.upsert(dispatch_status_info=dispatch_status_info)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    cargo.set_data(
        dispatch_id='dispatch_id_1234',
        status='pickuped',
        items=[models.GroceryCartItem(item_id='item_id_1')],
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.dispatch_status_info.dispatch_status == init_status


@pytest.mark.parametrize('need_send_notification', [False, True])
@pytest.mark.parametrize(
    'init_status, reason_type, expected_message_count',
    [
        ('closed', 'failure', 0),
        ('canceled', 'failure', 0),
        ('checked_out', 'timeout', 1),
        ('reserving', 'failure', 1),
        ('reserved', 'failure', 1),
        ('reserved', 'user_request', 0),
        ('assembling', 'payment_failed', 1),
        ('assembled', 'admin_request', 1),
        ('delivering', 'payment_timeout', 0),
        ('reserved', 'payment_timeout', 1),
        ('draft', 'fraud', 1),
        ('pending_cancel', 'failure', 1),
        ('draft', 'invalid_payment_method', 1),
        ('closed', 'dispatch_failure', 0),
        ('canceled', 'dispatch_failure', 0),
        ('reserving', 'dispatch_failure', 1),
        ('reserved', 'dispatch_failure', 1),
        ('pending_cancel', 'dispatch_failure', 1),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_user_notification(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        init_status,
        reason_type,
        expected_message_count,
        need_send_notification,
):

    cancel_reason_message = 'testing_message'
    cancel_reason_type = reason_type

    order = models.Order(pgsql=pgsql, status=init_status)

    assert order.status == init_status

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_message': cancel_reason_message,
        'cancel_reason_type': cancel_reason_type,
        'need_send_notification': need_send_notification,
    }

    if reason_type == 'admin_request':
        request['payload'] = {'support_login': 'support-login'}

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel', json=request,
    )

    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if not need_send_notification:
        expected_message_count = 0
    assert len(events) == expected_message_count

    if expected_message_count == 1:
        event = events[0]
        assert event.payload['reason'] == 'order_notification'
        assert 'order_info' in event.payload
        assert (
            event.payload['order_info']['taxi_user_id'] == order.taxi_user_id
        )
    if reason_type == 'admin_request':
        order.check_order_history(
            'admin_action',
            {
                'to_action_type': 'cancel',
                'status': 'success',
                'admin_info': {'x_yandex_login': 'support-login'},
            },
        )
        order.check_order_history('status_change', {'to': 'pending_cancel'})


@pytest.mark.parametrize(
    'reason_meta, expected_key_suffix',
    [
        ('not_enough_funds', 'not_enough_funds'),
        ('common', 'common'),
        ('test', 'common'),
    ],
)
@pytest.mark.now(consts.NOW)
async def test_user_notification_payment_failed(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        reason_meta,
        expected_key_suffix,
):
    cancel_reason_message = 'testing_message'
    cancel_reason_type = 'payment_failed'
    cancel_reason_meta = {'error_code': reason_meta}
    push_title = f'push_payment_error.title.{expected_key_suffix}'
    push_text = f'push_payment_error.subtitle.{expected_key_suffix}'
    sms_text = f'sms_payment_error.{expected_key_suffix}'

    order = models.Order(pgsql=pgsql, status='assembling', locale='en')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'cancel_reason_meta': cancel_reason_meta,
            'need_send_notification': True,
            'payload': {},
        },
    )

    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1

    event = events[0]
    assert event.payload['payload']['push_error_title'] == push_title
    assert event.payload['payload']['push_error_text'] == push_text
    assert event.payload['payload']['sms_error_text'] == sms_text


@experiments.PAYMENTS_CLIENT_MAPPINGS_EXP
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'reason_meta, not_enough_funds',
    [('not_enough_funds', True), ('common', False), ('test', False)],
)
@pytest.mark.parametrize(
    'payment_method_type, country_iso3, default_mapped_key',
    [('card', 'RUS', False), ('card', 'ISR', True), ('applepay', 'RUS', True)],
)
async def test_payments_client_mappings(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        reason_meta,
        payment_method_type,
        country_iso3,
        default_mapped_key,
        not_enough_funds,
):
    order = models.Order(pgsql=pgsql, status='assembling', locale='en')
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3=country_iso3,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        payment_method={'type': payment_method_type, 'id': '123'},
        cart_id=order.cart_id,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': 'testing_message',
            'cancel_reason_type': 'payment_failed',
            'cancel_reason_meta': {'error_code': reason_meta},
            'need_send_notification': True,
            'payload': {},
        },
    )

    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1

    mapped_key = (
        experiments.RUS_CARD_MAPPED_TANKER_KEY
        if not default_mapped_key and not_enough_funds
        else experiments.MAPPED_TANKER_KEY
    )

    event = events[0]
    assert (
        event.payload['payload']['push_error_title']
        == f'push_payment_error.title.{mapped_key}'
    )
    assert (
        event.payload['payload']['push_error_text']
        == f'push_payment_error.subtitle.{mapped_key}'
    )
    assert (
        event.payload['payload']['sms_error_text']
        == f'sms_payment_error.{mapped_key}'
    )


@pytest.mark.now(consts.NOW)
@TIMEOUT_CANCEL_ACTION_CONFIG
@pytest.mark.parametrize(
    'config', [15, 50, 100], ids=['cancel', 'postpone50', 'postpone100'],
)
async def test_payment_timeout_config(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        processing,
        grocery_depots,
        config,
        taxi_config,
):
    taxi_config.set_values({'GROCERY_ORDERS_PAYMENT_TIMEOUT': config})
    postpone_time = consts.NOW
    updated = '2020-03-13T07:00:00+00:00'
    if config == 15:
        action = 'cancel'
    else:
        action = 'postpone'
        if config == 50:
            postpone_time = '2020-03-13T07:50:00+00:00'
        if config == 100:
            postpone_time = '2020-03-13T08:40:00+00:00'
    cancel_reason_type = 'payment_timeout'
    cancel_reason_message = 'Payment timed out'

    order = models.Order(pgsql=pgsql, status='checked_out', updated=updated)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/cancel',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': cancel_reason_message,
            'cancel_reason_type': cancel_reason_type,
            'times_called': 0,
            'payload': {'event_created': '2020-03-13T07:00:00+00:00'},
        },
    )
    order.update()

    assert response.status_code == 200

    if action == 'postpone':
        events = list(processing.events(scope='grocery', queue='processing'))

        assert len(events) == 1

        assert events[0].payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': cancel_reason_type,
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_message': cancel_reason_message,
            'times_called': 1,
            'flow_version': 'grocery_flow_v1',
        }

        assert events[0].due == postpone_time
    else:
        assert order.status == 'pending_cancel'
