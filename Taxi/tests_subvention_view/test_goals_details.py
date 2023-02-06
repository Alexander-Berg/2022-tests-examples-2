# pylint: disable=C0302
import copy
import json

import pytest

from . import common


VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle1'},
        },
    ],
}

DEFAULT_HEADERS = {
    'X-Driver-Session': 'qwerty',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-YaTaxi-Driver-Profile-Id': 'driver1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '8.60 (562)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

DEFAULT_PARAMS = {'lon': '37.6', 'lat': '55.73', 'tz': 'Europe/Moscow'}

CURRENT_DAY = '2021-03-23'
MOCK_NOW = f'{CURRENT_DAY}T14:15:16+0300'


@pytest.mark.parametrize(
    'time_zone, expected_response',
    [
        ('Europe/Moscow', 'bsx_goals_details_response.json'),
        ('Asia/Yekaterinburg', 'bsx_goals_details_response_ekb_tz.json'),
    ],
)
@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'request_rule_id,rules_json,expected_code',
    [
        (
            'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'bsx_rules_select_test_bsx_goal.json',
            200,
        ),
        ('something_invalid', 'bsx_rules_select_test_bsx_goal.json', 400),
        (
            (
                'bsx:['
                '2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8,'
                '2f1377bb-4c8d-4cda-aa9a-2939e5e79ef9'
                ']'
            ),
            'bsx_rules_select_test_bsx_goal_different_drafts.json',
            409,
        ),
    ],
)
async def test_bsx_goal(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        time_zone,
        expected_response,
        request_rule_id,
        rules_json,
        expected_code,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bsx.set_rules(load_json(rules_json))
    bsx.set_by_driver({'global_counter1': 10})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params={'lon': '37.6', 'lat': '55.73', 'tz': time_zone},
        json={
            'goal_counter': 'global_counter1',
            'rule_id': request_rule_id,
            'date': '2021-04-01',
        },
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == load_json(expected_response)

        assert bsx.by_driver.times_called == 1
        by_driver_request = bsx.by_driver.next_call()['request_data'].json
        assert by_driver_request == {
            'global_counters': ['global_counter1'],
            'time_range': {
                'end': '2021-04-01T21:00:00+00:00',
                'start': '2021-03-31T21:00:00+00:00',
            },
            'unique_driver_id': 'udid',
            'timezone': 'Europe/Moscow',
        }

        assert bsx.by_ids.times_called == 1
        by_ids_request = bsx.by_ids.next_call()['request_data'].json
        assert by_ids_request == {
            'rules': ['2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8'],
        }

        assert bss.rules_select.times_called == 0


@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.parametrize(
    'bss_rs_response, expected_response',
    [
        (
            'bss_rules_select_response_multi_step.json',
            'bss_goals_details_response_multi_step.json',
        ),
        (
            'bss_rules_select_response_single_step.json',
            'bss_goals_details_response_single_step.json',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_bss_goal(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        bss_rs_response,
        expected_response,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bss.add_rules(load_json(bss_rs_response))
    bss.add_by_driver_subventions(load_json('bss_by_driver_response.json'))

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'rule_id': 'group_id_22222222-4c8d-4cda-aa9a-2939e5e79ef8',
            'date': '2021-04-01',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)

    assert bsx.by_draft.times_called == 0
    assert bss.rules_select.times_called == 1
    assert json.loads(bss.rules_select_call_params[0]) == {
        'drivers': [{'unique_driver_id': 'udid'}],
        'is_personal': True,
        'limit': 1000,
        'time_range': {
            'end': '2021-04-01T21:00:00+00:00',
            'start': '2021-03-31T21:00:00+00:00',
        },
    }
    assert bss.by_driver.times_called == 1
    by_driver_request = json.loads(bss.by_driver_call_params[0])
    assert by_driver_request == {
        'is_personal': True,
        'subvention_rule_ids': [
            'group_id/22222222-4c8d-4cda-aa9a-2939e5e79ef8',
        ],
        'time': '2021-04-01T06:35:00+00:00',
        'unique_driver_id': 'udid',
    }


@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
            'parent_name': 'br_root',
            'tanker_key': 'name.br_russia',
            'region_id': '225',
        },
        {
            'name': 'br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'region_id': '3',
        },
        {
            'name': 'br_moskovskaja_obl',
            'name_en': 'Moscow Region',
            'name_ru': 'Московская область',
            'node_type': 'node',
            'parent_name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_moskovskaja_obl',
            'region_id': '1',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_moskovskaja_obl',
            'tanker_key': 'name.br_moscow',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'tanker_key': 'name.br_moscow_adm',
            'region_id': '213',
        },
        {
            'name': 'br_moscow_middle_region',
            'name_en': 'Moscow (Middle Region)',
            'name_ru': 'Москва (среднее)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tanker_key': 'name.br_moscow_middle_region',
        },
        {
            'name': 'br_domodedovo',
            'name_en': 'Domodedovo',
            'name_ru': 'Домодедово',
            'node_type': 'node',
            'parent_name': 'br_moscow_middle_region',
            'tariff_zones': ['domodedovo'],
            'tanker_key': 'name.br_domodedovo',
            'region_id': '10725',
        },
    ],
)
async def test_bug_duplicated_tariff_classes_efficiencydev_12395(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bsx.set_rules(load_json('bsx_rs_test_bug_duplicated_tariff_classes.json'))
    bsx.set_by_driver({'global_counter1': 10})

    rule_ids = (
        'bsx:['
        '2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8,'
        'aaaabbcc-4c8d-4cda-aa9a-2939e5e79ef8'
        ']'
    )
    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': rule_ids,
            'date': '2021-04-01',
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'goals_details_response_duplicated_tariffs.json',
    )


@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_bug_wrong_branding_check_efficiencydev_12466(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bsx.set_rules(load_json('bsx_rs_test_bug_wrong_branding.json'))
    bsx.set_by_driver({'global_counter1': 1})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-01',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'goals_details_response_bug_branding_check.json',
    )


@pytest.mark.now('2021-04-19T06:35:00+0000')
@pytest.mark.parametrize(
    'window_size, expected_response, date',
    [
        (2, 'expected_response_2days_window_19_april.json', '2021-04-19'),
        (2, 'expected_response_2days_window_20_april.json', '2021-04-20'),
        (1, 'expected_response_1day_window_19_april.json', '2021-04-19'),
        (5, 'expected_response_5days_window_23_april.json', '2021-04-23'),
        (14, 'expected_response_14days_window_23_april.json', '2021-04-23'),
        (14, 'expected_response_14days_window_1_april.json', '2021-04-01'),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_bug_schedule_for_rule_window_efficiencydev_12402(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        window_size,
        expected_response,
        date,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    rule = load_json('bsx_rule_test_bug_schedule_for_rule_window.json')
    rule['window'] = window_size
    bsx.set_rules([rule])
    bsx.set_by_driver({'global_counter1': 10})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': date,
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2021-04-05T13:35:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(SUBVENTION_VIEW_USE_INLINE_BRANDING_TANKER_KEYS=True)
async def test_today_schedule_efficiencydev_12512(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bsx.set_rules(load_json('bsx_rs_test_today_schedule.json'))
    bsx.set_by_driver({'global_counter1': 1})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'goals_details_response_bug_today_schedule.json',
    )


@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'tariffs_in_candidates_response,tariffs_in_bss_rs_response,'
    'expected_response',
    [
        (
            ['comfort', 'econom', 'uberblack'],
            ['business'],
            'bss_goals_details_response.json',
        ),
    ],
)
async def test_tariff_classes_mapping_12498(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        tariffs_in_candidates_response,
        tariffs_in_bss_rs_response,
        expected_response,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    candidates_response = load_json(
        'candidates_profiles_response_mappable_tariffs.json',
    )
    candidates_response['drivers'][0][
        'classes'
    ] = tariffs_in_candidates_response
    candidates.load_profiles(candidates_response)

    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    bss_rs_response = load_json('bss_rules_select_response.json')
    bss_rs_response[0]['tariff_classes'] = tariffs_in_bss_rs_response
    bss.add_rules(bss_rs_response)

    bss.add_by_driver_subventions(load_json('bss_by_driver_response.json'))

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'rule_id': 'group_id_22222222-4c8d-4cda-aa9a-2939e5e79ef8',
            'date': '2021-04-01',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2021-04-01T06:35:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_got_404(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_tags_mocks,
        dmi,
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_position(request):
        return mockserver.make_response(
            json={'message': 'Not found'}, status=404,
        )

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-01',
        },
    )
    assert response.status_code == 404


@pytest.mark.now('2021-04-05T13:35:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(SUBVENTION_VIEW_USE_INLINE_BRANDING_TANKER_KEYS=True)
@pytest.mark.parametrize(
    'location_policy, expected_response',
    [
        ('geo_nodes', 'expected_response_a11n_cache_node_name.json'),
        ('tariff_zones', 'expected_response_a11n_cache_tariff_zones.json'),
        (
            'tariff_zones_sorted_by_area',
            'expected_response_a11n_cache_tariff_zones_sorted_by_area.json',
        ),
    ],
)
async def test_a11n_localization(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        location_policy,
        expected_response,
        taxi_config,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])
    taxi_config.set(
        SUBVENTION_VIEW_GOALS_DETAILS_SHOW_LOCATION_POLICY=location_policy,
    )

    bsx.set_rules(load_json('bsx_rs_test_today_schedule.json'))
    bsx.set_by_driver({'global_counter1': 1})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2021-04-05T13:35:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(SUBVENTION_VIEW_USE_INLINE_BRANDING_TANKER_KEYS=True)
@pytest.mark.parametrize(
    'show_last_minute, expected_response',
    [
        (True, 'goals_details_response_bug_today_schedule.json'),
        (False, 'goals_details_response_last_minute_skipped.json'),
    ],
)
async def test_show_last_minute_in_schedule(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
        bsx,
        show_last_minute,
        taxi_config,
        expected_response,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])
    taxi_config.set(
        SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=show_last_minute,
    )

    bsx.set_rules(load_json('bsx_rs_test_today_schedule.json'))
    bsx.set_by_driver({'global_counter1': 1})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_FETCH_GOALS_EXTRA_TARIFFS={'econom': ['courier']},
    SUBVENTION_VIEW_ADD_TARIFF_ZONE_CHECKING=True,
    SUBVENTION_VIEW_GOALS_DETAILS_SHOW_LOCATION_POLICY='tariff_zones',
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_kazakhstan',
            'name_en': 'Kazakhstan',
            'name_ru': 'Казахстан',
            'node_type': 'country',
            'parent_name': 'br_root',
            'tanker_key': 'name.br_kazakhstan',
            'region_id': '159',
        },
        {
            'name': 'br_almaty',
            'name_en': 'Almaty',
            'name_ru': 'Алматы',
            'node_type': 'agglomeration',
            'parent_name': 'br_kazakhstan',
            'tariff_zones': ['almaty', 'almaty_hub'],
            'tanker_key': 'name.br_almaty',
            'region_id': '162',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_moskovskaja_obl',
            'tanker_key': 'name.br_moscow',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'tanker_key': 'name.br_moscow_adm',
            'region_id': '213',
        },
        {
            'name': 'br_moskovskaja_obl',
            'name_en': 'Moscow Region',
            'name_ru': 'Московская область',
            'node_type': 'node',
            'parent_name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_moskovskaja_obl',
        },
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
            'parent_name': 'br_root',
            'tanker_key': 'name.br_russia',
            'region_id': '225',
        },
        {
            'name': 'br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'region_id': '3',
        },
    ],
)
@pytest.mark.parametrize(
    'geonode,udid,expected_response',
    [
        pytest.param(  # show only tariff (tariff_zone checking - on)
            {
                'geonode': 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm',  # noqa: E501
            },
            {},
            'goals_response_requirements_tariff_mismatch.json',
            id='tariff_mismatch',
        ),
        pytest.param(  # show tariff and tariff_zone (tariff_zone checking - on)  # noqa: E501
            {'geonode': 'br_root/br_kazakhstan/br_almaty'},
            {'unique_driver_id': 'udid'},
            'goals_response_requirements_tariff_and_tariff_zone_mismatch.json',
            id='tariff_and_tariff_zone_mismatch',
        ),
        pytest.param(  # show tariff and tariff_zone (tariff_zone checking - on)  # noqa: E501
            {'geonode': 'br_root/br_kazakhstan/br_almaty/almaty_hub'},
            {'unique_driver_id': 'udid'},
            'goals_response_requirements_tariff_and_tariff_zone_mismatch_rule_bounded_to_tariff_zone.json',  # noqa: E501
            id='tariff_and_tariff_zone_mismatch_rule_bounded_to_tariff_zone',
        ),
    ],
)
async def test_bsx_goal_tariff_zone_requirements(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        bsx,
        geonode,
        udid,
        expected_response,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx_response = 'bsx_rules_select_response_test_goal_tariff_zone_requirements_template.json'  # noqa: E501
    rules = load_json(bsx_response)
    assert len(rules) == 1
    rule_requirements = {'tariff_class': 'courier'}
    rules[0].update(rule_requirements)
    rules[0].update(geonode)
    rules[0].update(udid)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 5})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2021-01-15T00:00:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_ADD_TARIFF_ZONE_CHECKING=True,
    SUBVENTION_VIEW_GOALS_DETAILS_SHOW_LOCATION_POLICY='tariff_zones',
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_kazakhstan',
            'name_en': 'Kazakhstan',
            'name_ru': 'Казахстан',
            'node_type': 'country',
            'parent_name': 'br_root',
            'tanker_key': 'name.br_kazakhstan',
            'region_id': '159',
        },
        {
            'name': 'br_almaty',
            'name_en': 'Almaty',
            'name_ru': 'Алматы',
            'node_type': 'agglomeration',
            'parent_name': 'br_kazakhstan',
            'tariff_zones': ['almaty', 'almaty_hub'],
            'tanker_key': 'name.br_almaty',
            'region_id': '62',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
            'parent_name': 'br_root',
            'tanker_key': 'name.br_russia',
            'region_id': '225',
        },
        {
            'name': 'br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'region_id': '3',
        },
        {
            'name': 'br_moskovskaja_obl',
            'name_en': 'Moscow Region',
            'name_ru': 'Московская область',
            'node_type': 'node',
            'parent_name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_moskovskaja_obl',
            'region_id': '1',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_moskovskaja_obl',
            'tanker_key': 'name.br_moscow',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'tanker_key': 'name.br_moscow_adm',
            'region_id': '213',
        },
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='subvention_view_use_cargo_tanker_keys',
    consumers=[
        'subvention-view/v1/summary',
        'subvention-view/v1/goals',
        'subvention-view/v1/goals_details',
    ],
    clauses=[],
    default_value={'use_cargo_keys': True},
)
async def test_translates_cargo_keys(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx_response = 'bsx_rules_select_response_cargo_keys.json'
    rules = load_json(bsx_response)
    assert len(rules) == 1
    geonode = {'geonode': 'br_root/br_kazakhstan/br_almaty'}
    rules[0].update(geonode)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 5})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-01-15',
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response['header']['bubble_title'] == '5 из 20 доставок'
    assert (
        response['items'][0]['items'][0]['items'][0]['subtitle']
        == '10 доставок'
    )
    assert (
        response['items'][0]['items'][0]['items'][1]['subtitle']
        == '20 доставок'
    )
    assert (
        response['items'][2]['items'][1]['text']
        == 'Бонус за доставки не суммируется. Отразится в балансе и заработке 25 февраля.'  # noqa: E501
    )
    assert response['items'][4]['items'][3]['title'] == 'Место доставок'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'show_location_policy,expected_response',
    [
        pytest.param(
            'geo_nodes', 'Москва', id='location_dublication_policy_geonodes',
        ),
        pytest.param(
            'tariff_zones',
            'Борисово, Внуково, Москва',
            id='location_dublication_policy_tariff_zones',
        ),
        pytest.param(
            'tariff_zones_sorted_by_area',
            'Москва, Борисово, Внуково',
            id='location_dublication_policy_tariff_zones_sorted_by_area',
        ),
    ],
)
async def test_location_dublication_15041(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        bsx,
        taxi_config,
        show_location_policy,
        expected_response,
):
    taxi_config.set(
        SUBVENTION_VIEW_GOALS_DETAILS_SHOW_LOCATION_POLICY=show_location_policy,  # noqa: E501
    )
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx_response = 'bsx_rules_select_response_goal_without_geonode_template.json'  # noqa: E501
    rule = load_json(bsx_response)
    list_with_geonodes = [
        {
            'geonode': 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow',  # noqa: E501
        },
        {
            'geonode': 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow',  # noqa: E501
        },
    ]
    rules = []
    for i, geonode in enumerate(list_with_geonodes):
        rules.append(copy.deepcopy(rule))
        rules[i].update(geonode)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 5})
    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )
    assert response.status_code == 200
    assert (
        response.json()['items'][3]['items'][3]['subtitle']
        == expected_response
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {  # geonode had only inactive tariff zone
            'name': 'br_bad_geonode',
            'name_en': 'Geonode with inactive tariff zone',
            'name_ru': 'Геонода с неактивной тарифной зоной',
            'node_type': 'agglomeration',
            'parent_name': 'br_root',
            'tariff_zones': ['inactive_tariff_zone'],
            'tanker_key': 'name.br_bad_geonode',
        },
        {  # geonode has active and inactive tariff zones
            'name': 'br_good_geonode',
            'name_en': 'Geonode with inactive tariff zone',
            'name_ru': 'Геонода с неактивной тарифной зоной',
            'node_type': 'agglomeration',
            'parent_name': 'br_root',
            'tariff_zones': ['inactive_tariff_zone', 'moscow'],
            'tanker_key': 'name.br_good_geonode',
        },
    ],
)
@pytest.mark.parametrize(
    'show_location_policy, list_with_geonodes, expected_status_code, expected_response',  # noqa: E501
    [
        pytest.param(
            'geo_nodes',
            [{'geonode': 'br_root/br_bad_geonode/inactive_tariff_zone'}],
            500,
            'sd',
            id='one_inactive_tariff_zone',
        ),
        pytest.param(
            'geo_nodes',
            [{'geonode': 'br_root/br_bad_geonode'}],
            500,
            '',
            id='one_geonode_with_inactive_tariff_zone',
        ),
        pytest.param(
            'geo_nodes',
            [
                {'geonode': 'br_root/br_bad_geonode/inactive_tariff_zone'},
                {'geonode': 'br_root/br_good_geonode/moscow'},
            ],
            200,
            'Москва',
            id='one_inactive_and_one_active_tariff_zones_location_policy_geo_nodes',  # noqa: E501
        ),
        pytest.param(
            'tariff_zones',
            [
                {'geonode': 'br_root/br_bad_geonode/inactive_tariff_zone'},
                {'geonode': 'br_root/br_good_geonode/moscow'},
            ],
            200,
            'Москва',
            id='one_inactive_and_one_active_tariff_zones_location_policy_tariff_zones',  # noqa: E501
        ),
        pytest.param(
            'tariff_zones_sorted_by_area',
            [
                {'geonode': 'br_root/br_bad_geonode/inactive_tariff_zone'},
                {'geonode': 'br_root/br_good_geonode/moscow'},
            ],
            200,
            'Москва',
            id='one_inactive_and_one_active_tariff_zones_location_policy_tariff_zones_sorted_by_area',  # noqa: E501
        ),
        pytest.param(
            'geo_nodes',
            [
                {'geonode': 'br_root/br_bad_geonode'},
                {'geonode': 'br_root/br_good_geonode'},
            ],
            200,
            'Геонода с активной тарифной зоной',
            id='one_inactive_and_one_active_geonodes_location_policy_geo_nodes',  # noqa: E501
        ),
        pytest.param(
            'tariff_zones',
            [
                {'geonode': 'br_root/br_bad_geonode'},
                {'geonode': 'br_root/br_good_geonode'},
            ],
            200,
            'Москва',
            id='one_inactive_and_one_active_geonodes_location_policy_tariff_zones',  # noqa: E501
        ),
        pytest.param(
            'tariff_zones_sorted_by_area',
            [
                {'geonode': 'br_root/br_bad_geonode'},
                {'geonode': 'br_root/br_good_geonode'},
            ],
            200,
            'Москва',
            id='one_inactive_and_one_active_geonodes_location_policy_tariff_zones_sorted_by_area',  # noqa: E501
        ),
    ],
)
async def test_bsx_goal_with_inactive_tariff_zone(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        bsx,
        taxi_config,
        show_location_policy,
        list_with_geonodes,
        expected_status_code,
        expected_response,
):

    taxi_config.set(
        SUBVENTION_VIEW_GOALS_DETAILS_SHOW_LOCATION_POLICY=show_location_policy,  # noqa: E501
    )
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx_response = 'bsx_rules_select_response_goal_without_geonode_template.json'  # noqa: E501
    rule = load_json(bsx_response)
    rules = []
    for i, geonode in enumerate(list_with_geonodes):
        rules.append(copy.deepcopy(rule))
        rules[i].update(geonode)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 5})
    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
        json={
            'goal_counter': 'global_counter1',
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': '2021-04-05',
        },
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert (
            response.json()['items'][3]['items'][3]['subtitle']
            == expected_response
        )


