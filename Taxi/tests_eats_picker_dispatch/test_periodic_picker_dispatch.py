# pylint: disable=too-many-lines
import datetime

import pytest

from . import utils

PERIODIC_NAME = 'periodic-picker-dispatcher'


@pytest.mark.now
@utils.periodic_dispatcher_config3()
async def test_dispatch_only_for_free_pickers(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        stq,
        environment,
        now,
        create_place,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one,) = environment.create_pickers(
        place_id, count=1, available_until=now - datetime.timedelta(minutes=1),
    )
    (order_one,) = environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    environment.create_pickers(place_id, count=2)
    orders = environment.create_orders(place_id, count=3)
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 2
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[0]['eats_id']
    assert call_info['kwargs']['place_id'] == place_id
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[1]['eats_id']
    assert call_info['kwargs']['place_id'] == place_id

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 1600,
            'place-pickers-free': 2,
            'place-pickers-total': 3,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3()
async def test_dispatch_only_for_free_pickers_db_empty(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        stq,
        environment,
        now,
        get_places,
        places_environment,
):
    (place_id,) = environment.create_places(1)
    places_environment.create_places(1, dict(id=place_id))
    (delivery_zone,) = places_environment.create_delivery_zones(
        place_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(days=1)},
        ],
    )

    (picker_one,) = environment.create_pickers(place_id, count=1)
    (order_one,) = environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    environment.create_pickers(place_id, count=2)
    orders = environment.create_orders(place_id, count=3)
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 2
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[0]['eats_id']
    assert call_info['kwargs']['place_id'] == place_id
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == orders[1]['eats_id']
    assert call_info['kwargs']['place_id'] == place_id

    assert places_environment.mock_places_updates.times_called == 0
    assert places_environment.mock_retrieve_places.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1
    expected_data = utils.make_expected_data(
        [places_environment.catalog_places[place_id]],
        {place_id: delivery_zone},
    )
    utils.compare_db_with_expected_data(get_places(), expected_data)

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 1600,
            'place-pickers-free': 2,
            'place-pickers-total': 3,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_place_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=2)
    early_orders = environment.create_orders(
        place_id,
        count=4,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
    )
    for i, order in enumerate(early_orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )

    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=300,
        created_at=utils.to_string(now + datetime.timedelta(minutes=10)),
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 1

    assert stq.eats_picker_assign.times_called == 2
    assert early_orders[0]['status'] == 'dispatching'
    assert early_orders[1]['status'] == 'dispatching'
    assert early_orders[2]['status'] == 'new'
    assert early_orders[3]['status'] == 'new'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 7350,
            'place-pickers-free': 2,
            'place-pickers-total': 2,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_place_about_to_close_and_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id,) = environment.create_places(1)
    environment.create_pickers(
        place_id,
        count=2,
        available_until=now + datetime.timedelta(minutes=30),
    )
    place_finishes_work_at = utils.to_string(now + datetime.timedelta(hours=1))
    create_place(
        place_id,
        working_intervals=[
            (now - datetime.timedelta(hours=10), place_finishes_work_at),
        ],
    )
    orders = environment.create_orders(
        place_id,
        count=3,
        estimated_picking_time=3500,
        created_at=utils.to_string(now),
        place_finishes_work_at=place_finishes_work_at,
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 1

    assert stq.eats_picker_assign.times_called == 2
    assert orders[0]['status'] == 'dispatching'
    assert orders[1]['status'] == 'dispatching'
    assert orders[2]['status'] == 'new'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 5250,
            'place-pickers-free': 2,
            'place-pickers-total': 2,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_end_time_work_place_and_no_pickers(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
        stq_runner,
        mocked_time,
):
    (place_id,) = environment.create_places(1)
    environment.create_pickers(
        place_id,
        count=1,
        available_until=now - datetime.timedelta(minutes=10),
    )
    finish_place_time = utils.to_string(now - datetime.timedelta(minutes=10))
    create_place(
        place_id,
        working_intervals=[
            (now - datetime.timedelta(hours=10), finish_place_time),
        ],
    )
    (order_one,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
        place_finishes_work_at=finish_place_time,
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_cancel_dispatch.times_called == 1
    call_info = stq.eats_picker_cancel_dispatch.next_call()

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=order_one['eats_id'], kwargs=call_info['kwargs'],
    )
    assert order_one['status'] == 'dispatch_failed'

    environment.remove_pickers(place_id=place_id)
    (order_two,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
        place_finishes_work_at=finish_place_time,
    )

    mocked_time.sleep(6)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert order_two['status'] == 'new'

    assert stq.eats_picker_cancel_dispatch.times_called == 1
    call_info = stq.eats_picker_cancel_dispatch.next_call()

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=order_two['eats_id'], kwargs=call_info['kwargs'],
    )
    assert order_two['status'] == 'dispatch_failed'

    # Проверка, что причиной отмены диспатча является время работы магазина
    assert call_info['kwargs']['reason_code'] == 'PLACE_FINISHED_WORK_TIME'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 3600,
            'place-pickers-free': 0,
            'place-pickers-total': 0,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=1800)
