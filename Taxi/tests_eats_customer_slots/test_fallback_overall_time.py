import datetime

import pytest

from tests_eats_customer_slots import utils

PLACE_ID = 0
BRAND_ID = '0'


def eats_customer_slots_settings(
        experiments3,
        estimated_delivery_timepoint_shift,
        asap_disable_threshold,
        approximate_picking_time,
        asap_delivery_time_max_epsilon,
        finish_working_interval_offset,
):
    experiments3.add_config(
        name='eats_customer_slots_settings',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/get-picking-slots',
            'eats-customer-slots/orders-per-slot-cache',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'estimated_delivery_timepoint_shift': (
                estimated_delivery_timepoint_shift
            ),
            'asap_disable_threshold': asap_disable_threshold,
            'approximate_picking_time': approximate_picking_time,
            'asap_delivery_time_max_epsilon': asap_delivery_time_max_epsilon,
            'finish_working_interval_offset': finish_working_interval_offset,
        },
    )


def mock_products_info(mockserver):
    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _mock_products_info(request):
        return mockserver.make_response(
            json={
                'products': [
                    {
                        'id': public_id,
                        'origin_id': f'origin_id{public_id[-1]}',
                        'place_brand_id': str('brand_id'),
                        'name': 'name1',
                        'description': {},
                        'is_choosable': True,
                        'is_catch_weight': False,
                        'adult': False,
                        'shipping_type': 'pickup',
                        'barcodes': [],
                        'images': [],
                        'is_sku': True,
                    }
                    for public_id in request.json['product_ids']
                ],
            },
        )

    return _mock_products_info


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.fallback_overall_time(enabled_for_checkout=True)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-10-20T07:00:00+03:00')
@pytest.mark.parametrize('days', [[0], [1], [0, 1]])
@pytest.mark.parametrize(
    'time_to_customer,estimated_picking_time',
    [(900, 901), (0, 1801), (1801, 7200)],
)
@pytest.mark.parametrize(
    'shop_picking_type,has_partner_slots',
    [('our_picking', False), ('shop_picking', False), ('shop_picking', True)],
)
# pylint: disable=invalid-name
async def test_fallback_overall_time_calculate_slots(
        experiments3,
        mockserver,
        taxi_config,
        mock_calculate_load,
        taxi_eats_customer_slots,
        now,
        days,
        time_to_customer,
        estimated_picking_time,
        shop_picking_type,
        has_partner_slots,
):
    """
        Тест проверяет, что при включенном конфиге
        eats_customer_slots_fallback_overall_time удаляются все слоты,
        estimated_delivery_timepoint которых за вычетом времени
        (время доставки + время сборки + время ожидания) находится в интервале
        работы магазина
    """
    now = utils.localize(now, 'Europe/Moscow')
    eats_customer_slots_settings(
        experiments3,
        estimated_delivery_timepoint_shift=1800,
        asap_disable_threshold=0,
        approximate_picking_time=estimated_picking_time,
        asap_delivery_time_max_epsilon=0,
        finish_working_interval_offset=0,
    )
    mock_products_info(mockserver)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=PLACE_ID,
        brand_id=int(BRAND_ID),
        estimated_waiting_time=0,
        shop_picking_type=shop_picking_type,
        free_pickers_count=1,
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': day,
                    'time_from': '10:00',
                    'day_to': day,
                    'time_to': '20:00',
                }
                for day in days
            ],
        ),
    )
    if has_partner_slots:
        taxi_config.set_values(
            {'EATS_PARTNER_SLOTS_BRANDS_SETTINGS': {'brand_ids': [BRAND_ID]}},
        )

    request_body = utils.make_order(
        place_id=PLACE_ID,
        brand_id=BRAND_ID,
        overall_time=None,
        time_to_customer=time_to_customer,
        estimated_picking_time=estimated_picking_time,
    )
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=request_body,
    )

    assert response.status == 200
    slots_estimated_delivery_timepoints = [
        datetime.datetime.fromisoformat(slot['estimated_delivery_timepoint'])
        for slot in response.json()['available_slots']
    ]
    for day in days:
        first_slot_time = next(
            time
            for time in slots_estimated_delivery_timepoints
            if time.day == 20 + day
        )
        place_opens_at = datetime.datetime.fromisoformat(
            f'2021-10-2{day}T10:00:00+03:00',
        )
        assert first_slot_time >= (
            place_opens_at
            + datetime.timedelta(
                seconds=(time_to_customer + estimated_picking_time),
            )
        )


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.fallback_overall_time(enabled_for_catalog=True)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-10-20T07:00:00+03:00')
@pytest.mark.parametrize('days', [[0], [1], [0, 1]])
@pytest.mark.parametrize(
    'estimated_delivery_duration,approximate_picking_time,'
    'expected_first_slot_start',
    [
        (900, 901, '2021-10-20T11:00:00+03:00'),
        (0, 1801, '2021-10-20T11:00:00+03:00'),
        (1801, 7200, '2021-10-20T13:00:00+03:00'),
    ],
)
@pytest.mark.parametrize(
    'shop_picking_type,has_partner_slots',
    [('our_picking', False), ('shop_picking', False), ('shop_picking', True)],
)
# pylint: disable=invalid-name
async def test_fallback_overall_time_calculate_delivery_time(
        experiments3,
        mockserver,
        taxi_config,
        mock_calculate_load,
        taxi_eats_customer_slots,
        now,
        days,
        estimated_delivery_duration,
        approximate_picking_time,
        expected_first_slot_start,
        shop_picking_type,
        has_partner_slots,
):
    """
        Тест проверяет, что при включенном конфиге
        eats_customer_slots_fallback_overall_time при расчете времени доставки
        проверяется, что (время доставки + время сборки + время ожидания)
        находится в интервале работы магазина
    """
    now = utils.localize(now, 'Europe/Moscow')
    estimated_delivery_timepoint_shift = 1800
    eats_customer_slots_settings(
        experiments3,
        estimated_delivery_timepoint_shift=estimated_delivery_timepoint_shift,
        asap_disable_threshold=0,
        approximate_picking_time=approximate_picking_time,
        asap_delivery_time_max_epsilon=0,
        finish_working_interval_offset=0,
    )
    mock_products_info(mockserver)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=PLACE_ID,
        brand_id=int(BRAND_ID),
        estimated_waiting_time=0,
        shop_picking_type=shop_picking_type,
        free_pickers_count=1,
        working_intervals=utils.make_working_intervals(
            now,
            [
                {
                    'day_from': day,
                    'time_from': '10:00',
                    'day_to': day,
                    'time_to': '20:00',
                }
                for day in days
            ],
        ),
    )
    if has_partner_slots:
        taxi_config.set_values(
            {'EATS_PARTNER_SLOTS_BRANDS_SETTINGS': {'brand_ids': [BRAND_ID]}},
        )

    request_body = {
        'places': [
            {
                'place_id': PLACE_ID,
                'estimated_delivery_duration': estimated_delivery_duration,
            },
        ],
        'device_id': 'whatever',
    }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )

    assert response.status == 200
    assert response.json() == {
        'places': [
            {
                'asap_availability': False,
                'delivery_eta': (
                    datetime.datetime.fromisoformat(expected_first_slot_start)
                    + datetime.timedelta(days=days[0])
                    - now
                ).total_seconds(),
                'full_text': '',
                'place_id': f'{PLACE_ID}',
                'short_text': '',
                'slots_availability': True,
            },
        ],
    }
