# pylint: disable=too-many-lines
import copy
import datetime
import decimal
import json

import pytest

from . import configs
from . import consts
from . import experiments
from . import headers
from . import helpers
from . import models
from . import processing_noncrit
from .plugins import mock_grocery_payments


@experiments.GOAL_RESERVATION
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'init_status,status_code',
    [('closed', 409), ('draft', 200), ('checked_out', 200)],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_goals,
        grocery_wms_gateway,
        grocery_depots,
        grocery_payments,
        processing,
        init_status,
        status_code,
        transactions_eda,
):
    reward_sku = 'reward_item_id:st-gr'
    wms_logistic_tag = ['any_tag']
    order = models.Order(
        pgsql=pgsql, status=init_status, wms_logistic_tags=wms_logistic_tag,
    )
    grocery_wms_gateway.set_wms_logistic_tag(wms_logistic_tag)

    version = order.order_version
    assert order.status == init_status

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem('parcel_item_id:st-pa'),
            models.GroceryCartItem(reward_sku, quantity='1'),
        ],
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_goals.skus = [reward_sku]
    grocery_goals.order_id = order.order_id
    reserve_called = grocery_goals.reserve_times_called()

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    order.update()

    assert response.status_code == status_code
    if status_code == 200:
        assert order.status == 'reserving'
        if init_status != 'reserving':
            assert grocery_wms_gateway.times_mock_order_add() == 1
            assert grocery_payments.times_create_called() == 1
            assert order.order_version == version + 1

        setstate_event = processing_noncrit.check_noncrit_event(
            processing, order.order_id, 'tristero_setstate',
        )
        assert setstate_event is not None
        assert grocery_goals.reserve_times_called() - reserve_called == 1

        last_events = helpers.get_last_processing_events(
            processing=processing,
            order_id=order.order_id,
            queue='processing',
            count=2,
        )

        wms_reserve_event = last_events[0]
        assert wms_reserve_event.payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': 'WMS reserve timed out',
            'cancel_reason_meta': {'type': 'wms'},
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_type': 'timeout',
            'times_called': 0,
        }

        assert (
            wms_reserve_event.due
            == (
                consts.NOW_DT
                + datetime.timedelta(
                    seconds=consts.WMS_RESERVE_TIMEOUT_SECONDS,
                )
            ).isoformat()
        )

        payment_event = last_events[1]
        assert payment_event.payload == {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': 'grocery_flow_v1',
            'cancel_reason_message': 'Payment timed out',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_type': 'payment_timeout',
            'times_called': 0,
        }

        assert (
            payment_event.due
            == (
                consts.NOW_DT
                + datetime.timedelta(seconds=consts.PAYMENT_TIMEOUT_SECONDS)
            ).isoformat()
        )
    else:
        assert grocery_goals.reserve_times_called() == reserve_called
        assert grocery_wms_gateway.times_assemble_called() == 0
        assert grocery_payments.times_cancel_called() == 0
        assert order.status == init_status
        assert order.order_version == version


