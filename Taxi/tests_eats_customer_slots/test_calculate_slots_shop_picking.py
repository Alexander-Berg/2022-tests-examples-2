import datetime

import pytest

from tests_eats_customer_slots import utils


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config(
    asap_disable_threshold=1800, approximate_picking_time=10,
)
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.parametrize('time_to_customer', [0, 100, 1000, 4000])
@pytest.mark.parametrize(
    'time_zone, delivery_time, asap_by_place',
    [
        ('Etc/GMT+10', None, False),
        ('UTC', None, False),
        ('Europe/Moscow', None, True),
        ('Asia/Vladivostok', None, True),
        ('Asia/Kamchatka', None, False),
        ('Etc/GMT-14', None, False),
        ('Europe/Moscow', '2021-03-05T09:00:00+03:00', True),
        ('Europe/Moscow', '2021-03-05T12:01:00+03:00', True),
        ('Europe/Moscow', '2021-03-05T12:06:00+03:00', False),
        ('Europe/Moscow', '2021-03-05T22:00:00+03:00', False),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']},
                ),
            ],
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_shop_picking(
        taxi_eats_customer_slots,
        mock_calculate_load,
        make_expected_slots,
        time_to_customer,
        time_zone,
        delivery_time,
        asap_by_place,
        now,
):
    brand_id = 1
    now = utils.localize(now, time_zone)
    working_intervals = utils.make_working_intervals(
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
                'time_to': '21:00',
            },
        ],
    )

    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=working_intervals,
        shop_picking_type='shop_picking',
    )

    order = utils.make_order(
        time_to_customer=time_to_customer,
        brand_id=str(brand_id),
        delivery_time=delivery_time,
    )
    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    response_body = response.json()
    estimated_picking_time = now + datetime.timedelta(
        seconds=10,
    )  # approximate_picking_time
    estimated_completion_time = estimated_picking_time + datetime.timedelta(
        seconds=time_to_customer,
    )

    asap_by_disable_threshold = estimated_picking_time <= (
        now + datetime.timedelta(seconds=1800)
    )

    if delivery_time:
        delivery_time = datetime.datetime.fromisoformat(delivery_time)
        estimated_completion_time = max(
            estimated_completion_time, delivery_time,
        )

    assert response_body['available_asap'] == (
        asap_by_place and asap_by_disable_threshold
    )
    slots = response_body['available_slots']
    expected_slots = make_expected_slots(
        estimated_completion_time, brand_id, working_intervals,
    )
    if not response_body['available_asap']:
        expected_slots[0]['select_by_default'] = True
    assert slots == expected_slots