async def test_place_work_and_no_pickers(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        mocked_time,
        now,
        stq_runner,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    finish_place_time = utils.to_string(now + datetime.timedelta(minutes=120))
    (order_one,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1000,
        created_at=utils.to_string(now),
        place_finishes_work_at=finish_place_time,
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_assign.times_called == 1
    assert order_one['status'] == 'dispatching'
    (order_two,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
        place_finishes_work_at=finish_place_time,
    )

    mocked_time.sleep(1801)

    environment.remove_pickers(place_id=place_id)

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert order_two['status'] == 'new'
    mocked_time.sleep(1801)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert order_two['status'] == 'new'

    assert stq.eats_picker_cancel_dispatch.times_called == 1
    call_info = stq.eats_picker_cancel_dispatch.next_call()

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=order_two['eats_id'], kwargs=call_info['kwargs'],
    )

    # Проверка, что причиной отмены диспатча является недоступность сборщиков
    assert call_info['kwargs']['reason_code'] == 'PLACE_HAS_NO_PICKER'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 4600,
            'place-pickers-free': 0,
            'place-pickers-total': 0,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_place_idle_duration=1800)
async def test_no_available_pickers(
        now_utc,
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        get_places,
        mocked_time,
        stq,
        stq_runner,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)

    # no pickers, no orders
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    last_time_had_pickers = now_utc()
    assert get_places()[0]['last_time_had_pickers'] is None

    mocked_time.sleep(1801)
    environment.create_pickers(place_id=place_id, count=1)
    # one picker, no orders
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    last_time_had_pickers = now_utc()
    assert get_places()[0]['last_time_had_pickers'] == last_time_had_pickers

    mocked_time.sleep(900)
    (order,) = environment.create_orders(
        place_id, count=1, created_at=utils.to_string(now_utc()),
    )
    # one picker, one order
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    last_time_had_pickers = now_utc()
    assert get_places()[0]['last_time_had_pickers'] == last_time_had_pickers
    assert stq.eats_picker_assign.times_called == 1
    assert order['status'] == 'dispatching'
    environment.remove_order(order['eats_id'])

    environment.remove_pickers(place_id=place_id)
    (order,) = environment.create_orders(
        place_id, count=1, created_at=utils.to_string(now_utc()),
    )
    mocked_time.sleep(1801)
    # no pickers, one order
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_cancel_dispatch.times_called == 1
    call_info = stq.eats_picker_cancel_dispatch.next_call()

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=order['eats_id'], kwargs=call_info['kwargs'],
    )
    assert get_places()[0]['last_time_had_pickers'] == last_time_had_pickers
    # Проверка, что причиной отмены диспатча является отсутствие сборщиков
    assert call_info['kwargs']['reason_code'] == 'PLACE_HAS_NO_PICKER'
    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 1200,
            'place-pickers-free': 0,
            'place-pickers-total': 0,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_place_idle_duration=1800)
