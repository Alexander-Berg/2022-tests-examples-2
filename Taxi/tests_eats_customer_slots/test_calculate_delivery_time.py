# pylint: disable=too-many-lines

import datetime
import locale

import pytest

from tests_eats_customer_slots import utils


@pytest.fixture(autouse=True)
def set_locale():
    locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


def slots_unavailable_response(place_id=123456):
    return {
        'place_id': str(place_id),
        'short_text': utils.DEFAULT_TEXT_FORMATS[
            'short_text_slots_unavailable'
        ],
        'full_text': utils.DEFAULT_TEXT_FORMATS['full_text_slots_unavailable'],
        'delivery_eta': 0,
        'slots_availability': False,
        'asap_availability': True,
    }


def delivery_unavailable_response(place_id=123456):
    return {
        'place_id': str(place_id),
        'short_text': utils.DEFAULT_TEXT_FORMATS[
            'short_text_delivery_unavailable'
        ],
        'full_text': utils.DEFAULT_TEXT_FORMATS[
            'full_text_delivery_unavailable'
        ],
        'delivery_eta': 0,
        'slots_availability': False,
        'asap_availability': False,
    }


def make_param_free_pickers(
        expected_delivery_timepoint,
        expected_asap_availability,
        time_zone='Europe/Moscow',
        delivery_time=None,
        delivery_day=None,
        estimated_delivery_duration=0,
        estimated_delivery_timepoint_shift=0,
        asap_delivery_time_max_epsilon=0,
        approximate_picking_time=0,
):
    return [
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        estimated_delivery_timepoint_shift,
        asap_delivery_time_max_epsilon,
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
    'time_zone, delivery_time, delivery_day, estimated_delivery_duration, '
    'estimated_delivery_timepoint_shift, asap_delivery_time_max_epsilon, '
    'approximate_picking_time, expected_delivery_timepoint, '
    'expected_asap_availability',
    [
        make_param_free_pickers(
            time_zone='Etc/GMT+10',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00-10:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='UTC',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00+00:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='Etc/GMT-2',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T11:00:00+02:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            time_zone='Asia/Vladivostok',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T19:00:00+10:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            time_zone='Asia/Kamchatka',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+12:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            time_zone='Etc/GMT-14',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+14:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_free_pickers(
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            estimated_delivery_duration=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            estimated_delivery_duration=1900,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            approximate_picking_time=1900,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_free_pickers(
            estimated_delivery_duration=1000,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            estimated_delivery_duration=1000,
            estimated_delivery_timepoint_shift=900,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            approximate_picking_time=7400,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T15:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_free_pickers(
            approximate_picking_time=7400,
            estimated_delivery_timepoint_shift=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T14:00:00+03:00',
            ),
            expected_asap_availability=False,  # > asap_disable_threshold
        ),
        make_param_free_pickers(
            delivery_time='09:00',
            delivery_day=0,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            delivery_time='12:01',
            delivery_day=0,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:01',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:01',
            delivery_day=0,
            asap_delivery_time_max_epsilon=120,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_free_pickers(
            delivery_time='12:15',
            delivery_day=0,
            estimated_delivery_duration=800,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:15',
            delivery_day=0,
            estimated_delivery_duration=1900,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:15',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            asap_delivery_time_max_epsilon=300,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='18:00',
            delivery_day=0,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T18:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='23:59',
            delivery_day=0,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='18:00',
            delivery_day=1,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T18:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='23:59',
            delivery_day=1,
            expected_delivery_timepoint=None,
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:15',
            delivery_day=0,
            estimated_delivery_timepoint_shift=600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            delivery_time='12:15',
            delivery_day=0,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='19:15',
            delivery_day=1,
            estimated_delivery_timepoint_shift=600,
            expected_delivery_timepoint=None,
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_free_pickers(
            time_zone='UTC',
            delivery_time='19:15',
            delivery_day=1,
            estimated_delivery_timepoint_shift=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T19:00:00+00:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
    ],
)
async def test_calculate_delivery_time_free_pickers(
        taxi_eats_customer_slots,
        experiments3,
        make_expected_delivery_time_info,
        mock_calculate_load,
        time_zone,
        now,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        estimated_delivery_timepoint_shift,
        asap_delivery_time_max_epsilon,
        approximate_picking_time,
        expected_delivery_timepoint,
        expected_asap_availability,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            estimated_delivery_timepoint_shift,
            asap_disable_threshold=1800,
            approximate_picking_time=approximate_picking_time,
            asap_delivery_time_max_epsilon=asap_delivery_time_max_epsilon,
        ),
        None,
    )
    brand_id = 1
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
                    'time_to': '21:00',
                },
            ],
        ),
        shop_picking_type='our_picking',
    )

    await taxi_eats_customer_slots.invalidate_caches()

    request_body = {
        'places': [
            {
                'place_id': 123456,
                'estimated_delivery_duration': estimated_delivery_duration,
            },
        ],
        'device_id': '1',
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


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.settings_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_customer_slots_daily_slots',
    consumers=[
        'eats-customer-slots/calculate-slots',
        'eats-customer-slots/calculate-delivery-time',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'daily_slots': [
            {
                'day': d,
                'slots': [
                    {'start': f'{h:02}:00', 'end': f'{h+1:02}:00'}
                    for h in range(8, 20)
                ],
            }
            for d in range(30)
        ],
    },
)
@utils.text_formats_config()
async def test_calculate_delivery_time_multiple_places(
        taxi_eats_customer_slots,
        make_expected_delivery_time_info,
        mock_calculate_load,
        now,
):
    time_zone = 'Europe/Moscow'
    total_places = 30
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'] = [
        dict(
            mock_calculate_load.place_load_info_stub,
            time_zone=time_zone,
            place_id=day,
            working_intervals=utils.make_working_intervals(
                now,
                [
                    {
                        'day_from': day,
                        'time_from': '10:00',
                        'day_to': day,
                        'time_to': '21:00',
                    },
                ],
            ),
            shop_picking_type='our_picking',
        )
        for day in range(1, total_places)
    ]

    await taxi_eats_customer_slots.invalidate_caches()
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time',
        headers={'x-platform': 'check_place_working_days_platform'},
        json={
            'places': [
                {'place_id': place_id, 'estimated_delivery_duration': 0}
                for place_id in range(1, total_places)
            ],
            'device_id': '1',
        },
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body == {
        'places': [
            make_expected_delivery_time_info(
                str(day),
                now,
                asap_availability=False,
                delivery_timepoint=utils.make_datetime(
                    utils.add_days(now.date(), day), '10:00', now.tzinfo,
                ),
            )
            for day in range(1, total_places)
        ],
    }


