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


DISPATCH_ID = str(uuid.uuid4())

PROCESSING_FLOW_VERSION = 'postponed_order_no_payment_flow_v1'
DISPATCH_FLOW = 'grocery_dispatch'

CART_ID = 'a49609bd-741d-410e-9f04-476f46ad43c7'
REGION_ID = 213
DEPOT_ID = '301924'
YANDEX_UID = '123378'
PERSONAL_PHONE_ID = '37281ejwxdewmo'
LOCALE = 'ru'
IDEMPOTENCY_TOKEN = 's6372e231'
MARKET_BATCHING_TAGS = ['market_batching']

LOCATION_IN_RUSSIA = [37, 55]
PLACE_ID = 'yamaps://12345'

POSITION = {'location': LOCATION_IN_RUSSIA, 'place_id': PLACE_ID}
CART_POSITION = {'location': LOCATION_IN_RUSSIA, 'uri': PLACE_ID}

TIMESLOT_START = '2020-03-13T09:50:00+00:00'
TIMESLOT_END = '2020-03-13T17:50:00+00:00'
TIMESLOT_REQUEST_KIND = 'wide_slot'

ITEMS = [
    {'id': 'item_1:st-pa', 'quantity': '1'},
    {'id': 'item_2:st-pa', 'quantity': '1'},
]

