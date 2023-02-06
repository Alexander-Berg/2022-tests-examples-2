# pylint: disable=too-many-lines
import datetime
import decimal
import json
import uuid

import pytest

from testsuite.utils import matching

from . import configs
from . import consts
from . import headers
from . import helpers
from . import models
from . import payments
from . import processing_noncrit

DEPOT_ID = '2809'
DISPATCH_ID = str(uuid.uuid4())

STOP_RETRY_AFTER_MINUTES = 1
ERROR_AFTER_SECONDS = 10
RETRY_INTERVAL_HOURS = 1
GROCERY_ORDERS_ORDER_TIMEOUT = 2

GET_COLUMN_NAMES = """
SELECT column_name
FROM information_schema.columns
WHERE
    table_schema = 'orders'
    AND table_name = 'orders'
"""

GET_DATA_TYPE = """
SELECT data_type, column_name
FROM information_schema.columns
WHERE
    table_schema = 'orders'
    AND table_name = 'orders'
"""

GET_PG_DATA = """
SELECT *
FROM orders.orders WHERE order_id = %s;
"""

GET_PG_DATA_HISTORY = """
SELECT *
FROM orders.orders_history WHERE order_id = %s;
"""

GET_PG_DATA_PAYMENT = """
SELECT *
FROM orders.orders_payments WHERE order_id = %s;
"""

GET_PG_DATA_AUTH = """
SELECT *
FROM orders.auth_context WHERE order_id = %s;
"""

GET_PG_DATA_FEEDBACK = """
SELECT *
FROM orders.feedback WHERE order_id = %s;
"""

GET_PG_DATA_ADDITIONAL = """
SELECT *
FROM orders.orders_additional WHERE order_id = %s;
"""

RAW_AUTH_CONTEXT = (
    """
    {
    "headers": {
    "X-YaTaxi-GeoId":"""
    + """"76734895f71d2c91bf6b5c80a31b17bc4a560e3b1f153b55d992b0532f47edeb",
"X-AppMetrica-DeviceId": "549B310C-6160-473D-AE64-C8A3C04B0105",
"X-YaTaxi-Session": "taxi: 954f5b242072431dae805284309669ea",
"X-Yandex-UID": "600355988",
"X-YaTaxi-PhoneId": "539eba35e7e5b1f539845423",
"X-Login-Id": "t: 2002224381",
"X-YaTaxi-UserId": "954f5b242072431dae805284309669ea",
"X-Yandex-Login": "nikitatyazhkun",
"X-Request-Application": "app_brand=lavka,app_ver3=0,device_make="""
    + """apple,app_name=lavka_iphone,app_build=release"""
    + """,platform_ver2=6,app_ver2="""
    + """3,platform_ver1=14,app_ver1=1",
"X-Ya-User-Ticket": "3: user: """
    + """CIOQARDP2YiJBho7CgYIlOmingIQlOmingIaCnlhdGF4aTpwYXkaC3lh"""
    + """dGF4aTpyZWFkGgx"""
    + """5YXRheGk6d3JpdGUg7LB7KAA: OdmRVoV4fEv80UJb47i6mWi4ozb5x3"""
    + """JX_Jeg3pwukh7VD"""
    + """96OZkfClfjB_Cpn3Hj1FpIvPSML45zGo_7FfyAE_fX6p8EO6GXP95QE7"""
    + """b6c0-aHwWKWjBBw"""
    + """x9Vl2sddF93luCgnK5_vu-Z3Y3iv-DeolysSV_B1ElV1TgLrC2-6p6JB"""
    + """ElrZUgNQJxrCWwA"""
    + """p4imgnzDg4mECRYiYXP3ACe7oJ1W8ew8bQaGm2EljOy-sqX3Ztv5f3Js"""
    + """n_5PsSDlRr8V2BF"""
    + """iT9RKF1MvqdYfBBOW8au2WWGqaxPNfZcebuJwF"""
    + """I1_EBRpnWdC8eQxb7lJLGxG0Cbv3bS3bkdZID6Jq6-kRow",
"X-YaTaxi-Bound-Sessions": "taxi: zc744f993162448fb6dee1d57aff34b6",
"X-YaTaxi-User": "personal_phone_id=b33e310b4f6c49b1b59f2e00060b45e3,"""
    + """personal_email_id=759680ddcdb949d793143ddf7cb3a441,"""
    + """eats_user_id=1573429",
"X-YaTaxi-Bound-UserIds": "zc744f993162448fb6dee1d57aff34b6",
"X-YaTaxi-Pass-Flags": "portal,social,ya-plus,"""
    + """cashback-plus,credentials=token-bearer",
"X-Remote-IP": "31.173.86.20",
"X-Request-Language": "ru"
}
}
"""
)

CLAUSE = {
    'title': 'Config',
    'predicate': {
        'init': {
            'set': ['correct_revert'],
            'arg_name': 'name',
            'set_elem_type': 'string',
        },
        'type': 'in_set',
    },
    'value': {
        'retry_interval': {'hours': RETRY_INTERVAL_HOURS},
        'error_after': {'seconds': ERROR_AFTER_SECONDS},
        'stop_retry_after': {'minutes': STOP_RETRY_AFTER_MINUTES},
    },
}
EVENT_POLICY_CONFIG = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=[
        'grocery-orders/processing-policy',
        'grocery-processing/policy',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[CLAUSE],
    is_config=True,
)


@pytest.fixture
def _prepare_paid_delivery(
        pgsql, grocery_cart, grocery_payments, grocery_depots,
):
    def _do():
        delivery_cost = '100'

        order = models.Order(pgsql=pgsql)

        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_cart_data(cart_id=order.cart_id)

        payment_method = {'type': 'card', 'id': 'test_payment_method_id'}
        grocery_cart.set_payment_method(payment_method)
        grocery_cart.set_order_conditions(delivery_cost=delivery_cost)

        return order

    return _do


