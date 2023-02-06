import pytest

from tests_eats_customer_slots import utils


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.parametrize(
    'brand_id, order_eta, delivery_time, '
    'estimated_delivery_timepoint_shift, '
    'time_zone, slots_only, asap_only, asap_and_slots, no_asap_no_slots',
    [
        [1, 200, None, 0, 'Etc/GMT+10', 1, 0, 0, 0],  # slots only
        [1, 200, None, 0, 'Europe/Moscow', 0, 0, 1, 0],  # asap and slots
        [  # no asap and no slots
            1,
            200,
            '2021-03-06T15:00:00+00:00',
            0,
            'UTC',
            0,
            0,
            0,
            1,
        ],
        [  # asap only
            utils.EMPTY_BRAND,
            200,
            None,
            0,
            'Etc/GMT+10',
            0,
            1,
            0,
            0,
        ],
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_free_pickers(
        taxi_eats_customer_slots,
        experiments3,
        mock_calculate_load,
        brand_id,
        order_eta,
        delivery_time,
        estimated_delivery_timepoint_shift,
        time_zone,
        now,
        slots_only,
        asap_only,
        asap_and_slots,
        no_asap_no_slots,
        taxi_eats_customer_slots_monitor,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            estimated_delivery_timepoint_shift, asap_disable_threshold=1800,
        ),
        None,
    )
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '10:00',
                    'day_to': 0,
                    'time_to': '21:00',
                },
                {
                    'day_from': 1,
                    'time_from': '10:00',
                    'day_to': 1,
                    'time_to': '12:00',
                },
            ],
        ),
        shop_picking_type='our_picking',
    )

    order = utils.make_order(
        estimated_picking_time=order_eta,
        brand_id=str(brand_id),
        delivery_time=delivery_time,
    )
    await taxi_eats_customer_slots.tests_control(reset_metrics=True)
    await taxi_eats_customer_slots.invalidate_caches()

    await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    metrics = await taxi_eats_customer_slots_monitor.get_metric(
        'customer-slots-metrics',
    )

    assert metrics['asap_only'] == asap_only
    assert metrics['slots_only'] == slots_only
    assert metrics['asap_and_slots'] == asap_and_slots
    assert metrics['no_asap_no_slots'] == no_asap_no_slots
