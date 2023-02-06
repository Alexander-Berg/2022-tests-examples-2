import datetime
import decimal
import uuid

import dateutil.parser
import pytest

from . import configs
from . import consts
from . import experiments
from . import headers
from . import helpers
from . import models
from . import processing_noncrit

CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
LOCATION = [37, 55]
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
DOORCODE = '42'
DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'
LEFT_AT_DOOR = False
COMMENT = 'comment'
DEPOT_ID = '2809'
DISPATCH_ID = str(uuid.uuid4())
WMS_DEPOT_ID = 'wms-depot-id'
SECONDS_IN_DAY = 86400

SUBMIT_BODY = {
    'cart_id': CART_ID,
    'cart_version': CART_VERSION,
    'offer_id': OFFER_ID,
    'position': {
        'location': LOCATION,
        'place_id': PLACE_ID,
        'floor': FLOOR,
        'flat': FLAT,
        'doorcode': DOORCODE,
        'doorcode_extra': DOORCODE_EXTRA,
        'building_name': BUILDING_NAME,
        'doorbell_name': DOORBELL_NAME,
        'left_at_door': LEFT_AT_DOOR,
        'comment': COMMENT,
    },
}

PROCESSING_FLOW_VERSION = 'grocery_flow_v1'

ASSEMBLING_ETA = 5
DISPATCH_CONFIG_GENERAL = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'assembling_eta': ASSEMBLING_ETA},
        },
    ],
    is_config=True,
)

DUE_ASSEMBLED_TIMEPOINT_DT = consts.NOW_DT + datetime.timedelta(
    minutes=ASSEMBLING_ETA,
)
DUE_ASSEMBLED_TIMEPOINT = DUE_ASSEMBLED_TIMEPOINT_DT.isoformat()

GROCERY_ORDERS_FINISH_ORDER_TIME_MINUTES_LIMIT = 180