@pytest.fixture
def _check_hold_failed(
        pgsql, grocery_cart, grocery_wms_gateway, grocery_payments,
):
    def _do(order, basic_events):
        assert order.state == models.OrderState(hold_money_status='failed')
        assert grocery_wms_gateway.times_close_called() == 0
        assert grocery_payments.times_cancel_called() == 0

        assert len(basic_events) == 1

        event = basic_events[0]
        assert event.item_id == order.order_id
        assert event.payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'cancel_reason_type': 'payment_failed',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_message': 'hold_money_failed',
            'cancel_reason_meta': {'error_code': 'not_enough_funds'},
            'flow_version': 'grocery_flow_v1',
            'times_called': 0,
        }

    return _do


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_wms_accepting_ok(
        taxi_grocery_orders, pgsql, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': []},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='success')


@EVENT_POLICY_CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'wms_status, hold_status, edit_status',
    [
        ('success', 'success', 'success'),
        ('failed', 'success', 'failed'),
        ('success', 'failed', 'failed'),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=True)
@pytest.mark.parametrize('correcting_type', ['remove', 'add'])
@pytest.mark.parametrize('order_status', ['assembling', 'delivering'])
async def test_edit_state(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        wms_status,
        hold_status,
        edit_status,
        processing,
        correcting_type,
        order_status,
):
    order = models.Order(
        pgsql=pgsql,
        edit_status='in_progress',
        status=order_status,
        correcting_type=correcting_type,
        child_cart_id=str(uuid.uuid4()),
    )
    order.update()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_correcting_type(correcting_type=correcting_type)

    wms_payload = {'problems': []}
    hold_payload = helpers.make_set_state_payload(
        operation_type='update', success=True,
    )
    if wms_status != 'success':
        wms_payload = {'problems': [1, 2, 3]}  # not empty
    if hold_status != 'success':
        hold_payload = helpers.make_set_state_payload(
            operation_type='update', success=False,
        )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': wms_payload,
        },
    )

    assert response.status_code == 200

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': hold_payload,
        },
    )

    assert response.status_code == 200

    prev_cart_version = order.cart_version
    prev_order_revision = order.order_revision

    order.update()

    if edit_status == 'success':
        assert grocery_cart.correct_commit_times_called() == 1
        assert order.cart_version == prev_cart_version + 1
        assert order.order_revision == prev_order_revision + 1

        assert order.state == models.OrderState(
            wms_reserve_status='success', hold_money_status='success',
        )

        assert order.edit_status is None
        assert order.child_cart_id is None

        grocery_cart.set_cart_data(
            cart_version=order.cart_version, cart_id=order.cart_id,
        )

        payload = {
            'problems': [],
            'success': True,
            'order_revision': str(order.order_revision),
        }

        response = await taxi_grocery_orders.post(
            '/processing/v1/set-state',
            json={
                'order_id': order.order_id,
                'state': 'assembled',
                'payload': payload,
            },
        )

        assert response.status_code == 200

        assert grocery_cart.correct_commit_times_called() == 1

        order.check_order_history(
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_finished',
                'correcting_result': 'success',
            },
        )
        order.check_order_history(
            'state_change', {'to': {'edit_status': 'success'}},
        )

    else:
        assert grocery_cart.correct_commit_times_called() == 0
        assert order.state == models.OrderState(
            wms_reserve_status=wms_status, hold_money_status=hold_status,
        )
        assert order.edit_status == edit_status
        assert order.cart_version == prev_cart_version
        assert order.order_revision == prev_order_revision

        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
        event = events[0]
        assert event.due == datetime.datetime

        stop_retry_after = consts.NOW_DT + datetime.timedelta(
            minutes=STOP_RETRY_AFTER_MINUTES,
        )
        error_after = consts.NOW_DT + datetime.timedelta(
            seconds=ERROR_AFTER_SECONDS,
        )
        retry_interval_seconds = RETRY_INTERVAL_HOURS * 60 * 60
        expected_payload = {
            'order_id': order.order_id,
            'reason': 'correct_revert',
            'order_revision': order.order_revision,
            'to_revert': {
                'revert_money': hold_status == 'success',
                'revert_wms': wms_status == 'success',
            },
            'event_policy': {
                'stop_retry_after': stop_retry_after.isoformat(),
                'error_after': error_after.isoformat(),
                'retry_interval': retry_interval_seconds,
                'retry_count': 1,
            },
        }
        assert event.payload == expected_payload

        order.check_order_history(
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_finished',
                'correcting_result': 'fail',
            },
        )


@pytest.mark.parametrize(
    'wms_state,order_revision,payload_order_revision,status_code,edit_status',
    [
        ('wms_accepting', 1, None, 200, None),
        ('wms_cancelled', 1, None, 200, None),
        ('assembled', 1, None, 200, None),
        ('wms_accepting', 1, '1', 200, None),
        ('wms_accepting', 1, '2', 200, 'in_progress'),
        ('wms_cancelled', 1, '1', 200, None),
        ('assembled', 1, '1', 200, None),
        ('wms_accepting', 2, '1', 409, None),
        ('wms_cancelled', 2, '1', 500, None),
        ('assembled', 2, '1', 500, None),
    ],
)
async def test_order_revision_check(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        wms_state,
        order_revision,
        payload_order_revision,
        status_code,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql, order_revision=order_revision, edit_status=edit_status,
    )
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    payload = {'problems': []}
    if wms_state == 'assembled':
        payload['success'] = True
    if payload_order_revision is not None:
        payload['order_revision'] = payload_order_revision

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': wms_state,
            'payload': payload,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_wms_accepting_no_problems(
        taxi_grocery_orders, pgsql, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status='success')