def make_param_no_free_pickers(
        expected_delivery_timepoint,
        expected_asap_availability,
        time_zone='Europe/Moscow',
        delivery_time=None,
        delivery_day=None,
        estimated_delivery_duration=0,
        total_pickers_count=0,
        estimated_waiting_time=0,
        estimated_delivery_timepoint_shift=0,
        approximate_picking_time=0,
        asap_disable_threshold=360,
):
    return [
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        total_pickers_count,
        estimated_waiting_time,
        estimated_delivery_timepoint_shift,
        approximate_picking_time,
        asap_disable_threshold,
        expected_delivery_timepoint,
        expected_asap_availability,
    ]


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'time_zone, delivery_time, delivery_day, estimated_delivery_duration, '
    'total_pickers_count, estimated_waiting_time, '
    'estimated_delivery_timepoint_shift, approximate_picking_time, '
    'asap_disable_threshold, expected_delivery_timepoint, '
    'expected_asap_availability',
    [
        make_param_no_free_pickers(
            time_zone='Etc/GMT+11',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00-11:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            time_zone='Etc/UTC',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T10:00:00-00:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            time_zone='Etc/GMT-2',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T11:00:00+02:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            time_zone='Asia/Vladivostok',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T19:00:00+10:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            time_zone='Asia/Kamchatka',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+12:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_no_free_pickers(
            time_zone='Etc/GMT-14',
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+14:00',
            ),
            expected_asap_availability=False,  # place is closed
        ),
        make_param_no_free_pickers(
            total_pickers_count=2,
            estimated_waiting_time=300,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=10,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_no_free_pickers(
            total_pickers_count=2,
            estimated_waiting_time=900,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            total_pickers_count=2,
            estimated_delivery_duration=400,
            estimated_waiting_time=300,
            estimated_delivery_timepoint_shift=1600,
            approximate_picking_time=1000,
            asap_disable_threshold=1900,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_no_free_pickers(
            delivery_time='09:00',
            delivery_day=0,
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='12:04',
            delivery_day=0,
            total_pickers_count=2,
            estimated_waiting_time=600,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='12:06',
            delivery_day=0,
            total_pickers_count=2,
            estimated_waiting_time=600,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T12:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='12:04',
            delivery_day=0,
            estimated_delivery_duration=400,
            total_pickers_count=2,
            estimated_waiting_time=300,
            estimated_delivery_timepoint_shift=1600,
            approximate_picking_time=1000,
            asap_disable_threshold=1800,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            expected_asap_availability=True,
        ),
        make_param_no_free_pickers(
            delivery_time='12:04',
            delivery_day=0,
            estimated_delivery_duration=1800,
            total_pickers_count=2,
            estimated_waiting_time=600,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T13:00:00+03:00',
            ),
            # no free pickers, waiting too long
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='19:30',
            delivery_day=0,
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-19T19:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='19:31',
            delivery_day=0,
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T10:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='18:00',
            delivery_day=1,
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2021-03-20T18:00:00+03:00',
            ),
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
        make_param_no_free_pickers(
            delivery_time='20:00',
            delivery_day=1,
            total_pickers_count=2,
            estimated_waiting_time=500,
            estimated_delivery_timepoint_shift=1800,
            approximate_picking_time=1000,
            expected_delivery_timepoint=None,
            # pre-order (> asap_delivery_time_epsilon)
            expected_asap_availability=False,
        ),
    ],
)
async def test_calculate_delivery_time_no_free_pickers(
        taxi_eats_customer_slots,
        make_expected_delivery_time_info,
        mock_calculate_load,
        experiments3,
        now,
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        total_pickers_count,
        estimated_waiting_time,
        estimated_delivery_timepoint_shift,
        approximate_picking_time,
        asap_disable_threshold,
        expected_delivery_timepoint,
        expected_asap_availability,
):
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            asap_disable_threshold=asap_disable_threshold,
            estimated_delivery_timepoint_shift=(
                estimated_delivery_timepoint_shift
            ),
            approximate_picking_time=approximate_picking_time,
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
        free_pickers_count=0,
        total_pickers_count=total_pickers_count,
        estimated_waiting_time=estimated_waiting_time,
        working_intervals=working_intervals,
        shop_picking_type='our_picking',
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


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'delivery_time, delivery_day, expected_places',
    [
        [
            None,
            None,
            [
                {
                    'asap_availability': True,
                    'delivery_eta': 43200,
                    'full_text': 'Завтра к 00:00',
                    'place_id': '123456',
                    'short_text': 'Завтра 00:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            '18:00',
            0,
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 43200,
                    'full_text': 'Завтра к 00:00',
                    'place_id': '123456',
                    'short_text': 'Завтра 00:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            '23:59',
            0,
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 43200,
                    'full_text': 'Завтра к 00:00',
                    'place_id': '123456',
                    'short_text': 'Завтра 00:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            '18:00',
            1,
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 108000,
                    'full_text': 'Завтра к 18:00',
                    'place_id': '123456',
                    'short_text': 'Завтра 18:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            '23:59',
            1,
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 0,
                    'full_text': 'доставка недоступна',
                    'place_id': '123456',
                    'short_text': 'доставка недоступна',
                    'slots_availability': False,
                },
            ],
        ],
    ],
)
async def test_calculate_delivery_time_no_day_0(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        delivery_time,
        delivery_day,
        expected_places,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=utils.NEXT_DAY_BRAND,
    )

    await taxi_eats_customer_slots.invalidate_caches()
    request_body = {
        'places': [{'place_id': 123456, 'estimated_delivery_duration': 0}],
        'device_id': '1',
    }
    if delivery_time:
        delivery_timepoint = utils.make_datetime(
            now.date() + datetime.timedelta(days=delivery_day),
            delivery_time,
            now.tzinfo,
        )
        request_body['delivery_time'] = {
            'time': delivery_timepoint.replace(tzinfo=None).isoformat(),
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    assert response.json() == {'places': expected_places}


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'delivery_time, delivery_day',
    [[None, None], ['18:00', 0], ['23:59', 0], ['18:00', 1], ['23:59', 1]],
)
async def test_calculate_delivery_time_place_disabled(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        delivery_time,
        delivery_day,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        enabled=False,
    )

    await taxi_eats_customer_slots.invalidate_caches()
    request_body = {
        'places': [{'place_id': 123456, 'estimated_delivery_duration': 0}],
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
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    assert response.json() == {
        'places': [delivery_unavailable_response(123456)],
    }


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@utils.settings_config()
@pytest.mark.parametrize(
    '', [pytest.param(), pytest.param(marks=utils.daily_slots_config())],
)
@pytest.mark.parametrize(
    'delivery_time, delivery_day',
    [[None, None], ['18:00', 0], ['23:59', 0], ['18:00', 1], ['23:59', 1]],
)
async def test_calculate_delivery_time_empty_slots(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        delivery_time,
        delivery_day,
):
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=utils.EMPTY_BRAND,
    )
    await taxi_eats_customer_slots.invalidate_caches()
    request_body = {
        'places': [{'place_id': 123456, 'estimated_delivery_duration': 0}],
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
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    assert response.json() == {'places': []}


@pytest.mark.now('2021-03-19T12:00:00+03:00')
@utils.slots_enabled()
@utils.settings_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'calculate_load_response',
    [{'status': 500}, {'json': {'places_load_info': []}}],
    ids=['calculate_load_error', 'empty_places_load_info'],
)
@pytest.mark.parametrize(
    'delivery_time, delivery_day',
    [[None, None], ['18:00', 0], ['23:59', 0], ['18:00', 1], ['23:59', 1]],
)
async def test_calculate_delivery_time_empty_cache(
        taxi_eats_customer_slots,
        mock_calculate_load,
        calculate_load_response,
        now,
        delivery_time,
        delivery_day,
):
    mock_calculate_load.response = calculate_load_response
    await taxi_eats_customer_slots.invalidate_caches()
    request_body = {
        'places': [{'place_id': 1, 'estimated_delivery_duration': 0}],
        'device_id': '1',
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
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    assert response.json() == {'places': [slots_unavailable_response(1)]}


@utils.slots_enabled()
@utils.settings_config()
@pytest.mark.parametrize(
    'request_body',
    [
        {'places': [], 'device_id': '1'},
        {'places': [{'place_id': 1, 'estimated_delivery_duration': 0}]},
    ],
)
async def test_calculate_delivery_time_bad_request_400(
        taxi_eats_customer_slots, request_body,
):
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 400


@utils.slots_disabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-03-05T12:00:00+03:00')
@pytest.mark.parametrize(
    'delivery_time, delivery_day',
    [[None, None], ['18:00', 0], ['23:59', 0], ['18:00', 1], ['23:59', 1]],
)
async def test_calculate_delivery_time_slots_disabled(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        delivery_time,
        delivery_day,
):
    await taxi_eats_customer_slots.invalidate_caches()
    request_body = {
        'places': [{'place_id': 123456, 'estimated_delivery_duration': 0}],
        'device_id': '1',
        'phone_id': 'abc123edf567',
    }
    if delivery_time:
        delivery_timepoint = utils.make_datetime(
            now.date() + datetime.timedelta(days=delivery_day),
            delivery_time,
            now.tzinfo,
        )
        request_body['delivery_time'] = {
            'time': delivery_timepoint.replace(tzinfo=None).isoformat(),
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time', json=request_body,
    )
    assert response.status == 200
    assert response.json() == {'places': []}


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.now('2021-07-14T11:00:00+03:00')
@pytest.mark.parametrize(
    'total_pickers, free_pickers, estimated_waiting_time,'
    'approximate_picking_time, expected_asap',
    [
        # Нет пикеров вообще - нет asap
        (0, 0, 1200, 500, False),
        # Нет свободных пикеров и ждать слишком долго - asap недоступен
        (2, 0, 1200, 550, False),
        # Нет свободных сборщиков, но скоро будут, и заказ успеем собрать
        # до закрытия - asap доступен
        (2, 0, 600, 120, True),
        # Нет свободных сборщиков, но скоро будут, и заказ успеем собрать
        # до закрытия, но не успеем до asap_disable_threshold -
        # asap недоступен
        (2, 0, 600, 1150, False),
        # Нет свободных сборщиков, но скоро будут, и заказ до закрытия
        # не успеем собрать - asap недоступен
        (2, 0, 600, 1300, False),
        # Есть свободные сборщики, и заказ успеем собрать до закрытия -
        # asap доступен
        (2, 2, 600, 120, True),
        # Есть свободные сборщики, и заказ успеем собрать до закрытия,
        # но не успеем до asap_disable_threshold -
        # asap недоступен
        (2, 2, 600, 1750, False),
        # Есть свободные сборщики, но заказ до закрытия не успеем собрать -
        # asap недоступен
        (2, 2, 600, 2000, False),
    ],
)
async def test_calculate_delivery_time_asap_before_closing(
        taxi_eats_customer_slots,
        mock_calculate_load,
        experiments3,
        now,
        total_pickers,
        free_pickers,
        estimated_waiting_time,
        approximate_picking_time,
        expected_asap,
):
    place_id = 123456
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            asap_disable_threshold=1000,
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
        free_pickers_count=free_pickers,
        total_pickers_count=total_pickers,
        estimated_waiting_time=estimated_waiting_time,
        working_intervals=working_intervals,
        shop_picking_type='our_picking',
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


@pytest.mark.now('2022-06-09T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'brand_id, delivery_time, expected_places',
    [
        [
            1,
            None,
            [
                {
                    'asap_availability': True,
                    'delivery_eta': 0,
                    'full_text': 'Сегодня к 12:00',
                    'place_id': '123456',
                    'short_text': 'Сегодня 12:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            1,
            '2022-06-09T14:10:00',
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 3600 * 3,
                    'full_text': 'Сегодня с 15:00 до 16:00',
                    'place_id': '123456',
                    'short_text': 'Сегодня с 15:00 до 16:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            utils.NEXT_DAY_BRAND,
            '2022-06-10T12:10:00',
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 3600 * 25,
                    'full_text': 'Завтра с 13:00 до 14:00',
                    'place_id': '123456',
                    'short_text': 'Завтра с 13:00 до 14:00',
                    'slots_availability': True,
                },
            ],
        ],
        [
            utils.X3_DAY_BRAND,
            '2022-06-12T12:10:00',
            [
                {
                    'asap_availability': False,
                    'delivery_eta': 3600 * (24 * 3 + 1),
                    'full_text': '12 июня, с 13:00 до 14:00',
                    'place_id': '123456',
                    'short_text': '12 июня, с 13:00 до 14:00',
                    'slots_availability': True,
                },
            ],
        ],
    ],
)
@utils.text_formats_config()
async def test_calculate_delivery_time_full_slot_text_format(
        taxi_eats_customer_slots,
        mock_calculate_load,
        now,
        brand_id,
        delivery_time,
        expected_places,
):
    time_zone = 'Europe/Moscow'
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        brand_id=brand_id,
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
                    'time_to': '21:00',
                },
                {
                    'day_from': 3,
                    'time_from': '10:00',
                    'day_to': 3,
                    'time_to': '21:00',
                },
            ],
        ),
    )

    await taxi_eats_customer_slots.invalidate_caches(
        clean_update=True, cache_names=['places-load-info-cache'],
    )

    request_body = {
        'places': [{'place_id': 123456, 'estimated_delivery_duration': 0}],
        'device_id': '1',
    }
    if delivery_time:
        request_body['delivery_time'] = {
            'time': delivery_time,
            'zone': 'Europe/Moscow',
        }
    response = await taxi_eats_customer_slots.post(
        '/api/v1/places/calculate-delivery-time',
        json=request_body,
        headers={'X-App-Version': '1.2 (345)'},
    )
    assert response.status == 200
    assert response.json() == {'places': expected_places}