@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@configs.GROCERY_DISPATCH_FLOW_EXPERIMENT
@configs.DISPATCH_SUPPLY_CONFIG
@configs.DISPATCH_CLAIM_CONFIG
@DISPATCH_CONFIG_GENERAL
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.parametrize('delivery_type', ['courier', 'pickup'])
async def test_order_cycle(
        taxi_grocery_orders,
        pgsql,
        delivery_type,
        grocery_cart,
        grocery_payments,
        grocery_dispatch,
        grocery_depots,
        grocery_wms_gateway,
        processing,
        grocery_supply,
        mockserver,
        load_json,
        yamaps_local,
        personal,
        mocked_time,
        experiments3,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_delivery_zone_type('pedestrian')

    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)
    await taxi_grocery_orders.invalidate_caches()

    grocery_cart.set_delivery_type(delivery_type)

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']

    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.order_version == 0
    assert order.status == 'checked_out'
    assert order.cart_id == CART_ID

    assert grocery_cart.checkout_times_called() == 1
    grocery_cart.flush_all()

    assert _get_last_processing_payloads(processing, order, count=2) == [
        {
            'order_id': order.order_id,
            'reason': 'created',
            'order_version': order.order_version,
        },
        {
            'order_id': order.order_id,
            'reason': 'cancel',
            'flow_version': PROCESSING_FLOW_VERSION,
            'cancel_reason_message': 'Order timed out',
            'payload': {
                'event_created': consts.NOW,
                'initial_event_created': consts.NOW,
            },
            'cancel_reason_type': 'timeout',
            'times_called': 0,
        },
    ]

    # Reserve order -----------------------------------------------------------
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )

    assert grocery_wms_gateway.times_mock_order_add() == 0
    assert grocery_payments.times_create_called() == 0

    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': PROCESSING_FLOW_VERSION,
            'payload': {},
        },
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    order.update()

    assert order.order_version == 1
    assert order.status == 'reserving'

    assert grocery_wms_gateway.times_mock_order_add() == 1
    assert grocery_payments.times_create_called() == 1

    last_events = _get_last_processing_events(processing, order, 2)

    wms_reserve_event = last_events[0]
    assert wms_reserve_event.payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': PROCESSING_FLOW_VERSION,
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
            + datetime.timedelta(seconds=consts.WMS_RESERVE_TIMEOUT_SECONDS)
        ).isoformat()
    )

    payment_event = last_events[1]
    assert payment_event.payload == {
        'order_id': order.order_id,
        'reason': 'cancel',
        'flow_version': PROCESSING_FLOW_VERSION,
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

    # WMS success callback ----------------------------------------------------

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
    assert order.status == 'reserving'
    assert order.order_version == 2

    # Hold money success callback ---------------------------------------------

    grocery_payments.flush_all()
    assert grocery_payments.times_clear_called() == 0

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

    assert order.order_version == 4

    # After everything is OK, checking assemble event to processing
    assert _get_last_processing_payloads(processing, order, 1) == [
        {
            'order_id': order.order_id,
            'reason': 'assemble_ready',
            'flow_version': PROCESSING_FLOW_VERSION,
            'order_version': order.order_version,
        },
    ]

    # Assemble handle from processing ----------------------------------------

    grocery_wms_gateway.flush_all()
    assert grocery_wms_gateway.times_assemble_called() == 0

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': PROCESSING_FLOW_VERSION,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.status == 'assembling'
    assert order.order_version == 5

    assert grocery_wms_gateway.times_assemble_called() == 1

    notification_result = _get_last_processing_payloads(
        processing, order, count=1, queue='processing_non_critical',
    )[0]
    notification_expected = {
        'order_id': order.order_id,
        'reason': 'order_notification',
        'payload': {},
        'code': 'assembling',
    }
    processing_noncrit.check_push_notification(
        notification_result, notification_expected,
    )

    if delivery_type == 'courier':
        assert _get_last_processing_payloads(processing, order, 1) == [
            {
                'order_id': order.order_id,
                'reason': 'dispatch_request',
                'flow_version': PROCESSING_FLOW_VERSION,
                'due_time_point': DUE_ASSEMBLED_TIMEPOINT,
            },
        ]

    grocery_payments.flush_all()

    # Assemble callback from WMS ----------------------------------------------

    if delivery_type == 'courier':
        items = [{**it.as_object()} for it in grocery_cart.get_items()]

        grocery_dispatch.set_data(
            order_id=order.order_id,
            items=items,
            dispatch_id=DISPATCH_ID,
            performer_contact_phone='777',
            performer_contact_ext='777',
            performer_id='123',
            eats_profile_id='1010',
            status='scheduled',
            eta=300,
        )

        response = await taxi_grocery_orders.post(
            '/processing/v1/dispatch/register',
            json={'order_id': order.order_id, 'payload': {}},
        )

        assert response.status_code == 200

        order.update()

        assert order.dispatch_status_info.dispatch_id == DISPATCH_ID
        assert order.dispatch_status_info.dispatch_status == 'created'

        assert _get_last_processing_payloads(processing, order, 2) == [
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

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )
    assert response.status_code == 200

    order.update()
    assert order.status == 'assembled'
    assert order.order_version == 7

    # After assemble is OK, checking dispatch event to processing
    assert _get_last_processing_payloads(processing, order) == [
        {
            'order_id': order.order_id,
            'reason': 'dispatch_ready',
            'flow_version': PROCESSING_FLOW_VERSION,
            'order_version': order.order_version,
        },
    ]

    # Dispatch handle from processing -----------------------------------------

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': PROCESSING_FLOW_VERSION,
            'payload': {},
        },
    )
    assert response.status_code == 200

    order.update()
    if delivery_type == 'courier':
        assert order.status == 'delivering'
        assert order.order_version == 8
    else:
        assert order.status == 'assembled'
        assert order.order_version == 7

        assert _get_last_processing_payloads(processing, order, count=1) == [
            {
                'order_id': order.order_id,
                'reason': 'close',
                'flow_version': PROCESSING_FLOW_VERSION,
                'is_canceled': False,
                'idempotency_token': 'token-close-due',
            },
        ]

        notification_result = _get_last_processing_payloads(
            processing, order, count=1, queue='processing_non_critical',
        )[0]
        notification_expected = {
            'code': 'ready_for_pickup',
            'order_id': order.order_id,
            'payload': {},
            'reason': 'order_notification',
        }
        processing_noncrit.check_push_notification(
            notification_result, notification_expected,
        )

    # Close handle from processing --------------------------------------------

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'payload': {},
            'idempotency_token': 'token-close',
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.status == 'closed'
    if delivery_type == 'pickup':
        assert order.order_version == 8
    else:
        assert order.order_version == 9

    assert _get_last_processing_payloads(processing, order) == [
        {
            'order_id': order.order_id,
            'reason': 'finish',
            'deadline': (
                consts.NOW_DT
                + datetime.timedelta(
                    minutes=GROCERY_ORDERS_FINISH_ORDER_TIME_MINUTES_LIMIT,
                )
            ).isoformat(),
        },
    ]

    # Finish handle from processing -------------------------------------------

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200
    order.update()

    assert order.finished == consts.NOW_DT


