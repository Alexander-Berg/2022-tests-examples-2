import datetime
import json

import pytest

from tests_eats_customer_slots import utils


PLACES_COUNT = 101


def make_param(
        expected_delivery_timepoint,
        expected_asap_availability,
        time_zone='Europe/Moscow',
        delivery_time=None,
        delivery_day=None,
        estimated_delivery_duration=0,
        estimated_delivery_timepoint_shift=0,
        asap_delivery_time_max_epsilon=0,
        approximate_picking_time=0,
        cache_enabled=False,
        delivery_point=None,
        validate_expiration=False,
        slot_max_end_threshold=None,
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
        cache_enabled,
        delivery_point,
        validate_expiration,
        slot_max_end_threshold,
    ]


@pytest.mark.now('2022-06-25T12:00:00+03:00')
@utils.slots_enabled()
@utils.text_formats_config()
@utils.make_catalog_storage_cache(1)
@pytest.mark.parametrize(
    'time_zone, delivery_time, delivery_day, '
    'estimated_delivery_duration, estimated_delivery_timepoint_shift, '
    'asap_delivery_time_max_epsilon, approximate_picking_time, '
    'expected_delivery_timepoint, expected_asap_availability, '
    'cache_enabled, delivery_point, validate_expiration, '
    'slot_max_end_threshold',
    [
        make_param(
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',
            ),
            expected_asap_availability=False,
        ),
        make_param(
            estimated_delivery_timepoint_shift=1800,  # doesn't matter
            approximate_picking_time=1000,  # doesn't matter
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',  # slots[0]
            ),
            expected_asap_availability=False,
        ),
        make_param(
            delivery_day=0,
            # slots[1].start < delivery_time < slots[1].end
            delivery_time='15:10',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T15:00:00+03:00',  # slots[1]
            ),
            expected_asap_availability=False,
        ),
        make_param(
            time_zone='Etc/UTC',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T11:00:00+00:00',  # slots[0]
            ),
            expected_asap_availability=False,
        ),
        make_param(
            time_zone='Etc/UTC',
            delivery_day=0,
            # slot[1].start < delivery_time < slot[1].end
            delivery_time='12:10',
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T12:00:00+00:00',  # slots[1]
            ),
            expected_asap_availability=False,
        ),
        make_param(
            delivery_day=0,
            delivery_time='16:10',  # delivery_time > slots[1].end
            expected_delivery_timepoint=None,
            expected_asap_availability=False,
        ),
        make_param(
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',
            ),
            expected_asap_availability=False,
            cache_enabled=True,
        ),
        make_param(
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',
            ),
            expected_asap_availability=False,
            cache_enabled=True,
            delivery_point={'lat': 42.42, 'lon': 24.24},
        ),
        make_param(
            delivery_day=0,
            # slots[1].start < delivery_time < slots[1].end
            delivery_time='15:10',
            validate_expiration=True,  # delivery_time > slots[1].expires_at
            expected_delivery_timepoint=None,
            expected_asap_availability=False,
        ),
        make_param(
            slot_max_end_threshold=4 * 3600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',
            ),
            expected_asap_availability=False,
        ),
        make_param(
            slot_max_end_threshold=3 * 3600,
            expected_delivery_timepoint=datetime.datetime.fromisoformat(
                '2022-06-25T14:00:00+03:00',
            ),
            expected_asap_availability=False,
        ),
        make_param(
            slot_max_end_threshold=2 * 3600,
            expected_delivery_timepoint=None,
            expected_asap_availability=False,
        ),
    ],
)
async def test_calculate_delivery_time_shop_delivery(
        taxi_eats_customer_slots,
        redis_store,
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
        approximate_picking_time,
        expected_delivery_timepoint,
        expected_asap_availability,
        cache_enabled,
        delivery_point,
        validate_expiration,
        slot_max_end_threshold,
):
    cache_strategy = 'place' if delivery_point is None else 'geocode'
    experiments3.add_experiment3_from_marker(
        utils.partner_delivery_slots_config3(
            True,
            cache_enabled,
            cache_strategy,
            42,
            validate_expiration,
            slot_max_end_threshold,
        ),
        None,
    )
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

    place_id = 0
    brand_id = 0
    now = utils.localize(now, time_zone)

    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=place_id,
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=[],
        shop_picking_type='shop_picking',
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
        'delivery_point': delivery_point,
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

    redis_key = (
        utils.make_partner_delivery_slots_redis_place_key(place_id)
        if delivery_point is None
        else utils.make_partner_delivery_slots_redis_location_key(
            place_id, delivery_point['lat'], delivery_point['lon'],
        )
    )
    if cache_enabled:
        assert redis_store.get(redis_key) is None

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

    if cache_enabled:
        assert (
            json.loads(redis_store.get(redis_key))
            == utils.make_partner_delivery_slots()
        )
    else:
        assert redis_store.get(redis_key) is None
