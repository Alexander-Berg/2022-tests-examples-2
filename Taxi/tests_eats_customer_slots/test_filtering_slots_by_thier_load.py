import pytest

from tests_eats_customer_slots import utils


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.slots_loading_feature_enabled()
@utils.slot_capacity_coefficients()
@utils.slot_load_threshold()
@pytest.mark.now('2021-11-25T12:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_no_intervals_for_place(
        taxi_eats_customer_slots, mock_calculate_load,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        shop_picking_type='our_picking',
    )

    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert not response.json()['available_asap']
    assert len(response.json()['available_slots']) == 19


def make_intervals_from_slots(now, slots, capacity=2):
    intervals = []
    for slot in slots['daily_slots'][0]['slots']:
        start = utils.make_datetime(now, slot['start'], now.tzinfo)
        end = utils.make_datetime(now, slot['end'], now.tzinfo)

        intervals.append((start, end, capacity))
    return intervals


def make_slots_with_orders(now, slots, slot_load):
    slots_orders = []
    for item in slots['daily_slots']:
        day = item['day']
        slots = item['slots']
        for slot in slots:
            start = utils.make_datetime(
                utils.add_days(now, day), slot['start'], now.tzinfo,
            )
            end = utils.make_datetime(
                utils.add_days(now, day + int(slot['start'] >= slot['end'])),
                slot['end'],
                now.tzinfo,
            )

            slots_orders.append(
                {
                    'slot': {
                        'start': start.isoformat(),
                        'end': end.isoformat(),
                        'estimated_delivery_timepoint': start.isoformat(),
                    },
                    'orders': slot_load,
                },
            )
    return slots_orders


def change_slot_orders_count(now, slots_orders, slot_start, slot_end, orders):
    start = utils.make_datetime(now, slot_start, now.tzinfo).isoformat()
    end = utils.make_datetime(now, slot_end, now.tzinfo).isoformat()

    for slot in slots_orders:
        if slot['slot']['start'] == start and slot['slot']['end'] == end:
            slot['orders'] = orders


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.slots_loading_feature_enabled()
@utils.slot_capacity_coefficients()
@utils.slot_load_threshold()
@pytest.mark.now('2021-11-25T09:00:00+00:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_all_slots_overloaded(
        taxi_eats_customer_slots,
        testpoint,
        mock_calculate_load,
        create_place_intervals,
        now,
):
    now = utils.set_timezone(now)
    place_id = 123456
    capacity = 2
    slot_load = 2
    mock_calculate_load.response['json']['places_load_info'][0].update(
        shop_picking_type='our_picking',
    )

    @testpoint('set-cache-data-testpoint')
    def orders_per_slot_cache_tp(_):
        return [
            {
                'place_id': place_id,
                'slots': make_slots_with_orders(
                    now, utils.DEFAULT_SLOTS, slot_load,
                ),
            },
        ]

    capacities = make_intervals_from_slots(now, utils.DEFAULT_SLOTS, capacity)
    create_place_intervals(place_id, 1, capacities)

    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert not response.json()['available_asap']
    assert not response.json()['available_slots']

    assert orders_per_slot_cache_tp.times_called == 1


def make_expected_slot(now, slot_start, slot_end, select_by_default=None):
    start = utils.make_datetime(now, slot_start, now.tzinfo)
    end = utils.make_datetime(now, slot_end, now.tzinfo)

    slot = {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'estimated_delivery_timepoint': (start.isoformat()),
    }
    if select_by_default:
        slot['select_by_default'] = select_by_default
    return slot


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.slots_loading_feature_enabled()
@utils.slot_capacity_coefficients()
@utils.slot_load_threshold()
@pytest.mark.now('2021-11-25T09:00:00+00:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_only_one_slot_available(
        taxi_eats_customer_slots,
        testpoint,
        mock_calculate_load,
        create_place_intervals,
        now,
):
    now = utils.set_timezone(now)
    place_id = 123456
    capacity = 2
    slot_load = 2
    mock_calculate_load.response['json']['places_load_info'][0].update(
        shop_picking_type='our_picking',
    )

    orders_per_slot = make_slots_with_orders(
        now, utils.DEFAULT_SLOTS, slot_load,
    )

    available_slot_starts = '15:00'
    available_slot_end = '16:00'
    change_slot_orders_count(
        now, orders_per_slot, available_slot_starts, available_slot_end, 1,
    )

    @testpoint('set-cache-data-testpoint')
    def orders_per_slot_cache_tp(_):
        return [{'place_id': place_id, 'slots': orders_per_slot}]

    capacities = make_intervals_from_slots(now, utils.DEFAULT_SLOTS, capacity)
    create_place_intervals(place_id, 1, capacities)

    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert not response.json()['available_asap']
    assert len(response.json()['available_slots']) == 1
    assert (
        make_expected_slot(
            now,
            available_slot_starts,
            available_slot_end,
            select_by_default=True,
        )
        == response.json()['available_slots'][0]
    )

    assert orders_per_slot_cache_tp.times_called == 1


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.slots_loading_feature_enabled()
@utils.slot_capacity_coefficients()
@utils.slot_load_threshold()
@utils.replace_place_id(654321)
@pytest.mark.now('2021-11-25T09:00:00+00:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_replace_place_id(
        taxi_eats_customer_slots,
        testpoint,
        mock_calculate_load,
        create_place_intervals,
        now,
):
    now = utils.set_timezone(now)
    place_id = 123456
    capacity = 2
    slot_load = 2
    mock_calculate_load.response['json']['places_load_info'][0].update(
        shop_picking_type='our_picking',
    )

    orders_per_slot = make_slots_with_orders(
        now, utils.DEFAULT_SLOTS, slot_load,
    )

    available_slot_starts = '15:00'
    available_slot_end = '16:00'
    change_slot_orders_count(
        now, orders_per_slot, available_slot_starts, available_slot_end, 1,
    )

    @testpoint('set-cache-data-testpoint')
    def orders_per_slot_cache_tp(_):
        return [{'place_id': place_id, 'slots': orders_per_slot}]

    capacities = make_intervals_from_slots(now, utils.DEFAULT_SLOTS, capacity)
    create_place_intervals(654321, 1, capacities)

    order = utils.make_order(estimated_picking_time=200)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert not response.json()['available_asap']
    assert len(response.json()['available_slots']) == 1
    assert (
        make_expected_slot(
            now,
            available_slot_starts,
            available_slot_end,
            select_by_default=True,
        )
        == response.json()['available_slots'][0]
    )

    assert orders_per_slot_cache_tp.times_called == 1
