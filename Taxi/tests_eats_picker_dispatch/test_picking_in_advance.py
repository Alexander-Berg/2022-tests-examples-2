import datetime

import pytest

from . import utils

PERIODIC_NAME = 'periodic-picker-dispatcher'


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize('is_enabled', [True, False])
@pytest.mark.parametrize('free_pickers_threshold', [2, 1])
@pytest.mark.parametrize('is_config_enabled', [True, False])
@pytest.mark.parametrize(
    'ignore_racks, places_info',
    [
        (True, []),
        (False, []),
        (True, [{'place_id': 0, 'has_fridge': True, 'has_freezer': True}]),
        (False, [{'place_id': 0, 'has_fridge': True, 'has_freezer': True}]),
    ],
)
async def test_picking_in_advance(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        now,
        create_place,
        experiments3,
        is_enabled,
        free_pickers_threshold,
        ignore_racks,
        places_info,
        mockserver,
        is_config_enabled,
):
    if is_config_enabled:
        experiments3.add_config(
            **utils.picking_in_advance_settings(
                is_enabled, free_pickers_threshold, ignore_racks,
            ),
        )

    experiments3.add_config(**utils.picking_in_advance_offset())
    await taxi_eats_picker_dispatch.invalidate_caches()

    @mockserver.json_handler(
        '/eats-picker-racks/api/v1/fridge_and_freezer_info',
    )
    def _eats_picker_racks(_):
        return {'places_info': places_info}

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    free_pickers = 2
    environment.create_pickers(place_id, count=free_pickers)

    orders_count = 2
    orders = environment.create_orders(
        place_id,
        count=orders_count,
        is_asap=False,
        estimated_picking_time=1800,
    )
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
        order['estimated_delivery_time'] = utils.to_string(
            now + datetime.timedelta(minutes=(60 * i)),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)
    is_pickin_in_advance_enabled = (
        is_enabled or (places_info and not ignore_racks)
    ) and (free_pickers > free_pickers_threshold)

    if not is_pickin_in_advance_enabled or not is_config_enabled:
        orders_count = 1

    assert stq.eats_picker_assign.times_called == orders_count
    for i in range(0, orders_count):
        call_info = stq.eats_picker_assign.next_call()
        assert call_info['id'] == orders[i]['eats_id']
    assert stq.eats_picker_cancel_dispatch.times_called == 0


@pytest.mark.now
@utils.periodic_dispatcher_config3()
@pytest.mark.parametrize('offset, expected_orders', [(0, 1), (10800, 3)])
async def test_picking_in_advance_offset(
        taxi_eats_picker_dispatch,
        stq,
        environment,
        now,
        create_place,
        experiments3,
        mockserver,
        offset,
        expected_orders,
):
    experiments3.add_config(
        **utils.picking_in_advance_settings(True, 0, False),
    )
    experiments3.add_config(**utils.picking_in_advance_offset(offset))
    await taxi_eats_picker_dispatch.invalidate_caches()

    @mockserver.json_handler(
        '/eats-picker-racks/api/v1/fridge_and_freezer_info',
    )
    def _eats_picker_racks(_):
        return {
            'places_info': [
                {'place_id': 0, 'has_fridge': True, 'has_freezer': True},
            ],
        }

    (place_id,) = environment.create_places(1)
    create_place(
        place_id,
        working_intervals=[(now, now + datetime.timedelta(hours=10))],
    )
    free_pickers = 6
    environment.create_pickers(place_id, count=free_pickers)

    orders_count = 6
    orders = environment.create_orders(
        place_id,
        count=orders_count,
        is_asap=False,
        estimated_picking_time=1800,
    )
    for i, order in enumerate(orders, start=1):
        order['created_at'] = utils.to_string(
            now + datetime.timedelta(seconds=i),
        )
        order['estimated_delivery_time'] = utils.to_string(
            now + datetime.timedelta(minutes=(60 * i)),
        )
    await taxi_eats_picker_dispatch.run_task(PERIODIC_NAME)

    assert stq.eats_picker_assign.times_called == expected_orders
    for i in range(0, expected_orders):
        call_info = stq.eats_picker_assign.next_call()
        assert call_info['id'] == orders[i]['eats_id']
    assert stq.eats_picker_cancel_dispatch.times_called == 0