@pytest.mark.parametrize('consider_order_place_finish_time', [True, False])
async def test_place_finished_work_time(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        now_utc,
        stq,
        stq_runner,
        consider_order_place_finish_time,
):
    now = now_utc()
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now - datetime.timedelta(hours=10), now)],
    )

    if not consider_order_place_finish_time:
        place_finishes_work_at = utils.to_string(
            now - datetime.timedelta(hours=10),
        )
    else:
        place_finishes_work_at = utils.to_string(
            now + datetime.timedelta(hours=10),
        )

    (order,) = environment.create_orders(
        place_id,
        count=1,
        created_at=utils.to_string(now),
        place_finishes_work_at=place_finishes_work_at,
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_assign.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0
    assert order['status'] == 'new'

    if not consider_order_place_finish_time:
        assert stq.eats_picker_cancel_dispatch.times_called == 1
        call_info = stq.eats_picker_cancel_dispatch.next_call()

        await stq_runner.eats_picker_cancel_dispatch.call(
            task_id=order['eats_id'], kwargs=call_info['kwargs'],
        )

        # Проверка, что причиной отмены диспатча является время работы магазина
        assert call_info['kwargs']['reason_code'] == 'PLACE_FINISHED_WORK_TIME'

        metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
            'periodic-picker-dispatcher',
        )
        del metrics['$meta']
        assert metrics == {
            str(place_id): {
                'place-load': 1200,
                'place-pickers-free': 0,
                'place-pickers-total': 0,
            },
        }
    else:
        assert stq.eats_picker_cancel_dispatch.times_called == 0


@utils.place_disable_exp3()
@utils.stq_place_toggle_config3()
@utils.periodic_dispatcher_config3(max_place_idle_duration=1800)
@pytest.mark.now
async def test_place_finished_work_time_place_disable_exp3(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        now_utc,
        stq,
        stq_runner,
):
    now = now_utc()
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now - datetime.timedelta(hours=10), now)],
    )
    (order,) = environment.create_orders(
        place_id,
        count=1,
        created_at=utils.to_string(now),
        place_finishes_work_at=utils.to_string(now),
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert order['place_finishes_work_at']

    assert stq.eats_picker_assign.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0
    assert order['status'] == 'new'

    assert stq.eats_picker_cancel_dispatch.times_called == 1
    call_info = stq.eats_picker_cancel_dispatch.next_call()

    await stq_runner.eats_picker_cancel_dispatch.call(
        task_id=order['eats_id'], kwargs=call_info['kwargs'],
    )

    # Проверка, что причиной отмены диспатча является время работы магазина
    assert call_info['kwargs']['reason_code'] == 'PLACE_FINISHED_WORK_TIME'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 1200,
            'place-pickers-free': 0,
            'place-pickers-total': 0,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_place_idle_duration=1800)
@pytest.mark.parametrize(
    'has_picker, auto_disabled, assign_expected, status_expected',
    [
        (False, False, 0, 'new'),
        (False, True, 0, 'new'),
        (True, False, 1, 'dispatching'),
        (True, True, 1, 'dispatching'),
    ],
)
async def test_place_disabled(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        now_utc,
        stq,
        has_picker,
        auto_disabled,
        assign_expected,
        status_expected,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id, enabled=False)
    if has_picker:
        environment.create_pickers(place_id=place_id, count=1)
    (order,) = environment.create_orders(
        place_id, count=1, created_at=utils.to_string(now_utc()),
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == assign_expected
    assert environment.mock_core_notify_status_change_handler.times_called == 0
    assert order['status'] == status_expected

    assert stq.eats_picker_cancel_dispatch.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 1200


@pytest.mark.parametrize(
    'place_finishes_work_after, cancel_dispatch_called',
    [
        [datetime.timedelta(hours=0), 1],
        [datetime.timedelta(hours=-1), 1],
        [datetime.timedelta(hours=1), 0],
    ],
)
@pytest.mark.now
@utils.periodic_dispatcher_config3(max_place_idle_duration=1800)
async def test_picker_finished_work_time(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        now_utc,
        stq,
        stq_runner,
        place_finishes_work_after,
        cancel_dispatch_called,
):
    now = now_utc()
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[
            (
                now - datetime.timedelta(hours=10),
                now + place_finishes_work_after,
            ),
        ],
    )
    (order,) = environment.create_orders(
        place_id, count=1, created_at=utils.to_string(now),
    )
    environment.create_pickers(
        place_id=place_id,
        count=1,
        available_until=now - datetime.timedelta(seconds=1),
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0
    assert order['status'] == 'new'

    assert (
        stq.eats_picker_cancel_dispatch.times_called == cancel_dispatch_called
    )
    if cancel_dispatch_called:
        call_info = stq.eats_picker_cancel_dispatch.next_call()

        await stq_runner.eats_picker_cancel_dispatch.call(
            task_id=order['eats_id'], kwargs=call_info['kwargs'],
        )

        # Проверка, что причиной отмены диспатча является время работы магазина
        assert call_info['kwargs']['reason_code'] == 'PLACE_FINISHED_WORK_TIME'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 1200


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=100)
async def test_account_dispatching_and_waiting_dispatch(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now_utc,
):
    now = now_utc()
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=2)
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=100,
        created_at=utils.to_string(now),
        status='dispatching',
    )
    (order_two,) = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=80,
        created_at=utils.to_string(now),
        status='waiting_dispatch',
    )
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=50,
        created_at=utils.to_string(now + datetime.timedelta(seconds=10)),
        status='new',
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_cancel_dispatch.times_called == 1

    assert stq.eats_picker_assign.times_called == 1
    assert order_two['status'] == 'dispatching'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 115,
            'place-pickers-free': 1,
            'place-pickers-total': 2,
        },
    }


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=3600)
async def test_account_currently_picking_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    picker_one, picker_two = environment.create_pickers(place_id, count=2)
    (order_one, order_two, _) = environment.create_orders(
        place_id, count=3, estimated_picking_time=3601,
    )

    environment.start_picking_order(picker_one, order_one)
    environment.start_picking_order(picker_two, order_two)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_assign.times_called == 0
    assert stq.eats_picker_cancel_dispatch.times_called == 1

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 5401,
            'place-pickers-free': 0,
            'place-pickers-total': 2,
        },
    }