@pytest.mark.config(GROCERY_ORDERS_WRITE_ORDERS_OPERATIONS=True)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
@pytest.mark.parametrize('operation_type', payments.OPERATION_TYPES)
@pytest.mark.parametrize('success', [True, False])
async def test_order_operations_update(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        operation_type,
        success,
        edit_status,
):
    state = 'refund_money'
    operation_id = '1'
    order_id = 'test_order_id'
    order = models.Order(
        pgsql=pgsql,
        order_id=order_id,
        payment_operations=payments.get_default_payment_operations(
            order_id=order_id,
        ),
        edit_status=edit_status,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    order.update()

    payload = helpers.make_set_state_payload(
        success, operation_id='1', operation_type=operation_type,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={'order_id': order.order_id, 'state': state, 'payload': payload},
    )

    if operation_type in ('refund', 'remove', 'cancel'):
        assert response.status_code == 200
        order.update()
        status = 'success' if success else 'fail'
        errors = None
        if not success:
            errors = [
                {
                    'payment_type': 'applepay',
                    'error_reason_code': 'not_enough_funds',
                },
            ]
        order.check_payment_operation(
            (
                order.order_id,
                '1',
                operation_type,
                status,
                [],
                errors,
                payments.DEFAULT_COMPENSATION_ID,
            ),
        )
    else:
        assert response.status_code == 500
        return

    operation = next(
        operation
        for operation in order.payment_operations
        if operation.operation_type == operation_type
    )
    if success:
        assert operation.status == 'success'
    else:
        assert operation.status == 'fail'
    payment_history = {
        'to_operation_info': {
            'operation_id': operation_id,
            'operation_type': operation_type,
            'status': operation.status,
        },
    }
    if not success:
        payment_history['to_operation_info']['errors'] = payload['errors']
    order.check_order_history('payment_status_change', payment_history)

    events_compensations = list(
        processing.events(scope='grocery', queue='compensations'),
    )
    assert len(events_compensations) == 1
    event = events_compensations[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['compensation_id'] == payments.DEFAULT_COMPENSATION_ID
    assert event.payload['reason'] == 'set_compensation_state'
    assert event.payload['state'] == success


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('success', [True, False])
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
@processing_noncrit.NOTIFICATION_CONFIG
async def test_hold_money(
        taxi_grocery_orders,
        pgsql,
        success,
        grocery_cart,
        grocery_wms_gateway,
        grocery_payments,
        processing,
        grocery_depots,
        edit_status,
        _check_hold_failed,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': helpers.make_set_state_payload(success),
        },
    )

    assert response.status_code == 200

    order.update()
    basic_events = list(processing.events(scope='grocery', queue='processing'))

    if success:
        assert order.state == models.OrderState(hold_money_status='success')
        assert grocery_wms_gateway.times_close_called() == 0
        assert grocery_payments.times_cancel_called() == 0

        assert not basic_events
    else:
        if edit_status is None:
            _check_hold_failed(order, basic_events)


@pytest.mark.parametrize('success', [True, False])
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_close_money(
        taxi_grocery_orders,
        pgsql,
        success,
        grocery_cart,
        grocery_wms_gateway,
        grocery_payments,
        grocery_depots,
        edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'close_money',
            'payload': helpers.make_set_state_payload(success),
        },
    )

    assert response.status_code == 200

    assert grocery_payments.times_cancel_called() == 0
    assert grocery_wms_gateway.times_close_called() == 0

    order.update()
    if success:
        assert order.state == models.OrderState(close_money_status='success')
    else:
        assert order.state == models.OrderState(close_money_status='failed')


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_concurrent_update_different_states(
        taxi_grocery_orders, pgsql, testpoint, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    # Emulate situation when somebody change data during update.
    @testpoint('after_load_order_info')
    def after_load_order_info(data):
        order.upsert(state=models.OrderState(wms_reserve_status='success'))
        return {}

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    assert response.status_code == 200
    assert after_load_order_info.times_called == 1

    order.update()
    assert order.state == models.OrderState(
        wms_reserve_status='success', hold_money_status='success',
    )


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_idempotency(
        taxi_grocery_orders, pgsql, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    for _ in range(4):
        response = await taxi_grocery_orders.post(
            '/processing/v1/set-state',
            json={
                'order_id': order.order_id,
                'state': 'hold_money',
                'payload': {'success': True},
            },
        )

        assert response.status_code == 200
        order.update()
        assert order.order_version == 1
        assert order.state == models.OrderState(hold_money_status='success')


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_concurrent_update(
        taxi_grocery_orders, pgsql, testpoint, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    prev_order_version = 99

    # Emulate situation when somebody change data during update.
    @testpoint('after_load_order_info')
    def after_load_order_info(data):
        order.upsert(
            state=models.OrderState(hold_money_status='success'),
            order_version=prev_order_version,
        )
        return {}

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    assert response.status_code == 200
    assert after_load_order_info.times_called == 1

    order.update()
    assert order.order_version == prev_order_version
    assert order.state == models.OrderState(hold_money_status='success')


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_not_overwrite_stored_value(
        taxi_grocery_orders, pgsql, testpoint, grocery_cart, edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.update()
    assert order.state == models.OrderState()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    # Emulate situation when somebody change data during update.
    @testpoint('after_load_order_info')
    def after_load_order_info(data):
        order.upsert(state=models.OrderState(hold_money_status='failed'))
        return {}

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    assert response.status_code == 409
    assert after_load_order_info.times_called == 1

    order.update()
    assert order.state == models.OrderState(hold_money_status='failed')


@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=GROCERY_ORDERS_ORDER_TIMEOUT)
async def test_timeslot(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, processing,
):
    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    idempotency_token = 'idempotency_token'

    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        state=models.OrderState(wms_reserve_status='success'),
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        timeslot_request_kind=timeslot_request_kind,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    assert order.is_dispatch_request_started is None

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200

    order.update()
    assert order.is_dispatch_request_started is False

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 2
    dispatch_request_event = events[0]
    cancel_event = events[1]

    assert dispatch_request_event.payload == {
        'order_id': order.order_id,
        'reason': 'dispatch_request',
        'flow_version': 'grocery_flow_v1',
    }
    assert cancel_event.payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'timeout',
        'cancel_reason_message': 'Order timed out after long timeslot',
        'times_called': 0,
        'payload': {
            'event_created': matching.datetime_string,
            'initial_event_created': matching.datetime_string,
        },
    }
    assert _stringtime(cancel_event.due) == _stringtime(
        timeslot_end,
    ) + datetime.timedelta(minutes=GROCERY_ORDERS_ORDER_TIMEOUT)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200

    order.update()
    assert order.is_dispatch_request_started is False

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 2

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/continue',
        json={
            'order_id': order.order_id,
            'request_source': 'grocery_dispatch',
        },
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status_code == 200

    order.update()
    assert order.is_dispatch_request_started is True

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 3
    assemble_event = events[2]
    assert assemble_event.payload == {
        'order_id': order.order_id,
        'reason': 'assemble_ready',
        'flow_version': 'grocery_flow_v1',
        'order_version': 2,
    }

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/continue',
        json={
            'order_id': order.order_id,
            'request_source': 'grocery_dispatch',
        },
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status_code == 200

    order.update()
    assert order.is_dispatch_request_started is True

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 3


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_start_assemble_after_reserve_is_ok(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_depots,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        state=models.OrderState(wms_reserve_status='success'),
        edit_status=edit_status,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)

    assert order.order_version == 0

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    order.update()
    assert order.status == 'reserved'
    assert order.order_version == 2  # 2 updates: state & status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'assemble_ready',
        'flow_version': 'grocery_flow_v1',
        'order_version': order.order_version,
    }


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_postpone_after_reserve_is_ok(
        taxi_grocery_orders, pgsql, processing, grocery_cart, edit_status,
):
    postponed_flow = 'postponed_order_no_payment_flow_v1'

    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        edit_status=edit_status,
        grocery_flow_version=postponed_flow,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'success': True},
        },
    )
    order.update()

    assert order.status == 'reserved'
    assert order.order_version == 2

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1

    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'postpone',
        'flow_version': postponed_flow,
        'order_version': order.order_version,
    }


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_assembled_before_hold(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_depots,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        state=models.OrderState(
            wms_reserve_status='success', assembling_status='assembled',
        ),
        edit_status=edit_status,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)

    assert order.order_version == 0

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    order.update()
    assert order.status == 'reserved'
    assert order.order_version == 2  # 2 updates: state & status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'assemble_ready',
        'flow_version': 'grocery_flow_v1',
        'order_version': order.order_version,
    }


@pytest.mark.parametrize(
    'tristero_flow',
    ['tristero_flow_v1', 'tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_start_assemble_no_hold_tristero(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        tristero_flow,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        state=models.OrderState(),
        grocery_flow_version=tristero_flow,
        edit_status=edit_status,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    assert order.order_version == 0

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'success': True},
        },
    )

    order.update()
    assert order.status == 'reserved'
    assert order.order_version == 2  # 2 updates: state & status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'assemble_ready',
        'flow_version': tristero_flow,
        'order_version': order.order_version,
    }


@pytest.mark.config(GROCERY_ORDERS_SEND_ASSEMBLED_CARGO=True)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_start_dispatch_after_assemble_is_ok(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        edit_status,
):
    order = models.Order(pgsql=pgsql, edit_status=edit_status)
    order.upsert(
        state=models.OrderState(
            wms_reserve_status='success', hold_money_status='success',
        ),
        status='assembling',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='accepted',
            dispatch_cargo_status='performer_draft',
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_type('pickup')

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID, order_id=order.order_id, status='delivering',
    )

    assert order.status == 'assembling'
    assert order.order_version == 0

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )

    order.update()
    assert order.status == 'assembled'
    assert order.order_version == 2  # 2 updates: state & status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'dispatch_ready',
        'flow_version': 'grocery_flow_v1',
        'order_version': order.order_version,
    }

    assert grocery_dispatch.times_order_ready_called() == 1