@pytest.mark.parametrize('delivery_type', ['courier', 'rover'])
async def test_check_wms_request(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        delivery_type,
):
    max_eta = 15

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id='some_dispatch_id',
        dispatch_status='delivering',
        dispatch_cargo_status='new',
        dispatch_start_delivery_ts='2020-05-25T17:40:45+03:00',
    )
    order = models.Order(
        pgsql=pgsql,
        status='checked_out',
        dispatch_status_info=dispatch_status_info,
    )

    price = decimal.Decimal('12.34')
    quantity = decimal.Decimal('3')

    item_1 = models.GroceryCartItem(
        item_id='item-id-1', price=str(price), quantity=str(quantity),
    )
    item_2 = models.GroceryCartItem(
        item_id='item-id-1', price=str(price), quantity=str(quantity),
    )

    delivery_cost = 500

    full_sum = str(price * quantity * 2 + delivery_cost)
    grocery_cart.set_items(items=[item_1, item_2])

    grocery_cart.set_delivery_type(delivery_type=delivery_type)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(
        delivery_cost=delivery_cost, max_eta=max_eta, min_eta=10,
    )

    grocery_wms_gateway.check_reserve(
        items=[item_1, item_2],
        full_sum=full_sum,
        order=order,
        max_eta=max_eta,
        order_revision=str(order.order_revision),
        maybe_rover=(delivery_type == 'rover'),
        reserve_timeout=7 * 60,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert grocery_wms_gateway.times_mock_order_add() == 1


@experiments.GOAL_RESERVATION
@pytest.mark.now(consts.NOW)
async def test_wms_request_400(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_goals,
        grocery_wms_gateway,
        grocery_depots,
        processing,
):
    order = models.Order(pgsql=pgsql, status='checked_out')

    price = decimal.Decimal('12.34')
    quantity = decimal.Decimal('3')

    item_1 = models.GroceryCartItem(
        item_id='item-id-1', price=str(price), quantity=str(quantity),
    )
    item_2 = models.GroceryCartItem(
        item_id='item-id-1', price=str(price), quantity=str(quantity),
    )
    item_3 = models.GroceryCartItem(
        item_id='reward_item_id:st-gr',
        price=str(price),
        quantity=str(quantity),
    )

    grocery_cart.set_items(items=[item_1, item_2, item_3])
    goal_reserve_called = grocery_goals.reserve_times_called()

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_wms_gateway.set_http_resp(
        '{"code": "WMS_400", "message": "Bad request"}', 400,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 409
    assert grocery_wms_gateway.times_mock_order_add() == 1

    events = list(processing.events(scope='grocery', queue='processing'))

    assert grocery_goals.reserve_times_called() == goal_reserve_called
    assert len(events) == 2
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


@experiments.GOAL_RESERVATION
@pytest.mark.parametrize('delta, status_code', [(0, 409), (1, 200), (2, 409)])
async def test_idempotency(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_payments,
        grocery_depots,
        delta,
        status_code,
):
    request_order_version = 1
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        order_version=request_order_version + delta,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem('parcel_item_id:st-pa'),
            models.GroceryCartItem('reward_item_id:st-gr'),
        ],
    )

    version_before_request = order.order_version

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': request_order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == status_code
    assert order.status == 'reserving'

    assert grocery_wms_gateway.times_mock_order_add() == 0
    assert grocery_payments.times_create_called() == 0
    assert order.order_version == version_before_request


async def test_wms_failed(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
):
    order = models.Order(pgsql=pgsql, status='checked_out')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    version = order.order_version
    grocery_wms_gateway.set_fail_flag(True)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
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
    assert order.status == 'checked_out'


@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
async def test_wms_cancelled(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_wms_gateway,
        grocery_payments,
        grocery_depots,
):
    order = models.Order(pgsql=pgsql)
    order.update()
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': []},
        },
    )

    assert response.status_code == 200

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
    assert order.state == models.OrderState(wms_reserve_status='cancelled')

    assert grocery_wms_gateway.times_close_called() == 0
    assert grocery_payments.times_cancel_called() == 0

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
        'cancel_reason_message': 'order_cancelled',
        'times_called': 0,
    }


async def test_desired_status_canceled(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
):
    order = models.Order(
        pgsql=pgsql, status='checked_out', desired_status='canceled',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    version = order.order_version
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 409
    order.update()

    assert order.order_version == version
    assert order.status == 'checked_out'

    assert grocery_wms_gateway.times_close_called() == 0


async def test_start_hold_money(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        grocery_payments,
):
    order = models.Order(pgsql=pgsql, status='checked_out')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem('item_id_1', price='10', quantity='2'),
            models.GroceryCartItem('item_id_2', price='100', quantity='1'),
        ],
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200
    order.update()

    assert grocery_payments.times_create_called() == 1