@utils.periodic_dispatcher_config3()
async def test_multiple_places(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
):
    place_one, place_two, place_three, place_four = environment.create_places(
        count=4,
    )
    for place_id in (place_one, place_two, place_three, place_four):
        create_place(place_id)

    environment.create_pickers(place_two, count=2)
    environment.create_pickers(place_three, count=1)
    environment.create_pickers(place_four, count=2)

    place_one_orders = environment.create_orders(place_one, count=2)
    place_three_orders = environment.create_orders(place_three, count=2)
    place_four_orders = environment.create_orders(place_four, count=1)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 2
    assert all(o['status'] == 'new' for o in place_one_orders)
    assert place_three_orders[0]['status'] == 'dispatching'
    assert place_three_orders[1]['status'] == 'new'
    assert place_four_orders[0]['status'] == 'dispatching'

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    places_picking_time = {
        place_one: 2400,
        place_two: 0,
        place_three: 2400,
        place_four: 600,
    }
    for place_id, picking_time in places_picking_time.items():
        assert metrics[str(place_id)]['place-load'] == picking_time


@utils.periodic_dispatcher_config3()
async def test_no_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
):
    places = environment.create_places(5)
    for place_id in places:
        create_place(place_id)
        environment.create_pickers(place_id, count=3)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 0,
            'place-pickers-free': 3,
            'place-pickers-total': 3,
        }
        for place_id in places
    }


@utils.periodic_dispatcher_config3()
async def test_picker_orders_failure(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-picker-orders/api/v1/orders/select-for-dispatch',
    )
    def _picker_orders_select_orders_for_dispatch(request):
        raise mockserver.TimeoutError()

    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=1)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 0
    assert stq.eats_picker_cancel_dispatch.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 0


