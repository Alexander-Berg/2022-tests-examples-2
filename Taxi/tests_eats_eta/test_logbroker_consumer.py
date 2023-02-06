import datetime
import json
from typing import Optional

import pytest

from . import utils

LOGBROKER_TOPIC = '/eda/processing/production/order-client-events'
CONSUMER = 'order-client-events-consumer'

LOGBROKER_TESTPOINT = 'logbroker_commit'
CONSUMER_TESTPOINT = 'eats-eta::events-consumed'
PROCESSING_TESTPOINT = 'eats-eta::event-processed'

CONSUMER_TASK = 'order-client-events-consumer-lb_consumer'

LB_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 100,
        'queue_timeout_ms': 1,
        'config_poll_period_ms': 1,
    },
}


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_type, delivery_type, eater_passport_uid, device_id, '
    'delivery_coordinates, courier_type, meta, '
    'delivery_slot_started_at, delivery_slot_finished_at',
    [
        [
            'native',
            'marketplace',
            'eater-passport-uid',
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [
            'retail',
            'native',
            None,
            'device-id',
            None,
            None,
            {
                'delivery_slot_started_at': '03-03-2022 19:00',
                'delivery_slot_finished_at': '03-03-2022 20:00',
            },
            '2022-03-03T19:00:00+03:00',
            '2022-03-03T19:00:00+02:00',
        ],
        [
            'shop',
            'native',
            None,
            None,
            {'lat': 56.789, 'lon': 34.567},
            None,
            {
                'delivery_slot_started_at': '03-03-2022 19:00',
                'delivery_slot_finished_at': '2022-03-03T23:00:00+06:00',
            },
            '2022-03-03T19:00:00+03:00',
            '2022-03-03T18:00:00+01:00',
        ],
        ['fast_food', 'native', None, None, None, 'bicycle', None, None, None],
    ],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_create_order(
        taxi_eats_eta,
        checkout,
        testpoint,
        stq,
        now_utc,
        redis_store,
        check_redis_value,
        make_order,
        db_select_orders,
        order_type,
        delivery_type,
        eater_passport_uid,
        device_id,
        delivery_coordinates: Optional[dict],
        courier_type,
        meta,
        delivery_slot_started_at,
        delivery_slot_finished_at,
):
    order_nr = 'order-nr'
    place_id = 123
    eater_id = 'eater-id'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')
    checkout.add_order_revision(order_nr, delivery_date=now_utc)

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    @testpoint(PROCESSING_TESTPOINT)
    def after_processing(_):
        pass

    event = utils.make_event(
        order_nr,
        created_at,
        eater_passport_uid=eater_passport_uid,
        device_id=device_id,
        courier_type=courier_type,
        delivery_coordinates=delivery_coordinates,
        place_id=str(place_id),
        eater_id=eater_id,
        order_type=order_type,
        delivery_type=delivery_type,
        meta=meta,
    )
    expected_order = make_order(
        order_nr=order_nr,
        order_status='created',
        created_at=created_at,
        eater_passport_uid=eater_passport_uid,
        device_id=device_id,
        delivery_coordinates=None
        if delivery_coordinates is None
        else '({},{})'.format(
            delivery_coordinates['lon'], delivery_coordinates['lat'],
        ),
        delivery_zone_courier_type=courier_type,
        place_id=place_id,
        eater_id=eater_id,
        order_type=order_type,
        delivery_type=delivery_type,
        delivery_date=now_utc,
        delivery_slot_started_at=delivery_slot_started_at,
        delivery_slot_finished_at=delivery_slot_finished_at,
    )
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()
    await after_processing.wait_call()

    assert stq.eats_eta_process_event.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == expected_order
    for key in utils.ORDER_CREATED_REDIS_KEYS:
        value = expected_order[key]
        check_redis_value(order_nr, key, value)
    complete_at = redis_store.get(
        utils.make_redis_key('complete_at', order_nr),
    )
    assert complete_at is not None


@utils.eats_eta_settings_config3()
@pytest.mark.parametrize(
    'order_type, delivery_type, eater_passport_uid, device_id, '
    'delivery_coordinates, courier_type',
    [
        ['native', 'marketplace', 'eater-passport-uid', None, None, None],
        ['retail', 'native', None, 'device-id', None, None],
        ['shop', 'native', None, None, {'lat': 56.789, 'lon': 34.567}, None],
        ['fast_food', 'native', None, None, None, 'bicycle'],
    ],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_create_order_failed_to_update_estimations(
        taxi_eats_eta,
        checkout,
        testpoint,
        stq,
        redis_store,
        check_redis_value,
        make_order,
        db_select_orders,
        order_type,
        delivery_type,
        eater_passport_uid,
        device_id,
        delivery_coordinates: Optional[dict],
        courier_type,
):
    order_nr = 'order-nr'
    place_id = 123
    eater_id = 'eater-id'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    @testpoint(PROCESSING_TESTPOINT)
    def after_processing(_):
        pass

    event = utils.make_event(
        order_nr,
        created_at,
        eater_passport_uid=eater_passport_uid,
        device_id=device_id,
        courier_type=courier_type,
        delivery_coordinates=delivery_coordinates,
        place_id=str(place_id),
        eater_id=eater_id,
        order_type=order_type,
        delivery_type=delivery_type,
    )
    expected_order = make_order(
        order_nr=order_nr,
        order_status='created',
        created_at=created_at,
        eater_passport_uid=eater_passport_uid,
        device_id=device_id,
        delivery_coordinates=None
        if delivery_coordinates is None
        else '({},{})'.format(
            delivery_coordinates['lon'], delivery_coordinates['lat'],
        ),
        delivery_zone_courier_type=courier_type,
        place_id=place_id,
        eater_id=eater_id,
        order_type=order_type,
        delivery_type=delivery_type,
    )
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()
    await after_processing.wait_call()

    assert stq.eats_eta_process_event.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 1
    kwargs = stq.eats_eta_update_estimations.next_call()['kwargs']
    assert kwargs['order_nr'] == order_nr

    assert db_select_orders(order_nr=order_nr)[0] == expected_order
    assert not redis_store.keys()


@utils.eats_eta_settings_config3(process_events=False)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_create_order_events_processing_disabled(
        taxi_eats_eta, testpoint, stq, db_select_orders,
):
    order_nr = 'order-nr'
    place_id = 123
    eater_id = 'eater-id'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    event = utils.make_event(
        order_nr,
        created_at,
        eater_passport_uid='eater-passport-uid',
        device_id='device-id',
        courier_type=None,
        delivery_coordinates={'lat': 56.789, 'lon': 34.567},
        place_id=str(place_id),
        eater_id=eater_id,
        order_type='native',
        delivery_type='native',
    )
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()

    assert stq.eats_eta_process_event.times_called == 0

    assert not db_select_orders()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event, place_id, order_type, delivery_type, shipping_type, '
    'stq_called',
    [
        ['unknown', '123', 'native', 'native', 'delivery', 0],
        ['promise_changed', '123', 'native', 'native', 'delivery', 0],
        ['ready_to_send', '123', 'native', 'native', 'delivery', 0],
        ['created', 'abc', 'native', 'native', 'delivery', 1],
        ['created', '123', 'unknown', 'native', 'delivery', 0],
        ['created', '123', 'lavka', 'native', 'delivery', 0],
        ['created', '123', 'pharmacy', 'native', 'delivery', 0],
        ['created', '123', 'fuel_food', 'native', 'delivery', 0],
        ['created', '123', 'native', 'unknown', 'delivery', 0],
        ['created', '123', 'native', 'native', 'unknown', 0],
    ],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_create_order_bad_event(
        taxi_eats_eta,
        testpoint,
        stq,
        redis_store,
        db_select_orders,
        order_event,
        place_id,
        order_type,
        delivery_type,
        shipping_type,
        stq_called,
):
    order_nr = 'order-nr'
    created_at = '2021-09-16T12:00:00.1234+03:00'

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    @testpoint(CONSUMER_TESTPOINT)
    def after_commit(_):
        pass

    event = utils.make_event(
        order_nr,
        created_at,
        order_event=order_event,
        place_id=place_id,
        order_type=order_type,
        delivery_type=delivery_type,
        shipping_type=shipping_type,
    )
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await after_commit.wait_call()
    assert commit.times_called == 1

    assert stq.eats_eta_process_event.times_called == stq_called

    assert not db_select_orders(order_nr=order_nr)
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_create_existing_order(
        taxi_eats_eta,
        checkout,
        testpoint,
        stq,
        redis_store,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order_nr = 'order-nr'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    event = utils.make_event(
        order_nr, created_at, eater_passport_uid='123', device_id='456',
    )
    order = make_order(
        order_nr=order_nr,
        order_status='created',
        created_at=created_at,
        eater_passport_uid=None,
        device_id=None,
    )
    db_insert_order(order)
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()

    assert stq.eats_eta_process_event.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == order
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event, event_time, order_status, delivery_started_at, meta, '
    'picking_slot_started_at, picking_slot_finished_at',
    [
        [
            'confirmed',
            '2021-09-16T13:00:00.999999+03:00',
            'confirmed',
            None,
            {
                'assembly_slot': {
                    'id': 'slot-id',
                    'start': '03-03-2022 19:00',
                    'end': '2022-03-03T23:00:00+06:00',
                    'duration': 0,
                },
            },
            '2022-03-03T19:00:00+03:00',
            '2022-03-03T20:00:00+03:00',
        ],
        [
            'taken',
            '2021-09-16T13:00:00.999999+03:00',
            'taken',
            utils.parse_datetime('2021-09-16T13:00:00.999999+03:00'),
            [],
            None,
            None,
        ],
        [
            'finished',
            '2021-09-16T13:00:00.999999+03:00',
            'complete',
            None,
            [],
            None,
            None,
        ],
        [
            'cancelled',
            '2021-09-16T13:00:00.999999+03:00',
            'cancelled',
            None,
            [],
            None,
            None,
        ],
    ],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_change_order_status(
        taxi_eats_eta,
        testpoint,
        stq,
        check_redis_value,
        make_order,
        db_insert_order,
        db_select_orders,
        order_event,
        event_time,
        order_status,
        delivery_started_at,
        meta,
        picking_slot_started_at,
        picking_slot_finished_at,
):
    event_time = utils.parse_datetime(event_time)

    order_nr = 'order-nr'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    @testpoint(PROCESSING_TESTPOINT)
    def after_processing(_):
        pass

    order = make_order(
        order_nr=order_nr,
        order_status='created',
        created_at=created_at,
        eater_passport_uid=None,
        device_id=None,
        picking_slot_started_at=picking_slot_started_at,
        picking_slot_finished_at=picking_slot_finished_at,
    )
    db_insert_order(order)
    order['order_status'] = order_status
    order['delivery_started_at'] = delivery_started_at
    order['status_changed_at'] = event_time

    event = utils.make_event(order_nr, event_time, order_event, meta=meta)
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()
    await after_processing.wait_call()

    assert stq.eats_eta_process_event.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == order
    check_redis_value(order_nr, 'order_status', order_status)


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_status, order_event',
    [
        ['paid', 'created'],
        ['confirmed', 'payed'],
        ['taken', 'confirmed'],
        ['complete', 'taken'],
        ['cancelled', 'taken'],
    ],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_change_to_prev_order_status(
        taxi_eats_eta,
        checkout,
        testpoint,
        now_utc,
        stq,
        check_redis_value,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        order_event,
):
    order_nr = 'order-nr'

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    order = make_order(
        order_nr=order_nr,
        order_status=order_status,
        created_at=now_utc,
        eater_passport_uid=None,
        device_id=None,
    )
    db_insert_order(order)

    event = utils.make_event(order_nr, now_utc, order_event)
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()

    assert stq.eats_eta_process_event.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == order
    check_redis_value(order_nr, 'order_status', None)


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event', ['payed', 'confirmed', 'taken', 'finished', 'cancelled'],
)
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_change_not_existing_order_status(
        taxi_eats_eta,
        testpoint,
        stq,
        redis_store,
        db_select_orders,
        order_event,
        now_utc,
):
    order_nr = 'order-nr'

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    event = utils.make_event(order_nr, now_utc, order_event)
    response = await taxi_eats_eta.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    await commit.wait_call()

    assert stq.eats_eta_process_event.times_called == 0

    assert not db_select_orders(order_nr=order_nr)
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.config(EATS_ETA_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS)
async def test_order_flow(
        taxi_eats_eta,
        checkout,
        testpoint,
        stq,
        check_redis_value,
        make_order,
        db_select_orders,
):
    order_nr = 'order-nr'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    events = {}
    for i, order_event in enumerate(
            [
                'created',
                'payed',
                'ready_to_send',
                'sent',
                'confirmed',
                'taken',
                'finished',
            ],
    ):
        events[order_event] = utils.make_event(
            order_nr,
            created_at + datetime.timedelta(seconds=i * 600),
            order_event,
        )

    expected_order = make_order(
        order_nr=order_nr,
        order_status='complete',
        created_at=created_at,
        status_changed_at=utils.parse_datetime(
            events['finished']['finished_at'],
        ),
        delivery_started_at=utils.parse_datetime(events['taken']['taken_at']),
    )

    processed_events = []

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        processed_events.append(cookie)

    for order_event, event in events.items():
        response = await taxi_eats_eta.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': CONSUMER,
                    'data': json.dumps(event),
                    'topic': LOGBROKER_TOPIC,
                    'cookie': order_event,
                },
            ),
        )
        assert response.status_code == 200
    await taxi_eats_eta.run_task(CONSUMER_TASK)
    for _ in events:
        await commit.wait_call()

    assert processed_events == list(events.keys())

    assert stq.eats_eta_process_event.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == expected_order
    for key in utils.ORDER_CREATED_REDIS_KEYS:
        value = expected_order[key]
        check_redis_value(order_nr, key, value)