@pytest.mark.parametrize(
    'flow_version, status_code',
    [('grocery_flow_v1', 500), ('tristero_flow_v1', 200)],
)
async def test_grocery_payments_tristero(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        flow_version,
        status_code,
):
    order = models.Order(
        pgsql=pgsql, status='checked_out', grocery_flow_version=flow_version,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': flow_version,
            'payload': {},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == status_code


@pytest.mark.parametrize('handle_paid_delivery', [False, True])
async def test_start_hold_money_paid_delivery(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        grocery_depots,
        grocery_payments,
        experiments3,
        handle_paid_delivery,
):
    configs.handle_paid_delivery(experiments3, handle_paid_delivery)

    delivery_cost = '100'
    payment_method = {
        'type': 'card',
        'id': 'test_payment_method_id',
        'meta': {'card': {'verified': False, 'is_yandex_card': True}},
    }

    order = models.Order(pgsql=pgsql, status='checked_out')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    items = [
        models.GroceryCartItem('item_id_1', price='10', quantity='2'),
        models.GroceryCartItem('item_id_2', price='100', quantity='1'),
    ]

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(items)
    grocery_cart.set_payment_method(payment_method)
    grocery_cart.set_order_conditions(delivery_cost=delivery_cost)

    items_with_delivery = copy.deepcopy(grocery_cart.get_items())

    if handle_paid_delivery:
        items_with_delivery.append(
            models.GroceryCartItem(
                'delivery', price=delivery_cost, quantity='1', currency='RUB',
            ),
        )

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_payments.check_create(
        items_by_payment_types=[
            mock_grocery_payments.get_items_by_payment_type(
                items_with_delivery, payment_method,
            ),
        ],
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200

    assert grocery_payments.times_create_called() == 1


@pytest.mark.parametrize('handle_paid_delivery', [False, True])
async def test_exchange_flow_reserve(
        taxi_grocery_orders,
        experiments3,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        handle_paid_delivery,
):
    configs.handle_paid_delivery(experiments3, handle_paid_delivery)
    item_id = 'item_id'
    item_price = 10
    delivery_cost = 3
    exchange_rate = 15
    tested_from_currency = 'tested_currency'

    payment_method = {
        'type': 'card',
        'id': 'test_payment_method_id',
        'meta': {'card': {'issuer_country': 'RUS'}},
    }
    order = models.Order(
        pgsql=pgsql,
        status='checked_out',
        grocery_flow_version='exchange_currency',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    sub_item = models.GroceryCartSubItem(
        item_id + '_0',
        price=str(item_price),
        full_price='1',
        quantity='2',
        price_exchanged=str(item_price * exchange_rate),
    )

    items_v2 = models.GroceryCartItemV2(item_id, sub_items=[sub_item])

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items_v2([items_v2])
    grocery_cart.set_payment_method(payment_method=payment_method)
    grocery_cart.set_currency_settings(
        currency_settings={
            'from_currency': tested_from_currency,
            'to_currency': 'ILS',
        },
    )
    grocery_cart.set_order_conditions(
        delivery_cost=delivery_cost,
        pricing={
            'item_id': 'delivery',
            'price': str(delivery_cost),
            'full_price': str(delivery_cost),
            'quantity': '1',
            'price_exchanged': str(delivery_cost * exchange_rate),
        },
    )

    items_by_payment_types = (
        mock_grocery_payments.get_items_v2_by_payment_type(
            items=grocery_cart.get_items_v2(),
            payment_method=payment_method,
            exchange_flow=True,
        )
    )

    if handle_paid_delivery:
        delivery_item = {
            'item_id': 'delivery',
            'price': str(delivery_cost * exchange_rate),
            'quantity': '1',
            'item_type': 'delivery',
        }
        items_by_payment_types['items'].append(delivery_item)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    grocery_payments.check_create(
        items_by_payment_types=[items_by_payment_types],
        currency=tested_from_currency,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'payload': {},
        },
    )

    assert response.status_code == 200
    assert grocery_payments.times_create_called() == 1


@pytest.mark.now(consts.NOW)
async def test_retry_interval(processing, _run_with_error):
    retry_count = 2
    event_policy = {
        'retry_count': retry_count,
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
    }
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='processing'))

    event_policy['retry_count'] += 1
    assert len(events) == 1
    assert events[0].payload == {
        'event_policy': event_policy,
        'order_id': order.order_id,
        'order_version': order.order_version,
        'reason': 'created',
    }

    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)