@utils.periodic_dispatcher_config3()
async def test_picker_supply_failure(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-picker-supply/api/v1/select-store-pickers/',
    )
    def _picker_supply_select_store_pickers(request):
        raise mockserver.TimeoutError()

    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=1)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 0
    assert stq.eats_picker_cancel_dispatch.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 1200


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
@pytest.mark.config(
    EATS_PICKER_DISPATCH_SYNC_PLACES_INFO_PARAMS={
        'period_seconds': 60,
        'working_intervals_limit': 7,
        'places_batch_size': 1,
    },
)
async def test_catalog_storage_failure(
        taxi_eats_picker_dispatch,
        mockserver,
        taxi_eats_picker_dispatch_monitor,
        stq,
        environment,
        places_environment,
        get_places,
        now,
):
    (place_1_id, place_2_id) = places_environment.create_places(2)
    (delivery_zone,) = places_environment.create_delivery_zones(
        place_1_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(hours=10)},
        ],
    )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    async def mock_retrieve_places(request):
        if any(
                place_id_ not in (place_1_id, place_2_id)
                for place_id_ in request.json['place_ids']
        ):
            return mockserver.make_response(status=500)
        return await places_environment.mock_retrieve_places(request)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/delivery_zones/retrieve-by-place-ids',
    )
    async def mock_retrieve_delivery_zones(request):
        if any(
                place_id_ not in (place_1_id, 555)
                for place_id_ in request.json['place_ids']
        ):
            return mockserver.make_response(status=500)
        return await places_environment.mock_retrieve_delivery_zones(request)

    (picker_one, _) = environment.create_pickers(place_1_id, count=2)
    (order_one, _) = environment.create_orders(place_1_id, count=2)
    for place_id in (1, 2, 555, place_2_id):
        environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 1
    assert stq.eats_picker_cancel_dispatch.times_called == 0
    assert environment.mock_core_notify_status_change_handler.times_called == 0

    assert mock_retrieve_places.times_called == 5
    assert places_environment.mock_retrieve_places.times_called == 2
    assert mock_retrieve_delivery_zones.times_called == 2
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1
    expected_data = utils.make_expected_data(
        [places_environment.catalog_places[place_1_id]],
        {place_1_id: delivery_zone},
    )
    utils.compare_db_with_expected_data(get_places(), expected_data)
    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    for place_id in (1, 2, 555, place_1_id, place_2_id):
        assert metrics[str(place_id)]['place-load'] == 1200


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=100)
async def test_order_status_change_fail(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        mockserver,
):
    """
    Если ручка смены статуса заказа не ответила, мы продолжаем работу,
    а не падаем. Но при этом не запускаем STQ-задачу назначения сборщика
    """

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def picker_orders_status(request):
        raise mockserver.TimeoutError()

    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(place_id, count=2, estimated_picking_time=52)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert picker_orders_status.times_called == 1
    assert stq.eats_picker_cancel_dispatch.times_called == 1
    assert stq.eats_picker_assign.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 104


@utils.periodic_dispatcher_config3()
async def test_place_has_only_dispatching_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
):
    place_one, place_two = environment.create_places(count=2)
    create_place(place_one)
    create_place(place_two)
    environment.create_pickers(place_one, count=1)
    environment.create_pickers(place_two, count=1)
    environment.create_orders(place_one, count=1, status='dispatching')
    (place_two_order,) = environment.create_orders(
        place_two, count=1, status='new',
    )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == 1
    call_info = stq.eats_picker_assign.next_call()
    assert call_info['id'] == place_two_order['eats_id']
    assert call_info['kwargs']['place_id'] == place_two

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_one)]['place-load'] == 1200
    assert metrics[str(place_two)]['place-load'] == 1200


@pytest.mark.now
@pytest.mark.parametrize(
    'remaining_picking_duration, dispatch_count, cancel_count',
    [(360, 0, 1), (180, 1, 0)],
)
@utils.periodic_dispatcher_config3(max_picking_duration_limit=1000)
async def test_expired_order(
        now_utc,
        mockserver,
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        mocked_time,
        dispatch_count,
        cancel_count,
        remaining_picking_duration,
):
    estimated_picking_time = 1800
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    picker_one, _ = environment.create_pickers(place_id, count=2)
    order_one, _ = environment.create_orders(
        place_id, count=2, estimated_picking_time=estimated_picking_time,
    )
    environment.start_picking_order(picker_one, order_one)

    # Делаем так, что с момента старта сборки order_one прошло времени больше,
    # чем длительность его сборки
    mocked_time.sleep(2000)

    def eats_eta_picking_duration(order_nr):
        calculated_at = utils.to_string(now_utc())
        if order_nr == order_one['eats_id']:
            return {
                'name': 'picking_duration',
                'duration': estimated_picking_time,
                'remaining_duration': remaining_picking_duration,
                'calculated_at': calculated_at,
                'status': 'in_progress',
            }
        return {
            'name': 'picking_duration',
            'duration': estimated_picking_time,
            'remaining_duration': estimated_picking_time,
            'calculated_at': calculated_at,
            'status': 'not_started',
        }

    environment.get_picking_duration_response = eats_eta_picking_duration

    await taxi_eats_picker_dispatch.invalidate_caches()
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == cancel_count
    assert stq.eats_picker_assign.times_called == dispatch_count

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert (
        metrics[str(place_id)]['place-load']
        == (estimated_picking_time + remaining_picking_duration) // 2
    )