@pytest.mark.parametrize(
    'tristero_flow',
    ['tristero_flow_v1', 'tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
@pytest.mark.config(GROCERY_ORDERS_SEND_ASSEMBLED_CARGO=True)
async def test_start_dispatch_after_assemble_is_ok_tristero(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        tristero_flow,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        grocery_flow_version=tristero_flow,
        edit_status=edit_status,
        dispatch_flow='grocery_dispatch',
    )
    order.upsert(
        state=models.OrderState(wms_reserve_status='success'),
        status='assembling',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=DISPATCH_ID,
            dispatch_status='accepted',
            dispatch_cargo_status='performer_draft',
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_dispatch.set_data(
        dispatch_id=DISPATCH_ID, order_id=order.order_id, status='delivering',
    )

    assert order.status == 'assembling'
    assert order.order_version == 0

    await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )

    order.update()
    assert order.status == 'assembled'
    assert order.order_version == 2  # 2 updates: state & status

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 1
    create_order_event = events[0]
    assert create_order_event.item_id == order.order_id
    assert create_order_event.payload == {
        'order_id': order.order_id,
        'reason': 'dispatch_ready',
        'flow_version': tristero_flow,
        'order_version': order.order_version,
    }

    assert grocery_dispatch.times_order_ready_called() == 1


@pytest.mark.config(GROCERY_ORDERS_SEND_ASSEMBLED_CARGO=True)
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
@processing_noncrit.NOTIFICATION_CONFIG
async def test_cancel_in_case_of_failed_assembling(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_payments,
        grocery_wms_gateway,
        grocery_cart,
        grocery_depots,
        cargo,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        status='assembling',
        state=models.OrderState(
            wms_reserve_status='success',
            hold_money_status='success',
            close_money_status='success',
        ),
        edit_status=edit_status,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': False},
        },
    )

    assert response.status_code == 200

    assert cargo.times_set_points_ready_called() == 0
    assert grocery_payments.times_cancel_called() == 0
    assert grocery_wms_gateway.times_close_called() == 0

    basic_events = list(processing.events(scope='grocery', queue='processing'))
    assert len(basic_events) == 1
    assert basic_events[0].payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'failure',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'assembling_failed',
        'times_called': 0,
    }