def _extract_schedule_from_response(response, title='Расписание'):
    multi_sections = [
        itm for itm in response['items'] if itm['type'] == 'multi_section'
    ]
    schedules = [
        msec['items'][0]
        for msec in multi_sections
        if msec['items'][0]['title'] == title
    ]
    assert len(schedules) == 1, 'Found {} schedules in response'.format(
        len(schedules),
    )
    pads = schedules[0]['pads']
    content_items = schedules[0]['pads_content_items']

    res = {}
    for pad, content in zip(pads, content_items):
        key = '{}:{}'.format(pad['title'], pad['subtitle'])
        value = [itm['title'] for itm in content['rows'][0]['items']]
        res[key] = value
    return res


@common.TALLINN_GEONODES
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'mock_now,date,expected_schedule',
    [
        # Estonia switches clocks on October, 31
        (
            '2021-10-30T12:00:00+0000',
            '2021-10-30',
            {'30:Сб': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2021-10-31T16:00:00+0000',
            '2021-10-30',
            {'30:Сб': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2021-10-31T16:25:00+0000',
            '2021-10-30',
            {'30:Сб': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2021-10-31T16:00:00+0000',
            '2021-10-31',
            {'31:Вс': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2021-10-31T00:00:00+0000',
            '2021-11-01',
            {'1:Пн': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2021-10-31T16:25:00+0000',
            '2021-11-01',
            {'1:Пн': ['02:00-10:00', '12:00-14:30']},
        ),
        #
        # ...then switches back on March, 27
        (
            '2022-03-26T14:00:00+0000',
            '2022-03-27',
            {'27:Вс': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2022-03-26T14:00:00+0000',
            '2022-03-28',
            {'28:Пн': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2022-03-27T08:00:00+0000',
            '2022-03-27',
            {'27:Вс': ['02:00-10:00', '12:00-14:30']},
        ),
        (
            '2022-03-27T08:00:00+0000',
            '2022-03-26',
            {'26:Сб': ['02:00-10:00', '12:00-14:30']},
        ),
    ],
)
async def test_switch_to_winter_time(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        bsx,
        mocked_time,
        mock_now,
        date,
        expected_schedule,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    driver_trackstory.set_position({'lat': 59.437425, 'lon': 24.745137})
    mocked_time.set(common.parse_time(mock_now))

    bsx.set_rules(load_json('bsx_goal_tallinn_switching_clocks.json'))
    bsx.set_by_driver({'607700:A': 12})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '24.7451376',
            'lat': '59.437425',
            'tz': 'Europe/Tallinn',
        },
        json={
            'goal_counter': '607700:A',
            'rule_id': 'bsx:[05112dc9-a69f-4e8b-bd78-b26ad806ef34]',
            'date': date,
        },
    )
    assert response.status_code == 200

    assert (
        _extract_schedule_from_response(response.json()) == expected_schedule
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.experiments3(
    filename='experiment_subvention_view_commission_subventions.json',
)
@pytest.mark.parametrize(
    'tag, counter, bsx_rules, expected',
    [
        (
            'comission_A',
            'global_counter1',
            'bsx_rules_select_response_test_goals_comissions_A.json',
            'goals_details_comissions_response_A.json',
        ),
        (
            'comission_B',
            'global_counter1',
            'bsx_rules_select_response_test_goals_comissions_B.json',
            'goals_details_comissions_response_B.json',
        ),
    ],
)
async def test_goals_details_comissions(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_tags_mocks,
        driver_trackstory,
        bsx,
        tag,
        counter,
        bsx_rules,
        expected,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', [tag])
    bsx.set_rules(load_json(bsx_rules))
    bsx.set_by_driver({counter: 20})

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention-view/v1/view/goals/details',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '24.7451376',
            'lat': '59.437425',
            'tz': 'Europe/Moscow',
        },
        json={
            'goal_counter': counter,
            'rule_id': 'bsx:[2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8]',
            'date': CURRENT_DAY,
        },
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json() == load_json(expected)
