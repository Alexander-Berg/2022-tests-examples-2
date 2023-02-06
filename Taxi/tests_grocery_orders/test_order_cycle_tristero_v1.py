import datetime
import uuid

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

PROCESSING_FLOW_VERSION = 'tristero_flow_v1'

SUBMIT_BODY = {
    'cart_id': CART_ID,
    'cart_version': CART_VERSION,
    'offer_id': OFFER_ID,
    'flow_version': PROCESSING_FLOW_VERSION,
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

DUE_ASSEMBLED_TIMEPOINT_DT = consts.NOW_DT + datetime.timedelta(
    minutes=configs.ASSEMBLING_ETA,
)
DUE_ASSEMBLED_TIMEPOINT = DUE_ASSEMBLED_TIMEPOINT_DT.isoformat()


@configs.GROCERY_DISPATCH_FLOW_EXPERIMENT
@experiments.WMS_RESERVE_TIMEOUT
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_SUPPLY_CONFIG
@configs.DISPATCH_CLAIM_CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('delivery_type', ['courier', 'pickup'])
@processing_noncrit.NOTIFICATION_CONFIG
async def test_order_cycle(
        taxi_grocery_orders,
        pgsql,
        delivery_type,
        grocery_cart,
        grocery_payments,
        grocery_depots,
        grocery_supply,
        grocery_wms_gateway,
        processing,
        mockserver,
        load_json,
        yamaps_local,
        grocery_dispatch,
        personal,
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

    # Checks create event to processing
    assert _get_last_processing_events(processing, order, count=2) == [
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

    assert _get_last_processing_events(processing, order, count=1) == [
        {
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
        },
    ]

    assert response.status_code == 200
    order.update()

    assert order.order_version == 1
    assert order.status == 'reserving'

    assert grocery_wms_gateway.times_mock_order_add() == 1

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
    assert order.status == 'reserved'
    assert order.order_version == 3

    # After everything is OK, checking assemble event to processing
    assert _get_last_processing_events(processing, order, 1) == [
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
    assert order.order_version == 4

    assert grocery_wms_gateway.times_assemble_called() == 1

    notification_result = _get_last_processing_events(
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
        assert _get_last_processing_events(processing, order, 1) == [
            {
                'order_id': order.order_id,
                'reason': 'dispatch_request',
                'flow_version': PROCESSING_FLOW_VERSION,
                'due_time_point': DUE_ASSEMBLED_TIMEPOINT,
            },
        ]

    # Register dispatch -------------------------------------------------------

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
            'status_change': 'assembling',
        }

    # Assemble callback from WMS ----------------------------------------------

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
    if delivery_type == 'courier':
        assert order.order_version == 6
    else:
        assert order.order_version == 6

    # After assemble is OK, checking dispatch event to processing
    assert _get_last_processing_events(processing, order) == [
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
        assert order.order_version == 7
    else:
        assert order.status == 'assembled'
        assert order.order_version == 6

        notification_result = _get_last_processing_events(
            processing, order, count=1, queue='processing_non_critical',
        )[0]
        notification_expected = {
            'code': 'ready_for_pickup',
            'order_id': order.order_id,
            'payload': {},
            'reason': 'order_notification',
            'deadline': (
                datetime.datetime.now() + datetime.timedelta(minutes=3)
            ).isoformat(),
        }
        processing_noncrit.check_push_notification(
            notification_result, notification_expected,
        )

        assert _get_last_processing_events(processing, order, count=1) == [
            {
                'order_id': order.order_id,
                'reason': 'close',
                'flow_version': PROCESSING_FLOW_VERSION,
                'is_canceled': False,
                'idempotency_token': 'token-close-due',
            },
        ]

    # Close handle from processing --------------------------------------------

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'flow_version': PROCESSING_FLOW_VERSION,
            'is_canceled': False,
            'payload': {},
        },
    )

    assert response.status_code == 200

    order.update()
    assert order.status == 'closed'
    if delivery_type == 'pickup':
        assert order.order_version == 7
    else:
        assert order.order_version == 8

    # because it's without payment
    assert grocery_payments.times_create_called() == 0


def _get_last_processing_events(
        processing, order, count=1, queue='processing',
):
    return helpers.get_last_processing_payloads(
        processing, order.order_id, count=count, queue=queue,
    )