@pytest.mark.parametrize(
    'status,dispatch_status,assembling_status,want_event,result_status',
    [
        ('assembling', 'accepted', None, None, 'assembling'),
        ('assembling', 'accepted', 'assembled', 'dispatch_ready', 'assembled'),
        ('assembling', 'created', None, None, 'assembling'),
        ('pending_cancel', 'created', None, None, 'pending_cancel'),
        ('canceled', 'created', None, None, 'canceled'),
        ('assembling', 'delivering', None, None, 'assembling'),
        (
            'assembling',
            'delivering',
            'assembled',
            'dispatch_ready',
            'assembled',
        ),
    ],
)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_dispatch_requested(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_wms_gateway,
        grocery_depots,
        grocery_cart,
        status,
        dispatch_status,
        assembling_status,
        want_event,
        edit_status,
        result_status,
):
    order = models.Order(
        pgsql=pgsql,
        grocery_flow_version='grocery_flow_v3',
        status=status,
        state=models.OrderState(
            wms_reserve_status='success',
            hold_money_status='success',
            assembling_status=assembling_status,
        ),
        dispatch_status_info=models.DispatchStatusInfo(
            'dispatch_id_123', dispatch_status, 'accepted',
        ),
        edit_status=edit_status,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'dispatch_requested',
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.status == result_status

    events = list(processing.events(scope='grocery', queue='processing'))
    if want_event is not None:
        assert len(events) == 1
        event = events[0]
        assert event.item_id == order.order_id
        assert event.payload == {
            'order_id': order.order_id,
            'reason': want_event,
            'flow_version': 'grocery_flow_v3',
            'order_version': order.order_version,
        }
    else:
        assert not events


@pytest.mark.parametrize(
    'tristero_flow',
    ['tristero_flow_v1', 'tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
@pytest.mark.parametrize(
    'status,dispatch_status,assembling_status,want_event',
    [
        ('assembling', 'accepted', None, None),
        ('assembling', 'accepted', 'assembled', 'dispatch_ready'),
        ('assembling', 'created', None, None),
        ('assembling', 'delivering', None, None),
        ('assembling', 'delivering', 'assembled', 'dispatch_ready'),
    ],
)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_dispatch_requested_tristero(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_wms_gateway,
        grocery_cart,
        status,
        dispatch_status,
        assembling_status,
        want_event,
        tristero_flow,
        edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        grocery_flow_version=tristero_flow,
        status=status,
        state=models.OrderState(
            wms_reserve_status='success', assembling_status=assembling_status,
        ),
        dispatch_status_info=models.DispatchStatusInfo(
            'dispatch_id_123', dispatch_status, 'accepted',
        ),
        edit_status=edit_status,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'dispatch_requested',
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()

    events = list(processing.events(scope='grocery', queue='processing'))
    if want_event is not None:
        assert len(events) == 1
        event = events[0]
        assert event.item_id == order.order_id
        assert event.payload == {
            'order_id': order.order_id,
            'reason': want_event,
            'flow_version': tristero_flow,
            'order_version': order.order_version,
        }
    else:
        assert not events


@pytest.mark.parametrize(
    'status,dispatch_status,assembling_status,want_event,result_status',
    [
        ('assembling', 'accepted', None, None, 'assembling'),
        ('assembling', 'accepted', 'assembled', 'dispatch_ready', 'assembled'),
        ('assembling', 'created', None, None, 'assembling'),
        ('pending_cancel', 'created', None, None, 'pending_cancel'),
        ('canceled', 'created', None, None, 'canceled'),
        ('assembling', 'delivering', None, None, 'assembling'),
        (
            'assembling',
            'delivering',
            'assembled',
            'dispatch_ready',
            'assembled',
        ),
    ],
)
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_exchange_currency_requested(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_wms_gateway,
        grocery_depots,
        grocery_cart,
        status,
        dispatch_status,
        assembling_status,
        want_event,
        edit_status,
        result_status,
):
    order = models.Order(
        pgsql=pgsql,
        grocery_flow_version='exchange_currency',
        status=status,
        state=models.OrderState(
            wms_reserve_status='success',
            hold_money_status='success',
            assembling_status=assembling_status,
        ),
        dispatch_status_info=models.DispatchStatusInfo(
            'dispatch_id_123', dispatch_status, 'accepted',
        ),
        edit_status=edit_status,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'dispatch_requested',
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.status == result_status

    events = list(processing.events(scope='grocery', queue='processing'))
    if want_event is not None:
        assert len(events) == 1
        event = events[0]
        assert event.item_id == order.order_id
        assert event.payload == {
            'order_id': order.order_id,
            'reason': want_event,
            'flow_version': 'exchange_currency',
            'order_version': order.order_version,
        }
    else:
        assert not events


@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_wms_canceled_after_order_closing(
        taxi_grocery_orders, pgsql, grocery_cart, edit_status,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(wms_reserve_status='success'),
        status='closed',
        edit_status=edit_status,
    )
    order.update()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_cancelled',
            'payload': {'problems': []},
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.state == models.OrderState(wms_reserve_status='success')
    assert order.status == 'closed'


@pytest.mark.config(GROCERY_ORDERS_WRITE_ORDERS_OPERATIONS=True)
@pytest.mark.parametrize('operation_type', payments.OPERATION_TYPES)
@pytest.mark.parametrize('success', [True, False])
@pytest.mark.parametrize('state', ['hold_money', 'close_money'])
@pytest.mark.parametrize(
    'edit_status', ['in_progress', None],
)  # Check if new status doesn't break old ones
async def test_does_nothing_on_no_operation_type_or_id(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        operation_type,
        success,
        state,
        edit_status,
):
    order_id = 'test_order_id'
    order = models.Order(
        pgsql=pgsql,
        order_id=order_id,
        payment_operations=payments.get_default_payment_operations(
            order_id=order_id,
        ),
        edit_status=edit_status,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    order.update()

    payload = helpers.make_set_state_payload(
        success, operation_id='1', operation_type=operation_type,
    )

    if 'operation_id' in payload:
        del payload['operation_id']
    if 'operation_type' in payload:
        del payload['operation_type']

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={'order_id': order.order_id, 'state': state, 'payload': payload},
    )
    assert response.status_code == 200
    order.update()

    operation = next(
        operation
        for operation in order.payment_operations
        if operation.operation_type == operation_type
    )

    assert operation.status == 'requested'

    history = order.fetch_history()

    assert not any('payment_status_change' in item for item in history)


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_auth_context_ok(
        taxi_grocery_orders, grocery_cold_storage, grocery_cart, testpoint,
):
    order_id = 'order_id1'
    tips_status = 'pending'
    tips = '1.23'
    comment = 'До двери'
    created = '2020-05-25T17:20:45.123456'
    updated = '2020-05-25T17:35:45.123456'
    finished = '2020-05-25T17:43:45.123456'
    dispatch_start_delivery_ts = '2020-05-25T17:33:45.123456'
    dispatch_delivery_eta = 17
    dispatch_courier_name = 'Александр'
    dispatch_cargo_status = 'new'
    dispatch_status = 'closed'
    dispatch_id = '12345'
    due = '2020-05-25T17:20:46.123456'
    grocery_flow_version = 'grocery_flow_v1'
    idempotency_token = 'idempotency_token'
    currency = 'RUB'
    cancel_reason_message = 'Слишком долго'
    cancel_reason_type = 'user_request'
    assembling_status = 'assembled'
    close_money_status = 'success'
    hold_money_status = 'success'
    wms_reserve_status = 'success'
    doorcode = 'K123'
    doorcode_extra = ('doorcode_extra',)
    building_name = ('building_name',)
    doorbell_name = ('doorbell_name',)
    left_at_door = (False,)
    meet_outside = True
    no_door_call = True
    postal_code = 'SE16 3LR'
    delivery_common_comment = 'comment'
    place_id = 'some_place_id'
    floor = '1'
    flat = '5'
    house = '95B'
    street = 'Усачева'
    city = 'Москва'
    country = 'Россия'
    app_info = 'app_ver1=2,app_brand=yataxi,app_name=web'
    status = 'closed'
    client_price = 230.5
    depot_id = '123456'
    session = 'taxi:1526371256471'
    yandex_uid = '236i17836172'
    personal_phone_id = 'ye7872iu1rc3hir'
    phone_id = '12312ye7872iu1rc3hir'
    eats_user_id = 'some_12y48i2d'
    taxi_user_id = 'some_du38xo'
    eats_order_id = '12323-452123'
    cart_id = '32d82a0f-7da0-459c-ba24-12ec11f30c99'
    cart_version = 1
    short_order_id = '12312-123-1231'
    order_version = 13
    order_revision = 2
    billing_flow = 'grocery_payments'
    dispatch_flow = 'grocery_dispatch'
    location = [10.0, 20.0]
    promocode = 'late delivery'
    promocode_valid = True
    promocode_sum = '120'
    locale = 'ru'
    offer_id = 'offer_id1'
    user_info = 'user_info1'
    vip_type = consts.VIP_TYPE
    auth_context_table = [{'raw_auth_context': RAW_AUTH_CONTEXT}]
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cold_storage.set_orders_response(
        items=[
            {
                'item_id': order_id,
                'status': status,
                'client_price': str(client_price),
                'depot_id': depot_id,
                'session': session,
                'yandex_uid': yandex_uid,
                'personal_phone_id': personal_phone_id,
                'phone_id': phone_id,
                'eats_user_id': eats_user_id,
                'taxi_user_id': taxi_user_id,
                'eats_order_id': eats_order_id,
                'cart_id': cart_id,
                'cart_version': cart_version,
                'short_order_id': short_order_id,
                'order_version': order_version,
                'assembling_status': assembling_status,
                'close_money_status': close_money_status,
                'hold_money_status': hold_money_status,
                'wms_reserve_status': wms_reserve_status,
                'doorcode': doorcode,
                'doorcode_extra': doorcode_extra[0],
                'building_name': building_name[0],
                'doorbell_name': doorbell_name[0],
                'left_at_door': left_at_door[0],
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
                'postal_code': postal_code,
                'delivery_common_comment': delivery_common_comment,
                'place_id': place_id,
                'floor': floor,
                'flat': flat,
                'house': house,
                'street': street,
                'city': city,
                'country': country,
                'app_info': app_info,
                'cancel_reason_type': cancel_reason_type,
                'cancel_reason_message': cancel_reason_message,
                'currency': currency,
                'order_id': order_id,
                'grocery_flow_version': grocery_flow_version,
                'dispatch_id': dispatch_id,
                'dispatch_status': dispatch_status,
                'dispatch_cargo_status': dispatch_cargo_status,
                'dispatch_courier_name': dispatch_courier_name,
                'dispatch_delivery_eta': dispatch_delivery_eta,
                'dispatch_start_delivery_ts': dispatch_start_delivery_ts,
                'created': created,
                'updated': updated,
                'finished': finished,
                'comment': comment,
                'tips': tips,
                'tips_status': tips_status,
                'order_revision': order_revision,
                'billing_flow': billing_flow,
                'dispatch_flow': dispatch_flow,
                'location': location,
                'promocode': promocode,
                'promocode_valid': promocode_valid,
                'promocode_sum': promocode_sum,
                'vip_type': vip_type,
                'auth_context_table': auth_context_table,
                'due': due,
                'idempotency_token': idempotency_token,
                'locale': locale,
                'offer_id': offer_id,
                'user_info': user_info,
            },
        ],
    )

    @testpoint('check_extractor')
    def check_extractor(data):
        pass

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order_id,
            'state': 'close_money',
            'payload': {'problems': []},
        },
    )
    assert response.status_code == 500
    assert check_extractor.times_called == 1


@pytest.mark.config(GROCERY_ORDERS_ENABLE_RECOVERY_TO_PG=True)
@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_recovery_ok(
        taxi_grocery_orders, grocery_cold_storage, grocery_cart, pgsql,
):
    order_id = 'order_id1'
    tips_status = 'pending'
    tips = '1.23'
    comment = 'До двери'
    created = '2020-05-25T17:20:45.123456'
    updated = '2020-05-25T17:35:45.123456'
    finished = '2020-05-25T17:43:45.123456'
    dispatch_start_delivery_ts = '2020-05-25T17:33:45.123456'
    dispatch_delivery_eta = 17
    dispatch_courier_name = 'Александр'
    dispatch_cargo_status = 'new'
    dispatch_status = 'closed'
    dispatch_id = '12345'
    due = '2020-05-25T17:20:46.123456'
    grocery_flow_version = 'grocery_flow_v1'
    idempotency_token = 'idempotency_token'
    currency = 'RUB'
    cancel_reason_message = 'Слишком долго'
    cancel_reason_type = 'user_request'
    assembling_status = 'assembled'
    close_money_status = 'success'
    hold_money_status = 'success'
    wms_reserve_status = 'success'
    doorcode = 'K123'
    doorcode_extra = ('doorcode_extra',)
    building_name = ('building_name',)
    doorbell_name = ('doorbell_name',)
    left_at_door = (False,)
    meet_outside = True
    no_door_call = True
    postal_code = 'SE16 3LR'
    delivery_common_comment = 'comment_aass'
    place_id = 'some_place_id'
    floor = '2'
    flat = '5'
    house = '95B'
    street = 'Усачева'
    city = 'Москва'
    country = 'Россия'
    app_info = 'app_ver1=2,app_brand=yataxi,app_name=web'
    status = 'closed'
    client_price = 230.5
    depot_id = '123456'
    session = 'taxi:1526371256471'
    yandex_uid = '236i17836172'
    personal_phone_id = 'ye7872iu1rc3hir'
    phone_id = '12312ye7872iu1rc3hir'
    eats_user_id = 'some_12y48i2d'
    taxi_user_id = 'some_du38xo'
    eats_order_id = '12323-452123'
    cart_id = '32d82a0f-7da0-459c-ba24-12ec11f30c99'
    cart_version = 1
    short_order_id = '12312-123-1231'
    order_version = 13
    order_revision = 2
    billing_flow = 'grocery_payments'
    dispatch_flow = 'grocery_dispatch'
    location = [10.0, 20.0]
    promocode = 'late delivery'
    promocode_valid = True
    promocode_sum = '120'
    locale = 'ru'
    offer_id = 'offer_id1'
    user_info = 'user_info1'
    vip_type = consts.VIP_TYPE
    personal_email_id = 'personal_email_id1'
    bound_sessions = ['taxi:zbffc7e6d47e42dcb9ad576bb5534296']
    billing_settings_version = '1080_service'
    cancel_reason = 'cancel_reason'
    cancel_reason_meta = 'cancel_reason_meta'
    child_cart_id = '31d82a0f-7da0-459c-ba24-12ec11f30c99'
    correcting_type = 'add'
    desired_status = 'closed'
    dispatch_car_color = 'белый'
    dispatch_car_color_hex = 'FAFBFB'
    dispatch_car_model = 'Skoda Octavia'
    dispatch_car_number = 'Н510ТО197'
    dispatch_cargo_revision = 9
    dispatch_courier_first_name = 'Асим'
    dispatch_courier_id = 'dispatch_courier_id'
    dispatch_delivered_eta_ts = '2020-05-25T17:20:45.123456'
    dispatch_driver_id = (
        '43e5f12349d84e98a9c461e133ac64f7_f8210bc6463bd50068120fd62f27e94f'
    )
    dispatch_pickuped_eta_ts = '2020-05-25T17:20:45.123456'
    dispatch_status_meta = {
        'cargo_dispatch': {
            'claim_id': '4cb5cbf91c5846cdb2cad21f604144f9',
            'dispatch_delivery_type': 'yandex_taxi',
        },
    }
    dispatch_track_version = 61
    dispatch_transport_type = 'car'
    edit_status = 'success'
    entrance = '1'
    evaluation = 5
    feedback_status = 'refused'
    finish_started = '2020-05-25T17:20:45.123456'
    informer_key = 'informer_long_delivery'
    manual_update_enabled = False
    push_notification_enabled = False
    region_id = 5
    status_updated = '2020-05-25T17:20:45.123456'
    user_agent = (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) '
        'AppleWebKit/605.1.15 '
        '(KHTML, like Gecko) yandex-lavka/1.2.6.112243 '
        'YandexEatsKit/1.17.26 Lavka/Standalone'
    )
    user_ip = '127.0.0.1'
    wms_logistic_tags = ['market_batching']
    additional_phone_code = 'additional_phone_code'
    auth_context_table = [{'raw_auth_context': RAW_AUTH_CONTEXT}]
    feedback_table = [
        {
            'order_id': order_id,
            'feedback_options': ['Abc1', 'Abc2', 'Abc3'],
            'comment': 'feedback comment',
        },
    ]
    additional_table = [
        {
            'app_name': 'mobileweb_iphone',
            'appmetrica_device_id': '1FC37B95-3CAE-4FD8-B4B7-B48DD6208676',
            'created': created,
            'order_id': order_id,
            'updated': '2020-05-25T17:20:45.123456',
            'order_settings': '{}',
            'timeslot_start': '2020-03-13T09:50:00.123456',
            'timeslot_end': '2020-03-13T17:50:00.123456',
            'timeslot_request_kind': 'wide_slot',
            'is_dispatch_request_started': True,
        },
    ]
    payments_table = [
        {
            'order_id': order_id,
            'operation_id': '123',
            'operation_type': 'create',
            'status': 'success',
            'items': {
                'items': [
                    {
                        'price': '105',
                        'item_id': (
                            '9b681b3c0eba4e2f9a0738b4313f1def000200010000'
                        ),
                        'quantity': '1',
                        'receipt_info': {
                            'vat': '10',
                            'title': (
                                'Омлет с ветчиной и сыром «Хлеб Насущный»'
                            ),
                            'personal_tin_id': '9718101499',
                        },
                    },
                ],
                'payment_method': {
                    'id': 'card-x0c0cab13124063123e35406e',
                    'type': 'card',
                },
            },
            'errors': {},
            'created': '2020-05-25T17:20:45.123456',
            'updated': '2020-05-25T17:20:45.123456',
            'compensation_id': '1234',
        },
        {
            'order_id': order_id,
            'operation_id': '124',
            'operation_type': 'create',
            'status': 'success',
            'items': {
                'items': [
                    {
                        'price': '105',
                        'item_id': (
                            '9b681b3c0eba4e2f9a0738b4313f1def000200010000'
                        ),
                        'quantity': '1',
                        'receipt_info': {
                            'vat': '10',
                            'title': (
                                'Омлет с ветчиной и сыром «Хлеб Насущный»'
                            ),
                            'personal_tin_id': '9718101499',
                        },
                    },
                ],
                'payment_method': {
                    'id': 'card-x0c0cab13124063123e35406e',
                    'type': 'card',
                },
            },
            'errors': {},
            'created': '2020-05-25T17:20:45.123456',
            'updated': '2020-05-25T17:20:45.123456',
            'compensation_id': '1236',
        },
    ]
    history_table = [
        {
            'order_id': order_id,
            'ts': '2020-05-25T17:20:45.123456',
            'event_type': 'status_change',
            'event_data': '{"to": "draft"}',
        },
        {
            'order_id': order_id,
            'ts': '2020-05-26T17:20:45.123456',
            'event_type': 'status_change',
            'event_data': '{"to": "reserving"}',
        },
    ]
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cold_storage.set_orders_response(
        items=[
            {
                'order_id': order_id,
                'idempotency_token': idempotency_token,
                'created': created,
                'updated': updated,
                'eats_order_id': eats_order_id,
                'cart_id': cart_id,
                'cart_version': cart_version,
                'offer_id': offer_id,
                'taxi_user_id': taxi_user_id,
                'eats_user_id': eats_user_id,
                'phone_id': phone_id,
                'locale': locale,
                'user_info': user_info,
                'app_info': app_info,
                'yandex_uid': yandex_uid,
                'depot_id': depot_id,
                'due': due,
                'location': location,
                'place_id': place_id,
                'city': city,
                'street': street,
                'house': house,
                'flat': flat,
                'doorcode': doorcode,
                'entrance': entrance,
                'floor': floor,
                'comment': comment,
                'client_price': str(client_price),
                'promocode': promocode,
                'promocode_valid': promocode_valid,
                'promocode_sum': promocode_sum,
                'status': status,
                'cancel_reason': cancel_reason,
                'order_version': order_version,
                'user_ip': user_ip,
                'user_agent': user_agent,
                'session': session,
                'bound_sessions': bound_sessions,
                'wms_reserve_status': wms_reserve_status,
                'hold_money_status': hold_money_status,
                'close_money_status': close_money_status,
                'assembling_status': assembling_status,
                'short_order_id': short_order_id,
                'cancel_reason_type': cancel_reason_type,
                'cancel_reason_message': cancel_reason_message,
                'grocery_flow_version': grocery_flow_version,
                'dispatch_status': dispatch_status,
                'dispatch_cargo_status': dispatch_cargo_status,
                'dispatch_id': dispatch_id,
                'dispatch_delivery_eta': dispatch_delivery_eta,
                'personal_phone_id': personal_phone_id,
                'country': country,
                'dispatch_start_delivery_ts': dispatch_start_delivery_ts,
                'dispatch_courier_name': dispatch_courier_name,
                'currency': currency,
                'tips': tips,
                'tips_status': tips_status,
                'finished': finished,
                'dispatch_delivered_eta_ts': dispatch_delivered_eta_ts,
                'dispatch_pickuped_eta_ts': dispatch_pickuped_eta_ts,
                'region_id': region_id,
                'desired_status': desired_status,
                'finish_started': finish_started,
                'evaluation': evaluation,
                'feedback_status': feedback_status,
                'billing_flow': billing_flow,
                'dispatch_track_version': dispatch_track_version,
                'dispatch_courier_id': dispatch_courier_id,
                'order_revision': order_revision,
                'dispatch_transport_type': dispatch_transport_type,
                'cargo_revision': (
                    dispatch_cargo_revision
                ),  # cargo_revision -> dispatch_cargo_revision
                'dispatch_driver_id': dispatch_driver_id,
                'billing_settings_version': billing_settings_version,
                'dispatch_flow': dispatch_flow,
                'dispatch_status_meta': dispatch_status_meta,
                'status_updated': status_updated,
                'doorcode_extra': doorcode_extra[0],
                'building_name': building_name[0],
                'doorbell_name': doorbell_name[0],
                'left_at_door': left_at_door[0],
                'manual_update_enabled': manual_update_enabled,
                'dispatch_courier_first_name': dispatch_courier_first_name,
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
                'dispatch_car_number': dispatch_car_number,
                'edit_status': edit_status,
                'child_cart_id': child_cart_id,
                'correcting_type': correcting_type,
                'informer_key': informer_key,
                'postal_code': postal_code,
                'cancel_reason_meta': cancel_reason_meta,
                'vip_type': vip_type,
                'wms_logistic_tags': wms_logistic_tags,
                'push_notification_enabled': push_notification_enabled,
                'dispatch_car_model': dispatch_car_model,
                'dispatch_car_color': dispatch_car_color,
                'dispatch_car_color_hex': dispatch_car_color_hex,
                'personal_email_id': personal_email_id,
                'additional_phone_code': additional_phone_code,
                'delivery_common_comment': delivery_common_comment,
                'anonym_id': 'anonym_id',
                'auth_context_table': auth_context_table,
                'feedback_table': feedback_table,
                'additional_table': additional_table,
                'payments_table': payments_table,
                'history_table': history_table,
                'item_id': order_id,
            },
        ],
    )

    db = pgsql['grocery_orders'].cursor()
    db.execute(GET_COLUMN_NAMES)
    order_data_fields = db.fetchall()
    skip_fields = []

    order_data_fields_set = set()
    for field in order_data_fields:
        order_data_fields_set.add(field[0])
    for field in skip_fields:
        order_data_fields_set.remove(field)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order_id,
            'state': 'close_money',
            'payload': {'problems': []},
        },
    )
    if 'cargo_revision' in grocery_cold_storage.field_names:
        grocery_cold_storage.field_names.remove('cargo_revision')
        grocery_cold_storage.field_names.add('dispatch_cargo_revision')
    order_data_fields_set.add('additional_table')
    order_data_fields_set.add('auth_context_table')
    order_data_fields_set.add('feedback_table')
    order_data_fields_set.add('payments_table')
    order_data_fields_set.add('history_table')

    assert response.status_code == 200
    assert grocery_cold_storage.field_names == order_data_fields_set

    db.execute(GET_PG_DATA, [order_id])
    pg_order_data = db.fetchone()
    yt_order_data = grocery_cold_storage.response_value

    i = -1
    for k, pg_order_item in enumerate(pg_order_data):
        print(k, pg_order_item)
    for pg_order_item in pg_order_data:
        if order_data_fields[i][0] in skip_fields:
            continue

        i = i + 1
        if order_data_fields[i][0] == 'updated':
            continue
        if order_data_fields[i][0] == 'location':
            location_data = pg_order_item[1:-1].split(',')
            j = 0
            for item_location in location_data:
                location_data[j] = decimal.Decimal(item_location)
                j = j + 1
            assert location_data == yt_order_data[i]
            continue
        if isinstance(pg_order_item, datetime.datetime) and isinstance(
                yt_order_data[i], str,
        ):
            pg_order_item = pg_order_item.astimezone(
                datetime.timezone.utc,
            ).replace(tzinfo=None)
            yt_order_data[i] = _stringtime(yt_order_data[i])
        if isinstance(pg_order_item, decimal.Decimal) and isinstance(
                yt_order_data[i], str,
        ):
            yt_order_data[i] = decimal.Decimal(yt_order_data[i])

    db.execute(GET_PG_DATA_AUTH, [order_id])
    pg_order_auth_data = db.fetchone()
    yt_order_auth_data = grocery_cold_storage.response_value[
        len(pg_order_data) - len(skip_fields)
    ]
    assert json.loads(pg_order_auth_data[1]) == json.loads(
        yt_order_auth_data[0]['raw_auth_context'],
    )

    db.execute(GET_PG_DATA_FEEDBACK, [order_id])
    pg_order_feedback_data = db.fetchone()
    yt_order_feedback_data = grocery_cold_storage.response_value[
        len(pg_order_data) + 1 - len(skip_fields)
    ]
    assert pg_order_feedback_data[0] == yt_order_feedback_data[0]['order_id']
    assert (
        pg_order_feedback_data[1]
        == yt_order_feedback_data[0]['feedback_options']
    )
    assert pg_order_feedback_data[2] == yt_order_feedback_data[0]['comment']

    db.execute(GET_PG_DATA_ADDITIONAL, [order_id])
    pg_order_feedback_data = db.fetchone()
    yt_order_feedback_data = grocery_cold_storage.response_value[
        len(pg_order_data) + 2 - len(skip_fields)
    ]
    yt_order_feedback_data[0]['created'] = _stringtime(
        yt_order_feedback_data[0]['created'],
    )
    assert pg_order_feedback_data[0] == yt_order_feedback_data[0]['order_id']
    assert (
        pg_order_feedback_data[1]
        == yt_order_feedback_data[0]['appmetrica_device_id']
    )
    assert (
        pg_order_feedback_data[2]
        .astimezone(datetime.timezone.utc)
        .replace(tzinfo=None)
        == yt_order_feedback_data[0]['created']
    )
    assert pg_order_feedback_data[4] == yt_order_feedback_data[0]['app_name']
    assert pg_order_feedback_data[5] == json.loads(
        yt_order_feedback_data[0]['order_settings'],
    )
    assert pg_order_feedback_data[6].astimezone(datetime.timezone.utc).replace(
        tzinfo=None,
    ) == _stringtime(yt_order_feedback_data[0]['timeslot_start'])
    assert pg_order_feedback_data[7].astimezone(datetime.timezone.utc).replace(
        tzinfo=None,
    ) == _stringtime(yt_order_feedback_data[0]['timeslot_end'])
    assert (
        pg_order_feedback_data[8]
        == yt_order_feedback_data[0]['timeslot_request_kind']
    )
    assert (
        pg_order_feedback_data[9]
        == yt_order_feedback_data[0]['is_dispatch_request_started']
    )

    db.execute(GET_PG_DATA_PAYMENT, [order_id])
    pg_order_payment_data = db.fetchall()
    yt_order_payment_data = grocery_cold_storage.response_value[
        len(pg_order_data) + 3 - len(skip_fields)
    ]
    assert len(pg_order_payment_data) == len(yt_order_payment_data)
    i = 0
    for pg_order_payment_item in pg_order_payment_data:
        yt_order_payment_data[i]['created'] = _stringtime(
            yt_order_payment_data[i]['created'],
        )
        yt_order_payment_data[i]['updated'] = _stringtime(
            yt_order_payment_data[i]['updated'],
        )
        assert pg_order_payment_item[0] == yt_order_payment_data[i]['order_id']
        assert (
            pg_order_payment_item[1]
            == yt_order_payment_data[i]['operation_id']
        )
        assert (
            pg_order_payment_item[2]
            == yt_order_payment_data[i]['operation_type']
        )
        assert pg_order_payment_item[3] == yt_order_payment_data[i]['status']
        assert pg_order_payment_item[4] == yt_order_payment_data[i]['items']
        assert pg_order_payment_item[5] == yt_order_payment_data[i]['errors']
        assert (
            pg_order_payment_item[6]
            .astimezone(datetime.timezone.utc)
            .replace(tzinfo=None)
            == yt_order_payment_data[i]['created']
        )
        assert isinstance(pg_order_payment_item[7], datetime.datetime)
        assert (
            pg_order_payment_item[8]
            == yt_order_payment_data[i]['compensation_id']
        )
        i = i + 1

    db.execute(GET_PG_DATA_HISTORY, [order_id])
    pg_order_history_data = db.fetchall()
    yt_order_history_data = grocery_cold_storage.response_value[
        len(pg_order_data) + 4 - len(skip_fields)
    ]
    assert len(pg_order_history_data) == len(yt_order_history_data)
    i = 0
    for pg_order_history_item in pg_order_history_data:
        yt_order_history_data[i]['ts'] = _stringtime(
            yt_order_history_data[i]['ts'],
        )
        yt_order_history_data[i]['event_data'] = json.loads(
            yt_order_history_data[i]['event_data'],
        )
        assert pg_order_history_item[0] == yt_order_history_data[i]['order_id']
        assert (
            pg_order_history_item[1]
            .astimezone(datetime.timezone.utc)
            .replace(tzinfo=None)
            == yt_order_history_data[i]['ts']
        )
        assert (
            pg_order_history_item[2] == yt_order_history_data[i]['event_type']
        )
        assert (
            pg_order_history_item[3] == yt_order_history_data[i]['event_data']
        )
        i = i + 1