@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.now('2021-07-14T11:00:00+03:00')
@pytest.mark.parametrize(
    'approximate_picking_time, expected_asap',
    [
        # заказ успеем собрать до закрытия - asap доступен
        (1000, True),
        # заказ успеем собрать до закрытия, но не успеем
        # до now + asap_disable_threshold - asap недоступен
        (1750, False),
        # заказ до закрытия не успеем собрать - asap недоступен
        (1900, False),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_asap_before_closing_shop_picking(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        approximate_picking_time,
        expected_asap,
        experiments3,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            approximate_picking_time=approximate_picking_time,
            asap_disable_threshold=1700,
        ),
        None,
    )

    now = utils.localize(now, 'Europe/Moscow')
    working_intervals = utils.make_working_intervals(
        now,
        [
            {
                'day_from': 0,
                'time_from': '08:00',
                'day_to': 0,
                'time_to': '11:30',
            },
        ],
    )
    mock_calculate_load.response['json']['places_load_info'][0].update(
        working_intervals=working_intervals, shop_picking_type='shop_picking',
    )
    order = utils.make_order(estimated_picking_time=1234)

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    assert response.json()['available_asap'] == expected_asap


@pytest.mark.now('2021-10-26T18:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.parametrize(
    'status_by_cache',
    [
        pytest.param(
            200,
            marks=[
                pytest.mark.eats_catalog_storage_cache(
                    file='catalog_storage_cache.json',
                ),
            ],
        ),
        404,
    ],
)
@pytest.mark.parametrize(
    'items, status_by_items',
    [
        ([utils.make_order_item(0)], 200),
        ([utils.make_order_item(0, public_id=None)], 200),
        ([utils.make_order_item(0, core_id=None)], 200),
        ([utils.make_order_item(0, core_id=None, public_id=None)], 400),
        ([utils.make_order_item(0, core_id='1', public_id=None)], 404),
    ],
)
# @pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_shop_picking_partner_slots_http_errors(
        taxi_eats_customer_slots,
        mockserver,
        mock_calculate_load,
        now,
        status_by_cache,
        items,
        status_by_items,
):
    place_id = 0
    brand_id = 0
    time_zone = 'Europe/Moscow'
    now = utils.localize(now, time_zone)
    working_intervals = utils.make_working_intervals(
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
                'time_to': '21:00',
            },
        ],
    )

    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=place_id,
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=working_intervals,
        shop_picking_type='shop_picking',
    )

    order = utils.make_order(
        place_id=place_id, brand_id=str(brand_id), items=items,
    )

    @mockserver.json_handler('/eats-products/internal/v2/products/public_id')
    def _mock_products_public_id(request):
        public_ids = {0: 'public_id_0'}
        return mockserver.make_response(
            json={
                'products_ids': [
                    {'core_id': core_id, 'public_id': public_ids.get(core_id)}
                    for core_id in request.json['core_ids']
                ],
            },
        )

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _mock_products_info(request):
        products_info = {
            'public_id_0': {
                'id': 'public_id_0',
                'origin_id': 'origin_id_0',
                'place_brand_id': str(brand_id),
                'name': 'name_0',
                'description': {},
                'is_choosable': True,
                'is_catch_weight': False,
                'adult': False,
                'shipping_type': 'pickup',
                'barcodes': [],
                'images': [],
                'is_sku': True,
            },
        }
        return mockserver.make_response(
            json={
                'products': [
                    products_info[public_id]
                    for public_id in request.json['product_ids']
                ],
            },
        )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    if status_by_cache == 404:
        assert response.status == 200
    else:
        assert response.status == status_by_items


def make_default_picking_slots(timezone='Europe/Moscow'):
    return [
        utils.make_picking_slot(
            '2021-10-20T12:10:00', '2021-10-20T13:10:00', 1800, timezone,
        ),
    ]


def make_default_delivery_slots(
        timezone='Europe/Moscow', select_by_default=None,
):
    return [
        utils.make_delivery_slot(
            '2021-10-20T12:00:00',
            '2021-10-20T13:00:00',
            '2021-10-20T12:00:00',
            timezone,
            select_by_default,
        ),
    ]


def make_param_partner_slots(
        expected_slots,
        expected_asap,
        time_zone='Europe/Moscow',
        delivery_time=None,
        time_to_customer=300,
        estimated_delivery_timepoint_shift=0,
        overall_time=None,
        picking_slots='default',
        marks=None,
):
    if picking_slots == 'default':
        picking_slots = make_default_picking_slots()
    return pytest.param(
        time_zone,
        delivery_time,
        time_to_customer,
        estimated_delivery_timepoint_shift,
        overall_time,
        picking_slots,
        expected_slots,
        expected_asap,
        marks=[] if marks is None else marks,
    )


