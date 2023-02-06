from typing import Optional

import pytest

from . import utils


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
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
async def test_stq_create_order(
        checkout,
        mockserver,
        stq_runner,
        stq,
        check_redis_value,
        make_order,
        db_select_orders,
        order_type,
        delivery_type,
        eater_passport_uid,
        device_id,
        delivery_coordinates: Optional[dict],
        courier_type,
        redis_store,
):
    order_nr = 'order-nr'
    place_id = 123
    eater_id = 'eater-id'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

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

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == 0
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
async def test_stq_create_order_failed_to_update_estimations(
        checkout,
        mockserver,
        stq_runner,
        stq,
        make_order,
        db_select_orders,
        order_type,
        delivery_type,
        eater_passport_uid,
        device_id,
        delivery_coordinates: Optional[dict],
        courier_type,
        redis_store,
):
    order_nr = 'order-nr'
    place_id = 123
    eater_id = 'eater-id'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

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

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == 0
    assert stq.eats_eta_update_estimations.times_called == 1
    kwargs = stq.eats_eta_update_estimations.next_call()['kwargs']
    assert kwargs['order_nr'] == order_nr

    assert db_select_orders(order_nr=order_nr)[0] == expected_order
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_stq_create_order_retries_number_exceeded(
        experiments3, mockserver, stq_runner, redis_store, db_select_orders,
):
    max_retries = 3
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_settings_config3(process_event_stq_retries=max_retries),
        None,
    )
    order_nr = 'order-nr'
    created_at = '2021-09-16T12:00:00.1234+03:00'

    event = utils.make_event(order_nr, created_at)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event}, exec_tries=max_retries,
    )

    assert mock_stq_reschedule.times_called == 0

    assert not db_select_orders(order_nr=order_nr)
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event, place_id, order_type, delivery_type, shipping_type, '
    'expect_fail, expect_reschedule',
    [
        ['unknown', '123', 'native', 'native', 'delivery', True, False],
        [
            'promise_changed',
            '123',
            'native',
            'native',
            'delivery',
            False,
            False,
        ],
        ['payed', '123', 'native', 'native', 'delivery', False, False],
        ['ready_to_send', '123', 'native', 'native', 'delivery', False, False],
        ['created', 'abc', 'native', 'native', 'delivery', False, True],
        ['created', '123', 'unknown', 'native', 'delivery', True, False],
        ['created', '123', 'lavka', 'native', 'delivery', False, False],
        ['created', '123', 'pharmacy', 'native', 'delivery', False, False],
        ['created', '123', 'fuel_food', 'native', 'delivery', False, False],
        ['created', '123', 'native', 'unknown', 'delivery', True, False],
        ['created', '123', 'native', 'native', 'unknown', True, False],
    ],
)
async def test_stq_create_order_bad_event(
        mockserver,
        stq_runner,
        redis_store,
        db_select_orders,
        order_event,
        place_id,
        order_type,
        delivery_type,
        shipping_type,
        expect_fail,
        expect_reschedule,
):
    order_nr = 'order-nr'
    created_at = '2021-09-16T12:00:00.1234+03:00'

    event = utils.make_event(
        order_nr,
        created_at,
        order_event=order_event,
        place_id=place_id,
        order_type=order_type,
        delivery_type=delivery_type,
        shipping_type=shipping_type,
    )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == int(expect_reschedule)

    assert not db_select_orders(order_nr=order_nr)
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_stq_create_existing_order(
        checkout,
        mockserver,
        stq_runner,
        redis_store,
        make_order,
        db_insert_order,
        db_select_orders,
):
    order_nr = 'order-nr'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

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

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == order
    assert not redis_store.keys()


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event, event_time, order_status, delivery_started_at',
    [
        ['confirmed', '2021-09-16T13:00:00.999999+03:00', 'confirmed', None],
        [
            'taken',
            '2021-09-16T13:00:00.999999+03:00',
            'taken',
            utils.parse_datetime('2021-09-16T13:00:00.999999+03:00'),
        ],
        ['finished', '2021-09-16T13:00:00.999999+03:00', 'complete', None],
        ['cancelled', '2021-09-16T13:00:00.999999+03:00', 'cancelled', None],
    ],
)
async def test_stq_change_order_status(
        mockserver,
        stq_runner,
        check_redis_value,
        make_order,
        db_insert_order,
        db_select_orders,
        order_event,
        event_time,
        order_status,
        delivery_started_at,
):
    event_time = utils.parse_datetime(event_time)

    order_nr = 'order-nr'
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    order = make_order(
        order_nr=order_nr,
        order_status='created',
        created_at=created_at,
        eater_passport_uid=None,
        device_id=None,
    )
    db_insert_order(order)
    order['order_status'] = order_status
    order['delivery_started_at'] = delivery_started_at
    order['status_changed_at'] = event_time

    event = utils.make_event(order_nr, event_time, order_event)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == 0

    assert db_select_orders(order_nr=order_nr)[0] == order
    check_redis_value(order_nr, 'order_status', order_status)


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'order_event', ['payed', 'confirmed', 'taken', 'finished', 'cancelled'],
)
async def test_stq_change_not_existing_order_status(
        mockserver,
        stq_runner,
        redis_store,
        db_select_orders,
        order_event,
        now_utc,
):
    order_nr = 'order-nr'

    event = utils.make_event(order_nr, now_utc, order_event)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_process_event.call(
        task_id=order_nr, kwargs={'event': event},
    )

    assert mock_stq_reschedule.times_called == 0

    assert not db_select_orders(order_nr=order_nr)
    assert not redis_store.keys()