def _stringtime(timestring):
    try:
        return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S.%f')


@pytest.mark.parametrize(
    'problems, expected_status',
    [
        (
            [
                {
                    'type': 'some_problem_type',
                    'product_id': 'item-id-1',
                    'shelf_id': 'some_shelf_id',
                    'count': 1,
                    'reserve': 0,
                    'shelf_type': 'test_type',
                },
            ],
            None,
        ),
        (
            [
                {
                    'type': 'some_problem_type',
                    'product_id': 'item-id-1',
                    'shelf_id': 'some_shelf_id',
                    'count': 3,
                    'reserve': 0,
                    'shelf_type': 'test_type',
                },
            ],
            'failed',
        ),
        (
            [
                {
                    'count': 1,
                    'product_id': None,
                    'reserve': None,
                    'shelf_id': None,
                    'shelf_type': 'parcel',
                    'type': 'low',
                },
            ],
            'failed',
        ),
        ([{'123': '123'}], 'failed'),
    ],
)
@configs.GROCERY_ITEMS_CORRECTION_TICKET_PARAMETERS
@configs.GROCERY_ORDERS_ENABLE_CORRECTING_INSTEAD_CANCEL
@configs.GROCERY_ORDERS_WMS_PAUSE_DELAY
@configs.CORRECTING_ENABLED
async def test_wms_accepting_with_correct(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        processing,
        grocery_depots,
        tracker,
        problems,
        expected_status,
):
    order = models.Order(pgsql=pgsql, edit_status='in_progress')
    order.update()
    assert order.state == models.OrderState()

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': problems},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status=expected_status)

    if not expected_status:
        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
        event = events[0]

        correcting_items = [
            {'item_id': 'item-id-1', 'new_quantity': '2', 'old_quantity': '3'},
        ]

        expected_payload = {
            'order_id': order.order_id,
            'reason': 'correct',
            'correcting_items': correcting_items,
            'correcting_order_revision': order.order_revision,
            'flow_version': order.grocery_flow_version,
            'correcting_cart_version': order.cart_version,
            'correcting_type': 'remove',
            'correcting_source': 'system',
        }
        assert event.payload == expected_payload

        order.check_order_history(
            'order_correcting_status',
            {
                'correcting_type': 'remove',
                'correcting_items': [
                    {'item_id': 'item-id-1', 'quantity': '1'},
                ],
                'correcting_result': 'success',
                'to_order_correcting': 'correcting_started',
            },
        )
        order.check_order_history(
            'wms_pause', {'type': 'pause', 'delay': '60'},
        )

        assert tracker.times_called() == 1
        assert grocery_wms_gateway.times_set_pause_called() == 1


