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
LEFT_AT_DOOR = True
MEET_OUTSIDE = True
NO_DOOR_CALL = True
POSTAL_CODE = 'SE16 3LR'
DELIVERY_COMMON_COMMENT = 'comment'
COMMENT = 'comment'
DEPOT_ID = '2809'
DISPATCH_ID = str(uuid.uuid4())

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'
DISPATCH_FLOW = 'grocery_dispatch'

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
        'comment': COMMENT,
        'left_at_door': LEFT_AT_DOOR,
        'meet_outside': MEET_OUTSIDE,
        'no_door_call': NO_DOOR_CALL,
        'postal_code': POSTAL_CODE,
    },
    'delivery_common_comment': DELIVERY_COMMON_COMMENT,
    'flow_version': PROCESSING_FLOW_VERSION,
    'dispatch_flow': DISPATCH_FLOW,
}

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


def get_event_buss_data(order_id, status):
    return {
        'data': '{"order_id":"%s","order_status":"%s"}' % (order_id, status),
        'name': 'order-state-changed-uber',
    }


@pytest.mark.config(GROCERY_ORDERS_WRITE_TO_STATUS_CHANGED_TOPIC=True)
@configs.GROCERY_DISPATCH_FLOW_EXPERIMENT
@configs.DISPATCH_SUPPLY_CONFIG
@configs.DISPATCH_CLAIM_CONFIG
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@experiments.available_payment_types(['googlepay'])
@DISPATCH_CONFIG_GENERAL
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('delivery_type', ['courier', 'pickup'])
async def test_order_cycle(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        delivery_type,
        grocery_payments,
        grocery_depots,
        grocery_wms_gateway,
        processing,
        grocery_dispatch,
        mockserver,
        load_json,
        yamaps_local,
        personal,
        mocked_time,
        experiments3,
        testpoint,
        grocery_supply,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_payment_method({'type': 'googlepay', 'id': 'id'})
    grocery_cart.set_delivery_zone_type('pedestrian')

    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)
    await taxi_grocery_orders.invalidate_caches()

    grocery_cart.set_delivery_type(delivery_type)

    submit_headers = headers.DEFAULT_HEADERS.copy()
    submit_headers['X-YaTaxi-Session'] = 'uber_eats:' + headers.USER_ID

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit', json=SUBMIT_BODY, headers=submit_headers,
    )

    assert response.status_code == 200
    order_id = response.json()['order_id']

    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.order_version == 0
    assert order.status == 'checked_out'
    assert order.cart_id == CART_ID
    assert order.left_at_door == LEFT_AT_DOOR
    assert order.meet_outside == MEET_OUTSIDE
    assert order.no_door_call == NO_DOOR_CALL
    assert order.status_updated is not None
    assert order.postal_code == POSTAL_CODE
    assert order.delivery_common_comment == DELIVERY_COMMON_COMMENT

    assert grocery_cart.checkout_times_called() == 1
    grocery_cart.flush_all()

    assert _get_last_processing_payloads(processing, order, count=3) == [
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

    @testpoint('status_changed_event')
    def commit_reserving(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'reserving',
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

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

    assert commit_reserving.times_called == 1

    assert response.status_code == 200
    order.update()

    assert order.order_version == 1
    assert order.status == 'reserving'
    assert order.status_updated is not None

    assert grocery_wms_gateway.times_mock_order_add() == 1

    # Check that payment_timeout event has got to processing
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

    @testpoint('status_changed_event')
    def commit_reserved(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'reserved',
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'hold_money',
            'payload': {'success': True},
        },
    )

    assert commit_reserved.times_called == 1

    assert response.status_code == 200
    order.update()

    assert order.order_version == 4
    assert order.status == 'reserved'

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

    @testpoint('status_changed_event')
    def commit_assembling(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'assembling',
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/assemble',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': PROCESSING_FLOW_VERSION,
            'payload': {},
        },
    )

    assert commit_assembling.times_called == 1

    assert response.status_code == 200

    order.update()
    assert order.status == 'assembling'
    assert order.order_version == 5

    assert order.status_updated is not None
    assert grocery_wms_gateway.times_assemble_called() == 1

    notification_result = _get_last_processing_payloads(
        processing,
        order,
        count=1,
        queue='processing_non_critical',
        use_default_skip_keys=False,
    )[0]

    notification_expected = {
        'order_id': order.order_id,
        'reason': 'order_notification',
        'deadline': (
            datetime.datetime.now() + datetime.timedelta(minutes=3)
        ).isoformat(),
        'payload': {},
        'code': 'assembling',
    }

    order_info_expected = {
        'app_info': headers.APP_INFO,
        'yandex_uid': headers.YANDEX_UID,
        'country_iso3': 'RUS',
        'currency_code': 'RUB',
        'depot_id': DEPOT_ID,
        'eats_user_id': 'eats-user-id',
        'leave_at_door': LEFT_AT_DOOR,
        'locale': 'ru',
        'order_id': order.order_id,
        'personal_phone_id': 'personal-phone-id',
        'region_id': 213,
        'taxi_user_id': 'user-id',
    }

    processing_noncrit.check_push_notification(
        notification_result, notification_expected,
    )

    processing_noncrit.check_notification_order_info(
        notification_result['order_info'], order_info_expected, False,
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

        assert grocery_wms_gateway.times_set_eda_status_called() == 1

        non_crit_payloads = _get_last_processing_payloads(
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

    @testpoint('status_changed_event')
    def commit_assembled(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'assembled',
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )

    assert commit_assembled.times_called == 1

    assert response.status_code == 200

    order.update()
    assert order.status == 'assembled'
    assert order.order_version == 7
    assert order.status_updated is not None

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
    if delivery_type == 'courier':

        @testpoint('status_changed_event')
        def commit_delivering(data):
            assert data == {
                'order_id': order.order_id,
                'order_status': 'delivering',
                'yandex_uid': headers.YANDEX_UID,
                'timestamp': consts.NOW,
            }

        dispatch_info = order.dispatch_status_info
        dispatch_info.dispatch_status = 'delivering'
        order.upsert(dispatch_status_info=dispatch_info)

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
    if delivery_type == 'pickup':
        assert order.status == 'assembled'
        assert order.order_version == 7

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

        assert _get_last_processing_payloads(processing, order, count=1) == [
            {
                'order_id': order.order_id,
                'reason': 'close',
                'flow_version': PROCESSING_FLOW_VERSION,
                'is_canceled': False,
                'idempotency_token': '{}-close-due'.format(
                    order.idempotency_token,
                ),
            },
        ]
    else:
        assert commit_delivering.times_called == 1
        assert order.status == 'delivering'
        assert order.order_version == 8

    # Close handle from processing --------------------------------------------
    @testpoint('status_changed_event')
    def commit_closed(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'closed',
            'yandex_uid': headers.YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'payload': {},
            'idempotency_token': '{}-close'.format(order.idempotency_token),
        },
    )

    assert commit_closed.times_called == 1

    assert response.status_code == 200

    order.update()
    assert order.status == 'closed'
    assert order.status_updated is not None

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


def _get_last_processing_payloads(
        processing,
        order,
        count=1,
        queue='processing',
        use_default_skip_keys=True,
):
    if not use_default_skip_keys:
        return helpers.get_last_processing_payloads(
            processing, order.order_id, count=count, queue=queue, skip_keys=(),
        )
    return helpers.get_last_processing_payloads(
        processing, order.order_id, count=count, queue=queue,
    )


def _get_last_processing_events(
        processing,
        order,
        count=1,
        queue='processing',
        use_default_skip_keys=True,
):
    if not use_default_skip_keys:
        return helpers.get_last_processing_events(
            processing, order.order_id, count=count, queue=queue, skip_keys=(),
        )
    return helpers.get_last_processing_events(
        processing, order.order_id, count=count, queue=queue,
    )