async def test_stop_after(
        _run_with_error,
        _retry_after_error,
        processing,
        mocked_time,
        grocery_depots,
        grocery_cart,
        pgsql,
):
    mocked_time.set(consts.NOW_DT)
    # Without retry_interval and error_after we cannot return 429 error, we
    # should return 500 to see it in alert chat/grafana.
    order = await _run_with_error(
        expected_code=500,
        event_policy={
            'stop_retry_after': {'minutes': consts.STOP_AFTER_MINUTES},
        },
    )

    # try again later, after "stop_after".
    await _retry_after_error(
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


async def test_error_after(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    mocked_time.set(consts.NOW_DT)
    # With `error_after` we don't want to see messages in alert chat, we want
    # to ignore problems until `error_after` happened.
    order = await _run_with_error(
        expected_code=429,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
    )

    await _retry_after_error(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_retry_after_error_behaviour(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }
    mocked_time.set(consts.NOW_DT)
    # With error after we don't want to see messages in alert chat, we want to
    # ignore problems until `error_after` happened.
    order = await _run_with_error(expected_code=200, event_policy=event_policy)

    events = list(processing.events(scope='grocery', queue='processing'))

    events_after_first_retry = 1

    assert len(events) == events_after_first_retry
    assert events[0].due == helpers.skip_minutes(consts.RETRY_INTERVAL_MINUTES)

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }

    await _retry_after_error(
        order=order,
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=500,
    )

    await _retry_after_error(
        order=order,
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy=event_policy,
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert len(events) == events_after_first_retry


@configs.GROCERY_ORDERS_ENABLED_WMS_TAGS
@pytest.mark.parametrize(
    'user_orders_count, has_parcel, tags',
    [
        (0, None, ['tag_zero']),
        (1, None, ['tag_one']),
        (None, 0, []),
        (None, 1, ['has_parcel_tag']),
    ],
)
async def test_wms_tags(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_wms_gateway,
        experiments3,
        grocery_marketing,
        grocery_depots,
        user_orders_count,
        has_parcel,
        tags,
):
    item_ids = ['item-id-1', 'item-id-2']
    if has_parcel:
        item_ids[0] = 'parcel-item-id:st-pa'

    if user_orders_count is not None:
        configs.set_user_orders_count(experiments3, user_orders_count, tags)
    else:
        configs.set_has_parcel_wms_tags(experiments3, tags)

    order = models.Order(pgsql=pgsql, status='checked_out')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    max_eta = 15
    price = decimal.Decimal('12.34')
    quantity = decimal.Decimal('3')
    delivery_cost = 500

    item_1 = models.GroceryCartItem(
        item_id=item_ids[0], price=str(price), quantity=str(quantity),
    )
    item_2 = models.GroceryCartItem(
        item_id=item_ids[1], price=str(price), quantity=str(quantity),
    )

    full_sum = str(price * quantity * 2 + delivery_cost)
    grocery_cart.set_items(items=[item_1, item_2])
    grocery_cart.set_order_conditions(
        delivery_cost=delivery_cost, max_eta=max_eta, min_eta=10,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    if user_orders_count is not None:
        grocery_marketing.add_user_tag(
            tag_name='total_orders_count',
            usage_count=user_orders_count,
            user_id=order.yandex_uid,
        )

    grocery_wms_gateway.check_reserve(
        items=[item_1, item_2],
        full_sum=full_sum,
        order=order,
        order_revision=str(order.order_revision),
        max_eta=max_eta,
        client_tags=tags,
        reserve_timeout=7 * 60,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
    )

    assert response.status_code == 200
    assert grocery_wms_gateway.times_mock_order_add() == 1


@pytest.fixture
def _retry_after_error(mocked_time, taxi_grocery_orders):
    return helpers.retry_processing(
        '/processing/v1/reserve', mocked_time, taxi_grocery_orders,
    )


@pytest.fixture
def _run_with_error(pgsql, grocery_depots, grocery_cart, taxi_grocery_orders):
    async def _do(expected_code, event_policy, times_called=1):
        order = models.Order(pgsql=pgsql, status='checked_out')
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_payment_method({'type': 'card', 'id': None})

        response = await taxi_grocery_orders.post(
            '/processing/v1/reserve',
            json={
                'order_id': order.order_id,
                'order_version': order.order_version,
                'times_called': times_called,
                'event_policy': event_policy,
                'payload': {},
            },
        )

        assert response.status_code == expected_code

        return order

    return _do


@experiments.GOAL_RESERVATION
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.now(consts.NOW)
async def test_error_on_goal_reserve_error(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_goals,
        grocery_wms_gateway,
        grocery_depots,
        grocery_payments,
        processing,
        transactions_eda,
):
    reward_sku = 'reward_item_id:st-gr'
    wms_logistic_tag = ['any_tag']
    order = models.Order(
        pgsql=pgsql, status='draft', wms_logistic_tags=wms_logistic_tag,
    )
    grocery_wms_gateway.set_wms_logistic_tag(wms_logistic_tag)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items(
        [
            models.GroceryCartItem('parcel_item_id:st-pa'),
            models.GroceryCartItem(reward_sku, quantity='1'),
        ],
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_goals.skus = [reward_sku]
    grocery_goals.order_id = order.order_id
    grocery_goals.response_http_code = 400
    grocery_goals.error_code = 'reward_already_reserved'
    grocery_goals.failed_skus = [reward_sku]
    reserve_called = grocery_goals.reserve_times_called()

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    order.update()

    assert response.status_code == 409
    assert grocery_goals.reserve_times_called() - reserve_called == 1

    basic_events = list(processing.events(scope='grocery', queue='processing'))
    assert basic_events[1].payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': 'grocery_flow_v1',
        'cancel_reason_type': 'failure',
        'payload': {
            'event_created': consts.NOW,
            'initial_event_created': consts.NOW,
        },
        'cancel_reason_message': 'reserving_reward_failed',
        'times_called': 0,
    }
