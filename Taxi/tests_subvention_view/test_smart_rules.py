import pytest


from . import common


DEFAULT_HEADERS = {
    'X-Driver-Session': 'test_session',
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-YaTaxi-Driver-Profile-Id': 'driver1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle1'},
        },
    ],
}


@pytest.mark.now('2021-03-17T15:15:16.123123+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 7},
    SMART_SUBVENTIONS_SETTINGS={
        'async_queue_thread_count': 64,
        'clamp_activity': True,
        'dont_include_rules_out_of_group': True,
        'ignored_restrictions': ['activity'],
        'match_split_by': ['zone', 'geoarea', 'tariff_class'],
        'merge_included_intervals': True,
        'merge_overlapped_intervals': True,
        'restrictions': ['activity', 'geoarea'],
        'rules_select_limit': 50,
        'select_max_activity_from_rules': False,
        'throw_on_intervals_overlap': False,
        'use_async_queue': False,
        'use_rule_types_in_rules_select': True,
    },
)
async def test_smart_subventions_interval_rounding_bug(
        mockserver,
        mocked_time,
        bsx,
        ssch,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(
        load_json('candidates_profiles_response_merge.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    request_params = {'lat': '55.733863', 'lon': '37.590533'}

    response = await taxi_subvention_view.get(
        '/v1/schedule', params=request_params, headers=DEFAULT_HEADERS,
    )

    assert bsx.rules_select.times_called == 0
    assert ssch.schedule.next_call()['request_data'].json == {
        'activity_points': 90,
        'branding': {'has_lightbox': False, 'has_sticker': True},
        'ignored_restrictions': ['activity'],
        'tags': [],
        'tariff_classes': ['econom', 'mkk_antifraud', 'uberx', 'vezeteconom'],
        'time_range': {
            'from': '2021-03-17T12:15:16+00:00',
            'to': '2021-03-24T12:15:16+00:00',
        },
        'types': ['single_ride'],
        'zones': ['moscow'],
    }

    assert response.status_code == 200
    assert {'items_for_map': [], 'items_for_schedule': []} == response.json()
