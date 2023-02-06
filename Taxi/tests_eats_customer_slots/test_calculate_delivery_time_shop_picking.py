import datetime

import pytest

from tests_eats_customer_slots import utils


def make_param_our_slots(
        expected_delivery_timepoint,
        expected_asap_availability,
        time_zone='Europe/Moscow',
        delivery_time=None,
        delivery_day=None,
        estimated_delivery_duration=0,
        estimated_delivery_timepoint_shift=0,
        asap_delivery_time_max_epsilon=0,
        finish_working_interval_offset=0,
        approximate_picking_time=0,
):
    return [
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        estimated_delivery_timepoint_shift,
        asap_delivery_time_max_epsilon,
        finish_working_interval_offset,
        approximate_picking_time,
        expected_delivery_timepoint,
        expected_asap_availability,
    ]


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'time_zone, delivery_time, delivery_day, '
    'estimated_delivery_duration, estimated_delivery_timepoint_shift, '
    'asap_delivery_time_max_epsilon, finish_working_interval_offset, '
    'approximate_picking_time, expected_delivery_timepoint, '
    'expected_asap_availability',
    [
        make_param_our_slots(
            time_zone='Etc/GMT+11',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00-11:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_our_slots(
            time_zone='Etc/UTC',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00+00:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_our_slots(
            time_zone='Etc/GMT-2',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T11:00:00+02:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            time_zone='Asia/Vladivostok',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T19:00:00+10:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            time_zone='Asia/Kamchatka',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+12:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_our_slots(
            time_zone='Etc/GMT-14',
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+14:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_our_slots(
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            estimated_delivery_timepoint_shift=1900,
            approximate_picking_time=1850,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_our_slots(
            estimated_delivery_duration=1800,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1799,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            estimated_delivery_timepoint_shift=1000,
            approximate_picking_time=1200,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            delivery_time='09:00',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            asap_delivery_time_max_epsilon=120,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_our_slots(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_duration=29,
            estimated_delivery_timepoint_shift=60,
            approximate_picking_time=30,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_duration=31,
            estimated_delivery_timepoint_shift=60,
            approximate_picking_time=30,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='18:00',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T18:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='19:30',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T19:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='19:31',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='20:50',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='18:00',
            delivery_day=1,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T18:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_our_slots(
            delivery_time='20:00',
            delivery_day=1,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=None,
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
    ],
)
async def test_calculate_delivery_time_shop_picking(
        taxi_eats_customer_slots,
        make_expected_delivery_time_info,
        mock_calculate_load,
        experiments3,
        now,
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        estimated_delivery_timepoint_shift,
        asap_delivery_time_max_epsilon,
        finish_working_interval_offset,
        approximate_picking_time,
        expected_delivery_timepoint,
        expected_asap_availability,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            asap_disable_threshold=1800,
            estimated_delivery_timepoint_shift=(
                estimated_delivery_timepoint_shift
            ),
            approximate_picking_time=approximate_picking_time,
            asap_delivery_time_max_epsilon=asap_delivery_time_max_epsilon,
        ),
        None,
    )
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

    request_body = {
        'places': [
            {
                'place_id': 123456,
                'estimated_delivery_duration': estimated_delivery_duration,
            },
        ],
        'device_id': '1',
        'delivery_time': delivery_time,
        'personal_phone_id': 'abc123edf567',
    }
    if delivery_time:
        delivery_timepoint = utils.make_datetime(
            now.date() + datetime.timedelta(days=delivery_day),
            delivery_time,
            now.tzinfo,
        )
        request_body['delivery_time'] = {
            'time': delivery_timepoint.replace(tzinfo=None).isoformat(),
            'zone': time_zone,
        }
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body == {
        'places': [
            make_expected_delivery_time_info(
                '123456',
                now,
                asap_availability=expected_asap_availability,
                delivery_timepoint=expected_delivery_timepoint,
            ),
        ],
    }


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
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
async def test_calculate_delivery_time_asap_before_closing_shop_picking(
        taxi_eats_customer_slots,
        mock_calculate_load,
        experiments3,
        now,
        approximate_picking_time,
        expected_asap,
):
    place_id = 123456
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            asap_disable_threshold=1700,
            approximate_picking_time=approximate_picking_time,
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

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time',
        json={
            'places': [
                {'place_id': place_id, 'estimated_delivery_duration': 0},
            ],
            'device_id': '1',
        },
    )
    assert response.status == 200
    places = response.json()['places']
    assert places[0]['place_id'] == str(place_id)
    assert places[0]['asap_availability'] == expected_asap


def make_default_picking_slots(timezone='Europe/Moscow'):
    return [
        utils.make_picking_slot(
            '2021-10-20T12:10:00', '2021-10-20T13:10:00', 1800, timezone,
        ),
    ]


def make_param_partner_slots(
        expected_delivery_timepoint,
        expected_asap_availability,
        time_zone='Europe/Moscow',
        delivery_time=None,
        delivery_day=None,
        estimated_delivery_duration=0,
        picking_slots='default',
):
    if picking_slots == 'default':
        picking_slots = make_default_picking_slots()
    return [
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        picking_slots,
        expected_delivery_timepoint,
        expected_asap_availability,
    ]


@pytest.mark.now('2021-10-20T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.parametrize(
    'time_zone, delivery_time, delivery_day, estimated_delivery_duration, '
    'picking_slots, expected_delivery_timepoint, expected_asap_availability',
    [
        make_param_partner_slots(
            time_zone='Etc/GMT+11',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T10:00:00-11:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_partner_slots(
            time_zone='Etc/UTC',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T10:00:00+00:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_partner_slots(
            time_zone='Etc/GMT-2',
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T12:00:00',
                    '2021-10-20T13:00:00',
                    1800,
                    'Etc/GMT-2',
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+02:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            time_zone='Asia/Vladivostok',
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T20:00:00',
                    '2021-10-20T21:00:00',
                    1800,
                    'Asia/Vladivostok',
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-21T10:00:00+10:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            time_zone='Asia/Vladivostok',
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T19:10:00',
                    '2021-10-20T19:30:00',
                    1200,
                    'Asia/Vladivostok',
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T19:00:00+10:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            time_zone='Asia/Kamchatka',
            picking_slots=make_default_picking_slots('Asia/Kamchatka'),
            expected_delivery_timepoint=None,
            expected_asap_availability=False,  # no picking slots
        ),
        make_param_partner_slots(
            time_zone='Asia/Kamchatka',
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T21:10:00',
                    '2021-10-20T22:00:00',
                    1800,
                    'Asia/Kamchatka',
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-21T10:00:00+12:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_partner_slots(
            time_zone='Etc/GMT-14',
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-20T23:00:00',
                    '2021-10-21T00:00:00',
                    1800,
                    'Asia/Kamchatka',
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-21T10:00:00+14:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_partner_slots(
            estimated_delivery_duration=600,
            picking_slots=[],
            expected_delivery_timepoint=None,
            expected_asap_availability=False,  # no picking slots
        ),
        make_param_partner_slots(
            estimated_delivery_duration=600,
            picking_slots=None,
            expected_delivery_timepoint=None,
            expected_asap_availability=False,  # no picking slots
        ),
        make_param_partner_slots(
            estimated_delivery_duration=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-21T10:00:00', '2021-10-21T11:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T15:00:00', '2021-10-20T16:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:00:00', '2021-10-20T13:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T13:00:00', '2021-10-20T14:00:00', 1800,
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T13:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_partner_slots(
            estimated_delivery_duration=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-21T10:01:00', '2021-10-21T11:01:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T15:01:00', '2021-10-20T16:01:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T12:01:00', '2021-10-20T13:01:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T11:01:00', '2021-10-20T12:01:00', 1800,
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            estimated_delivery_duration=600,
            picking_slots=[
                utils.make_picking_slot(
                    '2021-10-21T10:00:00', '2021-10-21T11:00:00', 1800,
                ),
                utils.make_picking_slot(
                    '2021-10-20T16:00:00', '2021-10-20T17:00:00', 1800,
                ),
            ],
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T16:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_delivery_threshold
        ),
        make_param_partner_slots(
            estimated_delivery_duration=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            estimated_delivery_duration=1900,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            estimated_delivery_duration=3700,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            delivery_time='09:00',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_partner_slots(
            delivery_time='12:06',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T12:00:00+03:00',
            ),
            # > pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_partner_slots(
            delivery_time='18:00',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T18:00:00+03:00',
            ),
            # > pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_partner_slots(
            delivery_time='19:30',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-20T19:00:00+03:00',
            ),
            # > pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
        make_param_partner_slots(
            delivery_time='20:50',
            delivery_day=0,
            estimated_delivery_duration=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-10-21T10:00:00+03:00',
            ),
            # > pre-order (> asap_delivery_time_max_epsilon)
            expected_asap_availability=False,
        ),
    ],
)
async def test_calculate_delivery_time_shop_picking_partner_slots(
        taxi_eats_customer_slots,
        mockserver,
        make_expected_delivery_time_info,
        mock_calculate_load,
        experiments3,
        now,
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        picking_slots,
        expected_delivery_timepoint,
        expected_asap_availability,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(asap_disable_threshold=1800), None,
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

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    def __mock_get_picking_slots(request):
        if picking_slots is not None:
            return mockserver.make_response(
                json={'picking_slots': picking_slots},
            )
        return mockserver.make_response(
            status=404, json={'code': 'not_found', 'message': 'Not Found'},
        )

    request_body = {
        'places': [
            {
                'place_id': place_id,
                'estimated_delivery_duration': estimated_delivery_duration,
            },
        ],
        'device_id': '1',
        'delivery_time': delivery_time,
        'personal_phone_id': 'abc123edf567',
    }
    if delivery_time:
        delivery_timepoint = utils.make_datetime(
            now.date() + datetime.timedelta(days=delivery_day),
            delivery_time,
            now.tzinfo,
        )
        request_body['delivery_time'] = {
            'time': delivery_timepoint.replace(tzinfo=None).isoformat(),
            'zone': time_zone,
        }
    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body == {
        'places': [
            make_expected_delivery_time_info(
                str(place_id),
                now,
                asap_availability=expected_asap_availability,
                delivery_timepoint=expected_delivery_timepoint,
            ),
        ],
    }