MAKE_REQUEST = {
    'position': POSITION,
    'yandex_uid': YANDEX_UID,
    'personal_phone_id': PERSONAL_PHONE_ID,
    'locale': LOCALE,
    'items': ITEMS,
    'timeslot': {'start': TIMESLOT_START, 'end': TIMESLOT_END},
    'request_kind': TIMESLOT_REQUEST_KIND,
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
DEFAULT_ORDER_TIMEOUT_MINUTES = 100


def get_event_buss_data(order_id, status):
    return {
        'data': '{"order_id":"%s","order_status":"%s"}' % (order_id, status),
        'name': 'order-state-changed-uber',
    }


@pytest.mark.config(GROCERY_ORDERS_WRITE_TO_STATUS_CHANGED_TOPIC=True)
@pytest.mark.config(GROCERY_ORDERS_ALLOW_TO_USE_POSTPONED_FLOW=True)
@configs.GROCERY_DISPATCH_FLOW_EXPERIMENT
@configs.DISPATCH_SUPPLY_CONFIG
@configs.DISPATCH_CLAIM_CONFIG
@experiments.PAYMENT_TIMEOUT
@experiments.WMS_RESERVE_TIMEOUT
@experiments.available_payment_types(['googlepay'])
@DISPATCH_CONFIG_GENERAL
@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.now(consts.NOW)
async def test_order_cycle(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
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

    grocery_cart.set_delivery_type('courier')

    submit_headers = headers.DEFAULT_HEADERS.copy()
    submit_headers['X-YaTaxi-Session'] = 'uber_eats:' + headers.USER_ID

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/make',
        json=MAKE_REQUEST,
        headers={
            'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
            'X-YaTaxi-Session': 'uber_eats:123',
        },
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
            'yandex_uid': YANDEX_UID,
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

    wms_reserve_event = _get_last_processing_events(processing, order, 1)[0]
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
            datetime.datetime.strptime(TIMESLOT_END, '%Y-%m-%dT%H:%M:%S%z')
            + datetime.timedelta(minutes=DEFAULT_ORDER_TIMEOUT_MINUTES)
        ).isoformat()
    )

    # WMS success callback ----------------------------------------------------
    @testpoint('status_changed_event')
    def commit_reserved(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'reserved',
            'yandex_uid': YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'wms_accepting',
            'payload': {'problems': []},
        },
    )

    assert response.status_code == 200

    assert commit_reserved.times_called == 1

    order.update()
    assert order.status == 'reserved'
    assert order.order_version == 3

    postpone_payload = _get_last_processing_payloads(processing, order, 1)[0]
    assert postpone_payload == {
        'flow_version': PROCESSING_FLOW_VERSION,
        'order_id': order.order_id,
        'order_version': 3,
        'reason': 'postpone',
    }

    # Postpone handle from processing
    @testpoint('status_changed_event')
    def commit_postponed(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'postponed',
            'yandex_uid': YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/postpone',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': PROCESSING_FLOW_VERSION,
            'payload': {},
        },
    )

    assert commit_postponed.times_called == 1

    assert response.status_code == 200

    order.update()
    assert order.status == 'postponed'
    assert order.order_version == 4

    last_payload = _get_last_processing_payloads(processing, order, 1)[0]
    assert last_payload == {
        'flow_version': PROCESSING_FLOW_VERSION,
        'order_id': order.order_id,
        'reason': 'dispatch_request',
    }

    # register dispatch

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
        market_slot={
            'interval_start': TIMESLOT_START,
            'interval_end': TIMESLOT_END,
        },
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={'order_id': order.order_id, 'payload': {}},
    )

    assert response.status_code == 200

    order.update()

    assert order.dispatch_status_info.dispatch_id == DISPATCH_ID
    assert order.dispatch_status_info.dispatch_status == 'created'

    last_payload = _get_last_processing_payloads(processing, order, 1)[0]

    # check nothing was added in processing for postpone flow
    assert last_payload == {
        'flow_version': PROCESSING_FLOW_VERSION,
        'order_id': order.order_id,
        'reason': 'dispatch_request',
    }

    assert grocery_wms_gateway.times_set_eda_status_called() == 0

    non_crit_payloads = _get_last_processing_payloads(
        processing, order, queue='processing_non_critical', count=1,
    )
    assert non_crit_payloads == []

    # Postpone continue callback

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/continue',
        json={
            'order_id': order.order_id,
            'request_source': 'grocery_dispatch',
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200

    last_payload = _get_last_processing_payloads(processing, order, 1)[0]

    # check nothing was added in processing for postpone flow
    assert last_payload == {
        'flow_version': PROCESSING_FLOW_VERSION,
        'order_id': order.order_id,
        'reason': 'assemble_ready',
        'order_version': order.order_version,
    }

    # Assemble handle from processing ----------------------------------------

    grocery_wms_gateway.flush_all()

    @testpoint('status_changed_event')
    def commit_assembling(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'assembling',
            'yandex_uid': YANDEX_UID,
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

    processing_noncrit.check_push_notification(
        notification_result, notification_expected,
    )

    assert _get_last_processing_payloads(processing, order, 1) == [
        {
            'flow_version': order.grocery_flow_version,
            'order_id': order.order_id,
            'reason': 'dispatch_track',
            'times_called': 1,
        },
    ]

    grocery_payments.flush_all()

    # Assemble callback from WMS ----------------------------------------------

    @testpoint('status_changed_event')
    def commit_assembled(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'assembled',
            'yandex_uid': YANDEX_UID,
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

    dispatch_info = order.dispatch_status_info
    dispatch_info.dispatch_status = 'delivering'
    order.upsert(dispatch_status_info=dispatch_info)

    @testpoint('status_changed_event')
    def commit_delivering(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'delivering',
            'yandex_uid': YANDEX_UID,
            'timestamp': consts.NOW,
        }

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

    assert commit_delivering.times_called == 1
    assert order.status == 'delivering'
    assert order.order_version == 8

    # Close handle from processing --------------------------------------------

    @testpoint('status_changed_event')
    def commit_closed(data):
        assert data == {
            'order_id': order.order_id,
            'order_status': 'closed',
            'yandex_uid': YANDEX_UID,
            'timestamp': consts.NOW,
        }

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'payload': {},
        },
    )

    assert commit_closed.times_called == 1

    assert response.status_code == 200

    order.update()
    assert order.status == 'closed'
    assert order.status_updated is not None

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
