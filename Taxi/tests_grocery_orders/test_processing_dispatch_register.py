import datetime
import uuid

import pytest

from . import consts
from . import helpers
from . import models

DISPATCH_ID = str(uuid.uuid4())

GROCERY_ORDERS_ORDER_TIMEOUT = 2

DISPATCH_GENERAL_CONFIG = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': 5,
                'accept_language': 'en',
                'skip_door_to_door': False,
                'skip_client_notify': True,
                'skip_emergency_notify': False,
                'optional_return': False,
                'comment': 'Лавка',
                'user_name': 'Иван Иванович',
                'depot_name': 'ЯндексЛавка',
                'emergency_contact_name': 'Поддержка Лавки',
                'emergency_contact_phone': '+79991234567',
                'depot_skip_confirmation': True,
                'user_skip_confirmation': True,
                'use_time_intervals_perfect': True,
                'use_time_intervals_strict': True,
                'use_time_intervals_endpoint': True,
                'time_intervals_endpoint_perfect_span': 10,
                'time_intervals_endpoint_strict_span': 15,
                'send_items_weight': True,
                'send_items_size': True,
            },
        },
    ],
    is_config=True,
)


def _stringtime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


@DISPATCH_GENERAL_CONFIG
@pytest.mark.parametrize(
    'init_status, delivery_type, result_code, dispatch_times_called,'
    'dispatch_error_code',
    [
        ('assembling', 'pickup', 409, 0, None),
        ('assembling', 'courier', 200, 1, None),
        ('reserved', 'courier', 200, 1, None),
        ('assembled', 'courier', 200, 1, None),
        ('checked_out', 'courier', 409, 0, None),
        ('closed', 'courier', 409, 0, None),
        ('canceled', 'courier', 409, 0, None),
        ('pending_cancel', 'courier', 409, 0, None),
        ('assembling', 'courier', 500, 1, 400),
        ('assembling', 'courier', 500, 1, 406),
        ('assembling', 'courier', 500, 1, 409),
        ('assembling', 'courier', 500, 1, 500),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        grocery_supply,
        init_status,
        result_code,
        delivery_type,
        dispatch_times_called,
        dispatch_error_code,
        yamaps_local,
        experiments3,
        processing,
        grocery_wms_gateway,
):
    max_eta = 35
    exact_eta = 31
    min_eta = 25

    order = models.Order(
        pgsql=pgsql, status=init_status, dispatch_flow='grocery_dispatch',
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_order_conditions(
        delivery_cost='100',
        max_eta=max_eta,
        total_time=exact_eta,
        min_eta=min_eta,
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(delivery_type)
    grocery_cart.set_delivery_zone_type('pedestrian')

    items = [{**it.as_object()} for it in grocery_cart.get_items()]

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=items,
        status='idle',
        dispatch_id=DISPATCH_ID,
        performer_id='123',
        eats_profile_id='1010',
        create_error_code=dispatch_error_code,
        max_eta=max_eta,
        exact_eta=exact_eta,
        min_eta=min_eta,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == result_code
    assert grocery_dispatch.times_create_called() == dispatch_times_called

    if result_code == 200:
        order.update()

        assert order.dispatch_status_info.dispatch_id == DISPATCH_ID
        assert order.dispatch_status_info.dispatch_status == 'created'

        assert _get_last_processing_events(processing, order, 2) == [
            {
                'flow_version': order.grocery_flow_version,
                'order_id': order.order_id,
                'payload': {'success': True},
                'reason': 'setstate',
                'state': 'dispatch_requested',
            },
            {
                'flow_version': order.grocery_flow_version,
                'order_id': order.order_id,
                'reason': 'dispatch_track',
                'times_called': 1,
            },
        ]

        assert grocery_wms_gateway.times_set_eda_status_called() == 1

        non_crit_payloads = _get_last_processing_events(
            processing, order, queue='processing_non_critical', count=1,
        )

        assert non_crit_payloads[0] == {
            'order_id': order.order_id,
            'order_log_info': {
                'depot_id': order.depot_id,
                'order_state': 'dispatch_approved',
                'order_type': 'grocery',
            },
            'reason': 'status_change',
            'status_change': init_status,
        }


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=GROCERY_ORDERS_ORDER_TIMEOUT)
async def test_timeslot(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        grocery_supply,
        yamaps_local,
        experiments3,
        processing,
        grocery_wms_gateway,
        now,
):
    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    market_slot = {
        'interval_start': timeslot_start,
        'interval_end': timeslot_end,
    }

    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        dispatch_flow='grocery_dispatch',
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        timeslot_request_kind=timeslot_request_kind,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('courier')
    grocery_cart.set_delivery_zone_type('pedestrian')

    grocery_wms_gateway.set_reserve_timeout(
        (_stringtime(timeslot_end) - _stringtime(consts.NOW)).seconds // 60
        + GROCERY_ORDERS_ORDER_TIMEOUT,
    )

    items = [{**it.as_object()} for it in grocery_cart.get_items()]

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=items,
        status='idle',
        dispatch_id=DISPATCH_ID,
        performer_id='123',
        eats_profile_id='1010',
        market_slot=market_slot,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200
    assert grocery_dispatch.times_create_called() == 1


@pytest.mark.parametrize(
    'status',
    ['reserving', 'reserved', 'postponed', 'assembling', 'assembled'],
)
@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=GROCERY_ORDERS_ORDER_TIMEOUT)
async def test_postpone(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        status,
        processing,
        grocery_wms_gateway,
        now,
):
    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'

    market_slot = {
        'interval_start': timeslot_start,
        'interval_end': timeslot_end,
    }

    order = models.Order(
        pgsql=pgsql,
        status=status,
        dispatch_flow='grocery_dispatch',
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        grocery_flow_version='postponed_order_no_payment_flow_v1',
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('courier')
    grocery_cart.set_delivery_zone_type('pedestrian')

    grocery_wms_gateway.set_reserve_timeout(
        (_stringtime(timeslot_end) - _stringtime(consts.NOW)).seconds // 60
        + GROCERY_ORDERS_ORDER_TIMEOUT,
    )

    items = [{**it.as_object()} for it in grocery_cart.get_items()]

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=items,
        status='idle',
        dispatch_id=DISPATCH_ID,
        performer_id='123',
        eats_profile_id='1010',
        market_slot=market_slot,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={'order_id': order.order_id, 'payload': {}},
    )

    if status == 'postponed':
        assert response.status_code == 200
        assert grocery_dispatch.times_create_called() == 1
    else:
        assert response.status_code == 409
        assert grocery_dispatch.times_create_called() == 0

    assert list(processing.events(scope='grocery', queue='processing')) == []

    non_critical_events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert non_critical_events == []


@DISPATCH_GENERAL_CONFIG
@pytest.mark.parametrize('init_in_pg', [True, False])
async def test_no_overwrite_db_dispatch_info(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        processing,
        grocery_wms_gateway,
        init_in_pg,
):
    order = models.Order(
        pgsql=pgsql, status='assembling', dispatch_flow='grocery_dispatch',
    )

    if init_in_pg:
        order.upsert(
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_cargo_revision=1,
                dispatch_status='created',
                dispatch_cargo_status='accepted',
                dispatch_id=DISPATCH_ID,
            ),
        )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('courier')
    grocery_cart.set_delivery_zone_type('pedestrian')

    items = [{**it.as_object()} for it in grocery_cart.get_items()]

    grocery_dispatch.set_data(
        order_id=order.order_id,
        items=items,
        status='delivering',
        dispatch_id=DISPATCH_ID,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={'order_id': order.order_id, 'payload': {}},
    )

    order.update()

    if init_in_pg:
        assert order.dispatch_status_info.dispatch_status == 'created'
        assert grocery_dispatch.times_create_called() == 0
    else:
        assert order.dispatch_status_info.dispatch_status == 'delivering'
        assert grocery_dispatch.times_create_called() == 1

    assert response.status_code == 200


def _get_last_processing_events(
        processing, order, count=1, queue='processing',
):
    return helpers.get_last_processing_payloads(
        processing, order.order_id, count=count, queue=queue,
    )
