import datetime

import pytest
import pytz

from . import utils

PERIODIC_NAME = 'periodic-picker-dispatcher'


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=1800,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_no_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    orders = environment.create_orders(
        place_id,
        count=3,
        estimated_picking_time=1900,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 0

    assert stq.eats_picker_assign.times_called == 1
    assert orders[0]['status'] == 'dispatching'
    assert orders[1]['status'] == 'new'
    assert orders[2]['status'] == 'new'

    assert stq.eats_picker_place_disable.times_called == 1
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id)
    assert next_call['kwargs']['place_id'] == place_id
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 5700


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=2300,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id)
    environment.create_pickers(place_id, count=1)
    orders = environment.create_orders(
        place_id,
        count=3,
        estimated_picking_time=2500,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 1

    assert stq.eats_picker_assign.times_called == 1
    assert orders[0]['status'] == 'dispatching'
    assert orders[1]['status'] == 'new'
    assert orders[2]['status'] == 'new'

    assert stq.eats_picker_place_disable.times_called == 1
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id)
    assert next_call['kwargs']['place_id'] == place_id
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 7500


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=900,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_overload_about_to_close(
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

    assert stq.eats_picker_place_disable.times_called == 1
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id)
    assert next_call['kwargs']['place_id'] == place_id
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 5250


@utils.place_disable_exp3()
@pytest.mark.now('2021-11-09T12:00:00+03:00')
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=1800,
    max_place_idle_duration=1800,
)
@utils.stq_place_toggle_config3()
@pytest.mark.parametrize(
    'has_picker, last_time_had_pickers, do_cancel, do_disable, do_dispatch',
    [
        (True, None, False, False, True),
        (True, '2021-11-09T10:00:00+03:00', False, False, True),
        (True, '2021-11-09T11:30:00+03:00', False, False, True),
        (False, None, False, False, False),
        (False, '2021-11-09T10:00:00+03:00', True, True, False),
        (False, '2021-11-09T11:30:00+03:00', False, False, False),
    ],
)
async def test_place_disable_if_has_no_picker(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
        has_picker,
        last_time_had_pickers,
        do_cancel,
        do_disable,
        do_dispatch,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id, last_time_had_pickers=last_time_had_pickers)
    environment.create_pickers(place_id, count=int(has_picker))
    orders = environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=1800,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    if do_cancel:
        assert stq.eats_picker_cancel_dispatch.times_called == 1
        next_call = stq.eats_picker_cancel_dispatch.next_call()
        assert next_call['id'] == orders[0]['eats_id']
        assert next_call['kwargs']['reason_code'] == 'PLACE_HAS_NO_PICKER'
    else:
        assert stq.eats_picker_cancel_dispatch.times_called == 0

    if do_disable:
        assert stq.eats_picker_place_disable.times_called == 1
        next_call = stq.eats_picker_place_disable.next_call()
        assert next_call['id'] == str(place_id)
        assert next_call['kwargs']['place_id'] == place_id
    else:
        assert stq.eats_picker_place_disable.times_called == 0

    if do_dispatch:
        assert stq.eats_picker_assign.times_called == 1
        assert orders[0]['status'] == 'dispatching'
    else:
        assert stq.eats_picker_assign.times_called == 0
        assert orders[0]['status'] == 'new'

    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 1800


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=1800,
)
@utils.stq_place_toggle_config3()
@pytest.mark.parametrize(
    'pickers, place_is_closed, disable',
    [
        (None, False, False),
        (0, False, True),
        (1, False, True),
        (None, True, False),
        (0, True, False),
        (1, True, False),
    ],
)
async def test_place_do_not_disable_if_no_info_from_supply_or_closed(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        create_place,
        now,
        pickers,
        place_is_closed,
        disable,
):
    now = now.replace(tzinfo=pytz.utc)
    place_id_0, place_id_1 = (0, 1)

    auto_disabled_at = now - datetime.timedelta(seconds=1900)
    create_place(
        place_id=place_id_0,
        auto_disabled_at=auto_disabled_at,
        working_intervals=[
            (
                now - datetime.timedelta(hours=7),
                now
                + datetime.timedelta(hours=(-1 if place_is_closed else 10)),
            ),
        ],
    )
    create_place(
        place_id=place_id_1,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    if pickers == 0:
        environment.create_pickers_empty(place_id_0)
    elif pickers and pickers > 0:
        environment.create_pickers(
            place_id_0, 1, available_until=now - datetime.timedelta(hours=1),
        )

    environment.create_orders(place_id_0, count=1, estimated_picking_time=5500)

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_place_disable.times_called == disable


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(place_enable_delay=1800)
@utils.stq_place_toggle_config3()
async def test_place_enable_manually_disabled(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id,) = environment.create_places(1)
    create_place(place_id, enabled=False)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=100,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.invalidate_caches(clean_update=True)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_place_disable.times_called == 0
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == 100


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=3600,
    place_enable_delay=1800,
)
@utils.stq_place_toggle_config3()
@pytest.mark.parametrize(
    'auto_disabled_seconds, estimated_picking_time, enabled_expected',
    [
        (1801, 3599, True),
        (1801, 3601, False),
        (1799, 3599, False),
        (1799, 3601, False),
    ],
)
async def test_place_enable_auto_disabled(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        places_environment,
        create_place,
        stq,
        now,
        auto_disabled_seconds,
        estimated_picking_time,
        enabled_expected,
):
    (place_id,) = environment.create_places(1)
    auto_disabled_at = now - datetime.timedelta(seconds=auto_disabled_seconds)
    auto_disabled_at = auto_disabled_at.replace(tzinfo=pytz.UTC)
    create_place(place_id, enabled=False, auto_disabled_at=auto_disabled_at)
    environment.create_pickers(place_id, count=1)
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=estimated_picking_time,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    if enabled_expected:
        assert stq.eats_picker_place_enable.times_called == 1
        next_call = stq.eats_picker_place_enable.next_call()
        assert next_call['id'] == str(place_id)
        assert next_call['kwargs']['place_id'] == place_id
    else:
        assert stq.eats_picker_place_enable.times_called == 0
    assert stq.eats_picker_place_disable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics[str(place_id)]['place-load'] == estimated_picking_time