@DISPATCH_CONFIG_GENERAL
@pytest.mark.now(consts.NOW)
@processing_noncrit.NOTIFICATION_CONFIG
async def test_send_order_info_in_created_order_cycle_event(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_wms_gateway,
        processing,
        mockserver,
        load_json,
        yamaps_local,
        personal,
        mocked_time,
        experiments3,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_delivery_type('courier')
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, depot_id=WMS_DEPOT_ID)
    await taxi_grocery_orders.invalidate_caches()

    grocery_cart.set_delivery_type('courier')
    grocery_cart.set_order_conditions(
        delivery_cost=100, max_eta=40, min_eta=10,
    )

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']

    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.order_version == 0
    assert order.status == 'checked_out'
    assert order.cart_id == CART_ID

    assert grocery_cart.checkout_times_called() == 1
    grocery_cart.flush_all()

    # Extract first processing event
    event = _get_last_processing_payloads(
        processing, order, count=helpers.ALL_EVENTS, skip_keys=(),
    )[0]

    assert event['order_id'] == order.order_id
    assert event['reason'] == 'created'
    assert event['order_version'] == order.order_version
    assert 'order_info' in event
    order_info = event['order_info']
    assert order_info['order_id'] == order.order_id
    assert order_info['short_order_id'] == order.short_order_id
    assert decimal.Decimal(order_info['client_price']) == order.client_price
    assert order_info['legacy_depot_id'] == order.depot_id
    assert order_info['depot_id'] == WMS_DEPOT_ID
    assert dateutil.parser.parse(order_info['created']) == order.created
    assert dateutil.parser.parse(order_info['due']) == order.due
    assert order_info['cart_id'] == order.cart_id
    assert order_info['offer_id'] == order.offer_id
    assert order_info['locale'] == order.locale
    assert order_info['app_info'] == order.app_info
    assert order_info['city'] == order.city
    assert order_info['street'] == order.street
    assert order_info['house'] == order.house
    assert order_info['flat'] == order.flat
    assert order_info['doorcode'] == order.doorcode
    assert order_info['location'] == order.location_as_point()
    assert order_info['floor'] == order.floor
    assert order_info['comment'] == order.comment
    assert order_info['grocery_flow_version'] == order.grocery_flow_version
    assert order_info['country'] == order.country
    assert order_info['currency'] == order.currency
    assert order_info['region_id'] == order.region_id
    assert order_info['yandex_uid'] == order.yandex_uid
    assert order_info['taxi_user_id'] == order.taxi_user_id
    assert order_info['eats_user_id'] == order.eats_user_id
    assert order_info['phone_id'] == order.phone_id
    assert order_info['personal_phone_id'] == order.personal_phone_id
    assert order_info['place_id'] == order.place_id
    assert order_info['delivery_type'] == 'courier'
    assert order_info['max_eta'] == 40
    assert order_info['min_eta'] == 10


def _get_last_processing_payloads(
        processing, order, count=1, queue='processing', **kwargs,
):
    return helpers.get_last_processing_payloads(
        processing, order.order_id, count=count, queue=queue, **kwargs,
    )


def _get_last_processing_events(
        processing, order, count=1, queue='processing', **kwargs,
):
    return helpers.get_last_processing_events(
        processing, order.order_id, count=count, queue=queue, **kwargs,
    )
