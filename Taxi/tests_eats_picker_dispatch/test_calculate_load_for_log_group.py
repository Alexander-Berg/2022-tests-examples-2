import datetime

import pytest

from . import utils

PERIODIC_NAME = 'periodic-picker-dispatcher'


def make_place_load_info(place_id, **kwargs):
    return dict(
        {
            'place_id': place_id,
            'brand_id': 1,
            'country_id': 1,
            'region_id': 1,
            'time_zone': 'Europe/Moscow',
            'city': 'Москва',
            'enabled': True,
            'estimated_waiting_time': 0,
            'free_pickers_count': 1,
            'total_pickers_count': 1,
            'is_place_closed': False,
            'is_place_overloaded': False,
        },
        **kwargs,
    )


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_order_in_another_place(
        taxi_eats_picker_dispatch, environment, create_place, now,
):
    (place_id1, place_id2) = environment.create_places(2)
    create_place(
        place_id=place_id1,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    create_place(
        place_id=place_id2,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    (picker_one, picker_two) = environment.create_pickers_in_log_group(
        [place_id1, place_id2],
        count=2,
        available_until=now + datetime.timedelta(minutes=1),
    )

    (order_one, _) = environment.create_orders(
        place_id2,
        count=2,
        estimated_picking_time=1800,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker_one, order_one)

    (order_three,) = environment.create_orders(
        place_id1,
        count=1,
        estimated_picking_time=1600,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker_two, order_three)

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/places/calculate-load', json={'place_ids': [place_id1]},
    )
    assert response.status == 200
    places_load_info = response.json()['places_load_info']
    assert len(places_load_info[0].pop('working_intervals')) == 1
    assert places_load_info == [
        make_place_load_info(
            place_id1,
            free_pickers_count=0,
            total_pickers_count=2,
            estimated_waiting_time=2600,
        ),
    ]


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_calculate_load_two_log_groups(
        taxi_eats_picker_dispatch, environment, create_place, now,
):
    places = environment.create_places(4)
    for place_id in places:
        create_place(
            place_id=place_id,
            working_intervals=[(now, now + datetime.timedelta(hours=10))],
        )
    sorted(places)

    (picker1, picker2) = environment.create_pickers_in_log_group(
        [places[0], places[1]], count=2,
    )
    (picker3, picker4) = environment.create_pickers_in_log_group(
        [places[2], places[3]], count=2,
    )

    (order1, order2, _) = environment.create_orders(
        places[1],
        count=3,
        estimated_picking_time=1800,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker1, order1)
    environment.start_picking_order(picker2, order2)

    (order3,) = environment.create_orders(
        places[2],
        count=1,
        estimated_picking_time=1500,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    (order4,) = environment.create_orders(
        places[3],
        count=1,
        estimated_picking_time=1500,
        place_finishes_work_at=utils.to_string(
            now - datetime.timedelta(minutes=1),
        ),
    )
    environment.start_picking_order(picker3, order3)
    environment.start_picking_order(picker4, order4)

    response = await taxi_eats_picker_dispatch.post(
        '/api/v1/places/calculate-load',
        json={'place_ids': [places[0], places[1], places[2]]},
    )
    assert response.status == 200
    places_load_info = sorted(
        response.json()['places_load_info'], key=lambda item: item['place_id'],
    )
    assert len(places_load_info) == 3
    places_load_info[0].pop('working_intervals')
    places_load_info[1].pop('working_intervals')
    places_load_info[2].pop('working_intervals')
    assert places_load_info[0] == make_place_load_info(
        places[0],
        free_pickers_count=0,
        total_pickers_count=2,
        estimated_waiting_time=2700,
    )
    assert places_load_info[1] == make_place_load_info(
        places[1],
        free_pickers_count=0,
        total_pickers_count=2,
        estimated_waiting_time=2700,
    )
    assert places_load_info[2] == make_place_load_info(
        places[2],
        free_pickers_count=0,
        total_pickers_count=2,
        estimated_waiting_time=1500,
    )


@pytest.mark.now
@utils.periodic_dispatcher_config3(max_picking_duration_limit=7200)
async def test_place_dispatch_overload_log_group(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id1, place_id2) = environment.create_places(2)
    create_place(place_id1)
    create_place(place_id2)

    environment.create_pickers_in_log_group([place_id1, place_id2], count=2)

    early_orders = environment.create_orders(
        place_id1,
        count=4,
        estimated_picking_time=3600,
        created_at=utils.to_string(now),
    )
    for i, order in enumerate(early_orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )

    environment.create_orders(
        place_id2,
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
        str(place_id1): {
            'place-load': 7350,
            'place-pickers-free': 2,
            'place-pickers-total': 2,
        },
        str(place_id2): {
            'place-load': 7350,
            'place-pickers-free': 2,
            'place-pickers-total': 2,
        },
    }


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=1800,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_log_group_no_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id1, place_id2) = environment.create_places(2)
    create_place(place_id1)
    create_place(place_id2)

    environment.create_pickers_in_log_group([place_id1, place_id2], count=1)

    orders = environment.create_orders(
        place_id2,
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

    assert stq.eats_picker_place_disable.times_called == 2
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id2)
    assert next_call['kwargs']['place_id'] == place_id2
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id1)
    assert next_call['kwargs']['place_id'] == place_id1
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id1): {
            'place-load': 5700,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
        str(place_id2): {
            'place-load': 5700,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
    }


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=7200, place_disable_offset_time=2300,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_log_group_overload(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id1, place_id2) = environment.create_places(2)
    create_place(place_id1)
    create_place(place_id2)

    environment.create_pickers_in_log_group([place_id1, place_id2], count=1)
    orders = environment.create_orders(
        place_id1,
        count=2,
        estimated_picking_time=2500,
        created_at=utils.to_string(now),
    )

    extra_order = environment.create_orders(
        place_id2,
        count=1,
        estimated_picking_time=2500,
        created_at=utils.to_string(now + datetime.timedelta(minutes=1)),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 1

    assert stq.eats_picker_assign.times_called == 1
    assert orders[0]['status'] == 'dispatching'
    assert orders[1]['status'] == 'new'
    assert extra_order[0]['status'] == 'new'

    assert stq.eats_picker_place_disable.times_called == 2
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id1)
    assert next_call['kwargs']['place_id'] == place_id1
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id1): {
            'place-load': 7500,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
        str(place_id2): {
            'place-load': 7500,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
    }


@utils.place_disable_exp3()
@pytest.mark.now
@utils.periodic_dispatcher_config3(
    max_picking_duration_limit=119200, place_disable_offset_time=5000,
)
@utils.stq_place_toggle_config3()
async def test_place_disable_log_group_one_place_without_orders(
        taxi_eats_picker_dispatch,
        taxi_eats_picker_dispatch_monitor,
        environment,
        create_place,
        stq,
        now,
):
    (place_id1, place_id2) = environment.create_places(2)
    create_place(
        place_id1,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    create_place(
        place_id2,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )

    environment.create_pickers_in_log_group([place_id1, place_id2], count=1)
    orders = environment.create_orders(
        place_id1,
        count=3,
        estimated_picking_time=12000,
        created_at=utils.to_string(now),
    )

    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_cancel_dispatch.times_called == 0

    assert stq.eats_picker_assign.times_called == 1
    assert orders[0]['status'] == 'dispatching'
    assert orders[1]['status'] == 'new'

    assert stq.eats_picker_place_disable.times_called == 2
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id1)
    assert next_call['kwargs']['place_id'] == place_id1
    next_call = stq.eats_picker_place_disable.next_call()
    assert next_call['id'] == str(place_id2)
    assert next_call['kwargs']['place_id'] == place_id2
    assert stq.eats_picker_place_enable.times_called == 0

    metrics = await taxi_eats_picker_dispatch_monitor.get_metric(
        'periodic-picker-dispatcher',
    )
    del metrics['$meta']
    assert metrics == {
        str(place_id1): {
            'place-load': 36000,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
        str(place_id2): {
            'place-load': 36000,
            'place-pickers-free': 1,
            'place-pickers-total': 1,
        },
    }
