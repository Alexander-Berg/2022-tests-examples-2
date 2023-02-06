import pytest

from tests_eats_customer_slots import utils


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config(asap_disable_threshold=600)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-12-27T08:00:00+03:00')
@pytest.mark.parametrize(
    'delivery_time,available_asap',
    [
        ('2021-12-27T08:05:00+03:00', True),
        ('2021-12-27T08:05:01+03:00', False),
    ],
)
async def test_validate_delivery_time_asap(
        taxi_eats_customer_slots, delivery_time, available_asap,
):
    """
        При отсутствующем поле delivery_time в запросе, возвращаем 200, если
        ASAP-доставка доступна, 400 - если нет
    """

    order = utils.make_order(
        estimated_picking_time=200, delivery_time=delivery_time,
    )

    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/validate-delivery-time', json={'order': order},
    )
    assert response.status_code == 200
    assert response.json()['available_asap'] == available_asap


EXPECTED_SLOTS = [
    {
        'start': '2021-12-27T13:00:00+03:00',
        'estimated_delivery_timepoint': '2021-12-27T13:30:00+03:00',
        'end': '2021-12-27T14:00:00+03:00',
        'select_by_default': True,
    },
    {
        'start': '2021-12-27T14:00:00+03:00',
        'estimated_delivery_timepoint': '2021-12-27T14:30:00+03:00',
        'end': '2021-12-27T15:00:00+03:00',
    },
]


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config(estimated_delivery_timepoint_shift=1800)
@pytest.mark.now('2021-12-27T08:00:00+03:00')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'delivery_time,available_slots',
    [
        (
            '2021-12-27T13:30:00+03:00',
            [
                {
                    'start': '2021-12-27T13:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-12-27T13:30:00+03:00'
                    ),
                    'end': '2021-12-27T14:00:00+03:00',
                    'select_by_default': True,
                },
            ],
        ),
        (
            '2021-12-27T14:00:00+03:00',
            [
                {
                    'start': '2021-12-27T14:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-12-27T14:30:00+03:00'
                    ),
                    'end': '2021-12-27T15:00:00+03:00',
                },
            ],
        ),
        (
            '2021-12-27T11:30:00+00:00',
            [
                {
                    'start': '2021-12-27T14:00:00+03:00',
                    'estimated_delivery_timepoint': (
                        '2021-12-27T14:30:00+03:00'
                    ),
                    'end': '2021-12-27T15:00:00+03:00',
                },
            ],
        ),
        ('2021-12-27T12:59:59+03:00', []),
        ('2021-12-27T15:00:01+03:00', []),
    ],
)
async def test_validate_delivery_time_slots(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        delivery_time,
        available_slots,
):
    """
        При наличии поля delivery_slot в запросе, возвращаем 200, если
        существует доступный слот с совпадающим интервалом, и 400 - если нет
    """

    now = utils.localize(now, 'UTC')
    mock_calculate_load.response['json']['places_load_info'][0].update(
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '10:00',
                    'day_to': 0,
                    'time_to': '12:00',
                },
            ],
        ),
        shop_picking_type='our_picking',
    )

    order = utils.make_order(
        estimated_picking_time=200, delivery_time='2021-12-27T11:00:00+03:00',
    )

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.json()['available_slots'] == EXPECTED_SLOTS

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/validate-delivery-time',
        json={'order': order, 'delivery_time': delivery_time},
    )
    assert response.status == 200
    assert response.json()['available_slots'] == available_slots