@pytest.mark.now('2021-10-20T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.parametrize(
    'time_zone, delivery_time, time_to_customer, '
    'estimated_delivery_timepoint_shift, overall_time, picking_slots, '
    'expected_slots, expected_asap',
    [
        make_param_partner_slots(
            time_zone='Etc/GMT+10',
            picking_slots=make_default_picking_slots('Etc/GMT+10'),
            expected_slots=make_default_delivery_slots(
                'Etc/GMT+10', select_by_default=True,
            ),
            expected_asap=False,  # place is closed
        ),
        make_param_partner_slots(
            time_zone='UTC',
            picking_slots=make_default_picking_slots('UTC'),
            expected_slots=make_default_delivery_slots(
                'UTC', select_by_default=True,
            ),
            expected_asap=False,  # place is closed
        ),
        make_param_partner_slots(
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:01:00', '2021-10-20T12:29:00', 1800,
                ),
            ],
            expected_slots=make_default_delivery_slots(),
            expected_asap=True,
        ),
        make_param_partner_slots(
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:31:00', '2021-10-20T13:00:00', 1800,
                ),
            ],
            expected_slots=make_default_delivery_slots(select_by_default=True),
            expected_asap=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            expected_slots=make_default_delivery_slots(), expected_asap=True,
        ),
        make_param_partner_slots(
            overall_time=3000,
            expected_slots=make_default_delivery_slots(),
            expected_asap=True,
        ),
        make_param_partner_slots(
            overall_time=10800, expected_slots=[], expected_asap=True,
        ),
        make_param_partner_slots(
            estimated_delivery_timepoint_shift=600,
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    # estimated_delivery_timepoint_shift
                    '2021-10-20T12:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            time_to_customer=3900,
            estimated_delivery_timepoint_shift=600,
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    # estimated_delivery_timepoint_shift
                    '2021-10-20T13:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T11:00:00', '2021-10-20T12:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:00:00', '2021-10-20T14:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T16:00:00', '2021-10-20T17:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-21T11:00:00', '2021-10-21T12:00:00', 1800,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:00:00',
                    select_by_default=True,
                ),
                utils.make_delivery_slot(
                    '2021-10-20T16:00:00',
                    '2021-10-20T17:00:00',
                    '2021-10-20T16:00:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-21T11:00:00',
                    '2021-10-21T12:00:00',
                    '2021-10-21T11:00:00',
                ),
            ],
            expected_asap=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-21T11:00:00', '2021-10-21T12:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T16:00:00', '2021-10-20T17:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:00:00', '2021-10-20T14:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T13:00:00', 1800,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:00:00',
                    select_by_default=True,
                ),
                utils.make_delivery_slot(
                    '2021-10-20T16:00:00',
                    '2021-10-20T17:00:00',
                    '2021-10-20T16:00:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-21T11:00:00',
                    '2021-10-21T12:00:00',
                    '2021-10-21T11:00:00',
                ),
            ],
            expected_asap=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T12:20:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:20:00', '2021-10-20T12:40:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:40:00', '2021-10-20T14:00:00', 600,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            marks=utils.partner_picking_slots(),
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T12:20:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:20:00', '2021-10-20T12:40:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:40:00', '2021-10-20T14:00:00', 600,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            marks=utils.partner_picking_slots(60),
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T12:20:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:20:00', '2021-10-20T12:40:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:40:00', '2021-10-20T14:00:00', 600,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            marks=utils.partner_picking_slots(3600 * 5),
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T12:20:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:20:00', '2021-10-20T12:40:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:40:00', '2021-10-20T14:00:00', 600,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T14:00:00',
                    '2021-10-20T15:00:00',
                    '2021-10-20T14:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T15:00:00',
                    '2021-10-20T16:00:00',
                    '2021-10-20T15:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            marks=utils.partner_picking_slots(3600 * 3),
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:20:00', '2021-10-20T12:40:00', 600,
                ),
                utils.make_picking_slot(
                    '2021-10-20T17:20:00', '2021-10-20T17:40:00', 600,
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T13:00:00',
                    '2021-10-20T14:00:00',
                    '2021-10-20T13:10:00',
                ),
                utils.make_delivery_slot(
                    '2021-10-20T17:00:00',
                    '2021-10-20T18:00:00',
                    '2021-10-20T17:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            picking_slots=[],
            expected_slots=[],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Asia/Vladivostok',
            picking_slots=make_default_picking_slots('Asia/Vladivostok'),
            expected_slots=[],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Etc/GMT-9',
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T19:00:00',
                    '2021-10-20T20:00:00',
                    600,
                    'Etc/GMT-9',
                ),
            ],
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T19:00:00',
                    '2021-10-20T20:00:00',
                    '2021-10-20T19:10:00',
                    'Etc/GMT-9',
                    select_by_default=True,
                ),
            ],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Asia/Vladivostok',
            estimated_delivery_timepoint_shift=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T19:00:00',
                    '2021-10-20T20:00:00',
                    600,
                    'Asia/Vladivostok',
                ),
            ],
            expected_slots=[],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Asia/Kamchatka',
            estimated_delivery_timepoint_shift=600,
            picking_slots=make_default_picking_slots('Asia/Kamchatka'),
            expected_slots=[],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Etc/GMT-14',
            estimated_delivery_timepoint_shift=600,
            picking_slots=make_default_picking_slots('Etc/GMT-14'),
            expected_slots=[],
            expected_asap=False,  # no picking slots
        ),
        make_param_partner_slots(
            delivery_time='2021-10-20T09:00:00+03:00',
            expected_slots=make_default_delivery_slots(),
            expected_asap=True,
        ),
        make_param_partner_slots(
            delivery_time='2021-10-20T12:01:00+03:00',
            estimated_delivery_timepoint_shift=600,
            expected_slots=[
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    # estimated_delivery_timepoint_shift
                    '2021-10-20T12:10:00',
                ),
            ],
            expected_asap=True,
        ),
        make_param_partner_slots(
            delivery_time='2021-10-20T12:06:00+03:00',
            expected_slots=[
                # slots are filtering by end of slot
                utils.make_delivery_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    '2021-10-20T12:00:00',
                    select_by_default=True,
                ),
            ],
            # pre-order (> asap_delivery_time_mas_epsilon)
            expected_asap=False,
        ),
        make_param_partner_slots(
            delivery_time='2021-10-20T22:06:00+03:00',
            estimated_delivery_timepoint_shift=600,
            expected_slots=[],
            # pre-order (> asap_delivery_time_mas_epsilon)
            expected_asap=False,
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_shop_picking_partner_slots(
        taxi_eats_customer_slots,
        experiments3,
        mockserver,
        mock_calculate_load,
        time_zone,
        delivery_time,
        time_to_customer,
        estimated_delivery_timepoint_shift,
        overall_time,
        picking_slots,
        expected_asap,
        expected_slots,
        now,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            estimated_delivery_timepoint_shift, asap_disable_threshold=1800,
        ),
        None,
    )
    brand_id = 0
    place_id = 0
    now = utils.localize(now, time_zone)
    working_intervals = utils.make_working_intervals(
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
                'time_to': '21:00',
            },
        ],
    )

    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=place_id,
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=working_intervals,
        shop_picking_type='shop_picking',
    )

    order = utils.make_order(
        time_to_customer=time_to_customer,
        place_id=place_id,
        brand_id=str(brand_id),
        delivery_time=delivery_time,
        overall_time=overall_time,
    )
    for item in order['items']:
        item['quantum'] = 500
        item['measure_value'] = '1.0'

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    def __mock_get_picking_slots(request):
        if 'items' in request.json:
            for order_item, request_item in zip(
                    order['items'], request.json['items'],
            ):
                measure_value_quantity = (
                    order_item['quantum']
                    * order_item['quantity']
                    / (float(order_item['measure_value']) * 1000)
                )
                assert request_item['quantity'] == measure_value_quantity

        if picking_slots is not None:
            return mockserver.make_response(
                json={'picking_slots': picking_slots},
            )
        return mockserver.make_response(
            status=404, json={'code': 'not_found', 'message': 'Not Found'},
        )

    @mockserver.json_handler('/eats-products/internal/v2/products/public_id')
    def _mock_products_public_id(request):
        public_ids = {0: 'public_id_0'}
        return mockserver.make_response(
            json={
                'products_ids': [
                    {'core_id': core_id, 'public_id': public_ids.get(core_id)}
                    for core_id in request.json['core_ids']
                ],
            },
        )

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _mock_products_info(request):
        products_info = {
            'public_id_0': {
                'id': 'public_id_0',
                'origin_id': 'origin_id_0',
                'place_brand_id': str(brand_id),
                'name': 'name_0',
                'description': {},
                'is_choosable': True,
                'is_catch_weight': False,
                'adult': False,
                'shipping_type': 'pickup',
                'barcodes': [],
                'images': [],
                'is_sku': True,
            },
        }
        return mockserver.make_response(
            json={
                'products': [
                    products_info[public_id]
                    for public_id in request.json['product_ids']
                ],
            },
        )

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    response_body = response.json()

    assert response_body['available_asap'] == expected_asap
    assert response_body['available_slots'] == expected_slots