@pytest.mark.parametrize(
    'place_orders_offsets, expected_ordering',
    [
        ([[4], [3], [2], [1], [0]], [0, 1, 2, 3, 4]),
        ([[0], [1], [2], [3], [4]], [4, 3, 2, 1, 0]),
        ([[2], [1], [4], [5], [3]], [3, 2, 4, 0, 1]),
        ([[0, 1, 2], [1, 2, 3], [2, 3, 4], [5]], [3, 2, 1, 0]),
        ([[2, 1, 0], [3, 2, 1], [4, 3, 2], [5]], [3, 2, 1, 0]),
        ([[5, 0, 9], [98, 1, 34], [4, 1, 33], [0], [55, 11]], [1, 4, 2, 0, 3]),
    ],
)
@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_place_overload_place_ordering(
        taxi_eats_picker_dispatch,
        environment,
        create_place,
        stq,
        now,
        place_orders_offsets,
        expected_ordering,
):
    places_count = len(place_orders_offsets)
    places = environment.create_places(places_count)
    orders = []
    for i, place in enumerate(places):
        orders_count = len(place_orders_offsets[i])
        create_place(place)
        environment.create_pickers(place, count=orders_count)
        for offset in place_orders_offsets[i]:
            (order,) = environment.create_orders(
                place,
                count=1,
                estimated_picking_time=100,
                created_at=utils.to_string(
                    now - datetime.timedelta(seconds=offset),
                ),
            )
            orders.append(order)

    await taxi_eats_picker_dispatch.invalidate_caches()
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == len(orders)

    for order in orders:
        assert order['status'] == 'dispatching'

    for i in expected_ordering:
        for _ in enumerate(place_orders_offsets[i]):
            call_info = stq.eats_picker_assign.next_call()
            assert call_info['kwargs']['place_id'] == places[i]


@pytest.mark.now
@utils.periodic_dispatcher_config3()
async def test_dispatch_fetch_working_intervals_from_places_info(
        taxi_eats_picker_dispatch,
        environment,
        places_environment,
        now,
        get_places,
):
    place_id = places_environment.create_places(
        1,
        dict(
            working_intervals=[
                {'from': now, 'to': now + datetime.timedelta(hours=10)},
            ],
        ),
    )[0]

    (picker_one,) = environment.create_pickers(place_id, count=1)
    (order_one,) = environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert places_environment.mock_places_updates.times_called == 0
    assert places_environment.mock_retrieve_places.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 0

    db_places = get_places([place_id])
    assert len(db_places[0]['working_intervals']) == 1


@pytest.mark.now
@utils.periodic_dispatcher_config3()
async def test_dispatch_fetch_working_intervals_from_delivery_zones(
        taxi_eats_picker_dispatch,
        environment,
        places_environment,
        now,
        get_places,
):
    place_id = places_environment.create_places(1)[0]
    places_environment.create_delivery_zones(
        place_id,
        1,
        working_intervals=[
            {'from': now, 'to': now + datetime.timedelta(hours=10)},
        ],
    )

    (picker_one,) = environment.create_pickers(place_id, count=1)
    (order_one,) = environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert places_environment.mock_places_updates.times_called == 0
    assert places_environment.mock_retrieve_places.times_called == 1
    assert places_environment.mock_retrieve_delivery_zones.times_called == 1

    db_places = get_places([place_id])
    assert len(db_places[0]['working_intervals']) == 1


@pytest.mark.now('2022-01-21T12:00:00+0000')
@utils.periodic_dispatcher_config3()
@pytest.mark.config(
    EATS_PICKER_DISPATCH_METRICS_THRESHOLD={'outdated_after': 60},
)
async def test_resetting_dispatch_metrics(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        now,
        create_place,
        mocked_time,
):
    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one,) = environment.create_pickers(
        place_id, count=1, available_until=now - datetime.timedelta(minutes=1),
    )
    (order_one,) = environment.create_orders(place_id, count=1)
    environment.start_picking_order(picker_one, order_one)

    environment.create_pickers(place_id, count=2)
    orders = environment.create_orders(place_id, count=3)
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    mocked_time.sleep(60)
    await taxi_eats_picker_dispatch.invalidate_caches()

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 1600,
            'place-pickers-free': 2,
            'place-pickers-total': 3,
        },
    }

    mocked_time.sleep(1)
    await taxi_eats_picker_dispatch.invalidate_caches()

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert not metrics