@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=1800,
    place_enable_delay=1800,
)
@utils.stq_place_toggle_config3()
@utils.place_disable_exp3()
@pytest.mark.now
@pytest.mark.parametrize(
    'auto_disabled_seconds, enabled_expected', [(1799, False), (1801, True)],
)
async def test_place_enable_no_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
        auto_disabled_seconds,
        enabled_expected,
):
    (place_id,) = environment.create_places(1)
    auto_disabled_at = (
        now - datetime.timedelta(seconds=auto_disabled_seconds)
    ).replace(tzinfo=pytz.UTC)
    create_place(place_id, enabled=False, auto_disabled_at=auto_disabled_at)
    environment.create_pickers(place_id, count=1)

    await taxi_eats_picker_dispatch.invalidate_caches(clean_update=True)
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    if enabled_expected:
        assert stq.eats_picker_place_enable.times_called == 1
        next_call = stq.eats_picker_place_enable.next_call()
        assert next_call['id'] == str(place_id)
        assert next_call['kwargs']['place_id'] == place_id
    else:
        assert stq.eats_picker_place_enable.times_called == 0
    assert stq.eats_picker_place_disable.times_called == 0
    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics['0']['place-load'] == 0


@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=1800,
    place_enable_delay=1800,
)
@utils.stq_place_toggle_config3()
@utils.place_disable_exp3()
@pytest.mark.now
@pytest.mark.parametrize(
    'auto_disabled_seconds, place_is_closed, enable',
    [
        (1799, False, False),
        (1801, False, False),
        (1799, True, True),
        (1801, True, True),
    ],
)
async def test_place_enable_no_pickers(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        mockserver,
        create_place,
        stq,
        now,
        auto_disabled_seconds,
        place_is_closed,
        enable,
):
    (place_id,) = environment.create_places(1)
    auto_disabled_at = (
        now - datetime.timedelta(seconds=auto_disabled_seconds)
    ).replace(tzinfo=pytz.UTC)
    create_place(
        place_id,
        enabled=False,
        auto_disabled_at=auto_disabled_at,
        working_intervals=[
            (
                now - datetime.timedelta(hours=7),
                now + datetime.timedelta(hours=(-1 if place_is_closed else 1)),
            ),
        ],
    )
    environment.create_orders(
        place_id,
        count=1,
        estimated_picking_time=100,
        created_at=utils.to_string(now),
    )

    @mockserver.json_handler('/eats-core/v1/places/enable')
    def _places_enable(request):
        assert request.json == {'place_ids': [place_id]}
        return {'payload': {'enabled_places': [place_id], 'errors': []}}

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_place_enable.times_called == enable
    assert stq.eats_picker_place_disable.times_called == 0
    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id): {
            'place-load': 100,
            'place-pickers-free': 0,
            'place-pickers-total': 0,
        },
    }


@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=1800,
    place_enable_delay=1800,
)
@utils.stq_place_toggle_config3()
@utils.place_disable_exp3()
@pytest.mark.parametrize('auto_disabled_seconds', [1799, 1801])
async def test_place_enable_no_pickers_no_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        mockserver,
        create_place,
        stq,
        now_utc,
        auto_disabled_seconds,
):
    (place_id,) = environment.create_places(1)
    auto_disabled_at = now_utc() - datetime.timedelta(
        seconds=auto_disabled_seconds,
    )
    auto_disabled_at = auto_disabled_at.replace(tzinfo=pytz.UTC)
    create_place(place_id, enabled=False, auto_disabled_at=auto_disabled_at)

    @mockserver.json_handler('/eats-core/v1/places/enable')
    def _places_enable(request):
        assert request.json == {'place_ids': [place_id]}
        return {'payload': {'enabled_places': [place_id], 'errors': []}}

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_place_enable.times_called == 0
    assert stq.eats_picker_place_disable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {}


@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200,
    place_disable_offset_time=1800,
    place_enable_delay=1800,
)
@utils.stq_place_toggle_config3()
@utils.place_disable_exp3()
@pytest.mark.parametrize(
    'pickers, place_is_closed, enable',
    [
        (None, False, False),
        (0, False, False),
        (1, False, True),
        (None, True, True),
        (0, True, True),
        (1, True, True),
    ],
)
async def test_place_do_not_enable_if_no_info_from_supply_and_open(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        create_place,
        now,
        pickers,
        place_is_closed,
        enable,
):
    now = now.replace(tzinfo=pytz.utc)
    place_id_0, place_id_1 = (0, 1)

    auto_disabled_at = now - datetime.timedelta(seconds=1900)
    create_place(
        place_id_0,
        enabled=False,
        auto_disabled_at=auto_disabled_at,
        working_intervals=[
            (
                now - datetime.timedelta(hours=7),
                now + datetime.timedelta(hours=(-1 if place_is_closed else 1)),
            ),
        ],
    )
    create_place(place_id_1)

    if pickers == 0:
        environment.create_pickers_empty(place_id_0)
    elif pickers and pickers > 0:
        environment.create_pickers(
            place_id_0, 1, available_until=now - datetime.timedelta(hours=1),
        )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    assert stq.eats_picker_place_enable.times_called == enable
