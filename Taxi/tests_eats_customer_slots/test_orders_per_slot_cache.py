import datetime

import pytest

from tests_eats_customer_slots import utils


@pytest.mark.now('2021-11-20T13:00:00+00:00')
@utils.slots_loading_feature_enabled()
@utils.daily_slots_config()
@utils.settings_config()
async def test_orders_per_slot_cache(
        taxi_eats_customer_slots,
        testpoint,
        mockserver,
        now,
        create_place_intervals,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    place_id = 123456
    place_id2 = 654321
    logistic_group_id = 1

    @testpoint('place-load-info-cache-testpoint')
    def place_load_info_tp(_):
        response = []
        response.append(utils.make_place_load(now, place_id))
        response.append(utils.make_place_load(now, place_id2))
        return response

    create_place_intervals(place_id2, logistic_group_id)
    create_place_intervals(place_id, logistic_group_id)

    @mockserver.json_handler('/eats-picker-orders/api/v1/orders/preorders')
    def mock_get_preorders(request):
        return mockserver.make_response(
            status=200,
            json={
                'preorders': [
                    {
                        'eats_id': '211120-012345',
                        'place_id': place_id,
                        'estimated_delivery_time': utils.to_string(
                            now + datetime.timedelta(hours=2),
                        ),
                        'is_asap': False,
                    },
                    {
                        'eats_id': '211120-012346',
                        'place_id': place_id,
                        'estimated_delivery_time': utils.to_string(
                            now + datetime.timedelta(hours=3),
                        ),
                        'is_asap': False,
                    },
                ],
            },
        )

    @testpoint('before-setting-cache-values-testpoint')
    def before_setting_cache_data(cache_data):
        assert len(cache_data) == 2
        sorted(cache_data, key=lambda record: record['place_id'])
        assert cache_data[0]['place_id'] == place_id2
        assert cache_data[1]['place_id'] == place_id
        assert (
            cache_data[0]['slots_preorders']
            == cache_data[1]['slots_preorders']
        )

    await taxi_eats_customer_slots.invalidate_caches(
        clean_update=True,
        cache_names=['place-orders-per-slot-cache', 'places-load-info-cache'],
    )

    # One call before test has been run and one actual call
    assert mock_get_preorders.times_called == 2
    assert place_load_info_tp.times_called == 2
    assert before_setting_cache_data.times_called == 2