@pytest.mark.parametrize(
    'problems, expected_status',
    [
        (
            [
                {
                    'type': 'some_problem_type',
                    'product_id': 'item-id-1',
                    'shelf_id': 'some_shelf_id',
                    'count': 1,
                    'reserve': 0,
                    'shelf_type': 'test_type',
                },
            ],
            None,
        ),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=True)
@pytest.mark.now(consts.NOW)
@EVENT_POLICY_CONFIG
@configs.GROCERY_ITEMS_CORRECTION_TICKET_PARAMETERS
@configs.GROCERY_ORDERS_ENABLE_CORRECTING_INSTEAD_CANCEL
@configs.GROCERY_ORDERS_WMS_PAUSE_DELAY
@configs.CORRECTING_ENABLED
async def test_auto_correcting_with_failed_hold(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_depots,
        grocery_cart,
        problems,
        expected_status,
):
    order = models.Order(pgsql=pgsql)
    order.update()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': problems},
        },
    )
    assert response.status_code == 200

    order.update()
    assert order.state == models.OrderState(wms_reserve_status=None)
    assert order.edit_status == 'in_progress'

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {
                'operation_id': '1',
                'operation_type': 'create',
                'errors': [
                    {
                        'error_reason_code': 'not_enough_funds',
                        'payment_type': 'card',
                    },
                ],
            },
        },
    )

    assert response.status_code == 200
    order.update()
    assert order.state == models.OrderState(
        wms_reserve_status=None, hold_money_status='failed',
    )
    assert order.edit_status is None

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': []},
        },
    )

    assert response.status_code == 200
    order.update()
    assert order.state == models.OrderState(
        wms_reserve_status='success', hold_money_status='failed',
    )
    assert order.edit_status is None

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == 3

    event = events[1]

    assert event.item_id == order.order_id
    print(event.payload)
    assert event.payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'cancel_reason_type': 'payment_failed',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'hold_money_failed',
        'cancel_reason_meta': {'error_code': 'not_enough_funds'},
        'flow_version': 'grocery_flow_v1',
        'times_called': 0,
    }
