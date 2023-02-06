import datetime

import pytest

from tests_eats_customer_slots import utils


def make_params(
        delivery_time,
        expected_delivery_availability,
        expected_asap,
        delivery_day=0,
        time_zone='Europe/Moscow',
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
        expected_delivery_availability,
        expected_asap,
    ]


def make_testcases():
    common_params = [
        make_params(
            time_zone='Etc/GMT+1',
            delivery_time='09:59',
            expected_delivery_availability=False,  # place is closed
            expected_asap=False,
        ),
        make_params(
            time_zone='Etc/GMT+1',
            delivery_time='10:00',
            expected_delivery_availability=True,
            expected_asap=False,
        ),
        make_params(
            time_zone='Etc/GMT+1',
            delivery_time='11:00',
            expected_delivery_availability=True,
            expected_asap=False,
        ),
        make_params(
            time_zone='Etc/GMT+1',
            delivery_time='11:00',
            approximate_picking_time=4000,
            # should start picking when place is closed
            expected_delivery_availability=False,
            expected_asap=False,
        ),
        make_params(
            time_zone='Etc/GMT+1',
            delivery_time='11:00',
            estimated_delivery_duration=4000,
            # should start delivery when place is closed
            expected_delivery_availability=False,
            expected_asap=False,
        ),
        make_params(
            delivery_time=None,
            expected_delivery_availability=True,
            expected_asap=True,
        ),
        make_params(
            delivery_time=None,
            approximate_picking_time=4000,
            expected_delivery_availability=True,
            expected_asap=True,
        ),
        make_params(
            delivery_time='12:00',
            expected_delivery_availability=True,
            expected_asap=True,
        ),
        make_params(
            delivery_time='12:10',
            expected_delivery_availability=True,
            expected_asap=False,
        ),
        make_params(
            delivery_time='12:10',
            asap_delivery_time_max_epsilon=4000,
            expected_delivery_availability=True,
            expected_asap=True,
        ),
        make_params(
            delivery_time='20:59',
            expected_delivery_availability=True,
            expected_asap=False,
        ),
        make_params(
            delivery_time='21:00',
            expected_delivery_availability=False,  # place is closed
            expected_asap=False,
        ),
        make_params(
            time_zone='Etc/GMT-10',
            asap_delivery_time_max_epsilon=8000,
            estimated_delivery_duration=8000,
            delivery_time='21:00',
            expected_delivery_availability=True,
            expected_asap=True,
        ),
    ]

    no_picking_slots_place_params = [
        [0, 'our_picking', None],
        [0, 'shop_picking', None],
    ]
    shop_picking_slots_place_params = [
        [
            1,
            'shop_picking',
            [
                [f'2022-05-11T{h}:00:00', f'2022-05-11T{h+1}:00:00', 3600]
                for h in range(10, 21)
            ],
        ],
    ]
    return (
        [
            params + picking_slot_params
            for params in common_params
            for picking_slot_params in (
                no_picking_slots_place_params + shop_picking_slots_place_params
            )
        ]
        + [
            params
            for picking_slot_params, expected_asap in zip(
                no_picking_slots_place_params
                + shop_picking_slots_place_params,
                [False] * len(no_picking_slots_place_params)
                + [True] * len(shop_picking_slots_place_params),
            )
            for params in [
                make_params(
                    delivery_time=None,
                    approximate_picking_time=8000,
                    expected_delivery_availability=True,
                    # approximate_picking_time > asap_disable_threshold
                    expected_asap=expected_asap,
                )
                + picking_slot_params,
                make_params(
                    time_zone='Etc/GMT-10',
                    asap_delivery_time_max_epsilon=8000,
                    approximate_picking_time=8000,
                    delivery_time='21:00',
                    expected_delivery_availability=True,
                    expected_asap=expected_asap,
                )
                + picking_slot_params,
            ]
        ]
    )


@pytest.mark.now('2022-05-11T12:00:00+03:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.text_formats_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize(
    'time_zone, delivery_time, delivery_day, estimated_delivery_duration, '
    'estimated_delivery_timepoint_shift, asap_delivery_time_max_epsilon, '
    'approximate_picking_time, expected_delivery_availability, '
    'expected_asap, brand_id, shop_picking_type, picking_slots',
    make_testcases(),
)
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['1']})
async def test_validate_delivery_time(
        mockserver,
        taxi_eats_customer_slots,
        experiments3,
        mock_calculate_load,
        now,
        time_zone,
        delivery_time,
        delivery_day,
        estimated_delivery_duration,
        estimated_delivery_timepoint_shift,
        asap_delivery_time_max_epsilon,
        approximate_picking_time,
        expected_delivery_availability,
        expected_asap,
        brand_id,
        shop_picking_type,
        picking_slots,
):
    place_id = 7
    experiments3.add_experiment3_from_marker(
        utils.settings_config(
            estimated_delivery_timepoint_shift,
            asap_disable_threshold=7200,
            approximate_picking_time=approximate_picking_time,
            asap_delivery_time_max_epsilon=asap_delivery_time_max_epsilon,
        ),
        None,
    )
    now = utils.localize(now, time_zone)
    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=place_id,
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
        shop_picking_type=shop_picking_type,
    )
    if picking_slots is not None:
        picking_slots = [
            utils.make_picking_slot(*picking_slot, timezone=time_zone)
            for picking_slot in picking_slots
        ]

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    def _mock_get_picking_slots(_):
        if picking_slots is not None:
            return mockserver.make_response(
                json={'picking_slots': picking_slots},
            )
        return mockserver.make_response(status=500)

    await taxi_eats_customer_slots.invalidate_caches()

    request_body = {
        'places': [
            {
                'place_id': place_id,
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
        '/api/v1/places/validate-delivery-time', json=request_body,
    )
    assert response.status == 200
    response_body = response.json()
    assert response_body == {
        'places': [
            {
                'place_id': str(place_id),
                'is_asap': expected_asap,
                'delivery_availability': expected_delivery_availability,
            },
        ],
    }
