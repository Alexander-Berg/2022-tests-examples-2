# pylint: disable=C0302
import copy
import datetime
import json

import pytest
import pytz

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

SELFREG_HEADER = {
    'X-Driver-Session': 'qwerty',
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

IOS_HEADERS = {
    'X-Driver-Session': 'qwerty',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-YaTaxi-Driver-Profile-Id': 'driver1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '1.62 (111)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'ios',
}

# monday
MOCK_NOW = '2020-09-14T14:15:16+0300'
DEFAULT_PARAMS = {'lon': '37.6', 'lat': '55.73', 'tz': 'Europe/Moscow'}

MOCK_POSITION = {'lat': 55.751244, 'lon': 37.618423}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_empty_subventions(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {}


BS_REQUEST_DATE_RANGE = {
    'start': '2020-09-14T11:15:16+00:00',
    'end': '2020-09-14T11:18:16+00:00',
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
@pytest.mark.parametrize(
    'by_driver,expected_response',
    [
        (
            'by_driver_response_test_goal_subventions.json',
            'expected_response_test_goal_subventions.json',
        ),
        (
            'by_driver_response_test_goal_completed_subventions.json',
            'expected_response_test_goal_completed_subventions.json',
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_USE_BSX_RS_WRAPPER=False),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_USE_BSX_RS_WRAPPER=True),
            ],
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_goal_subventions(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        by_driver,
        expected_response,
        candidates,
):
    for rule_status in load_json(by_driver):
        bss.add_by_driver_subvention(rule_status)

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if data['types'] == ['goal'] and data['is_personal']:
            return {
                'subventions': load_json(
                    'bs_response_test_goal_subventions.json',
                ),
            }
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(expected_response)


def _gen_schedule(intervals):
    items = [
        {
            'activity': 0,
            'draft_id': 'e192c900-70db-443e-9f3d-de4a0169f773',
            'rate': rate,
            'rule_id': '095f2104-6ccb-4ea1-9d93-4622b716f723',
            'tariff_class': 'comfort',
            'tariff_zone': 'moscow',
            'time_range': {'from': from_, 'to': to},
        }
        for from_, to, rate in intervals
    ]
    return [{'items': items, 'type': 'single_ride'}]


SINGLE_ONTOP_RULE = {
    'rule_type': 'single_ontop',
    'start': '2020-05-02T21:00:00+00:00',
    'end': '2021-05-30T21:00:00+00:00',
    'rates': [{'week_day': 'mon', 'start': '18:00', 'bonus_amount': '100500'}],
    'id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
    'budget_id': 'abcd1234',
    'draft_id': '1234abcd',
    'schedule_ref': '1234abcd',
    'zone': 'moscow',
    'tariff_class': 'comfort',
    'updated_at': '2020-05-02T21:00:00+00:00',
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@common.enable_single_ontop
@pytest.mark.config(
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
)
async def test_single_ride_subventions_bsx(
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
        ssch,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    ssch.set_schedules(
        _gen_schedule(
            [
                (
                    '2020-05-02T21:00:00+00:00',
                    '2021-05-30T21:00:00+00:00',
                    100500,
                ),
            ],
        ),
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(
        'expected_response_test_single_ride_subventions_bsx.json',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
)
@pytest.mark.parametrize('use_ontop', [True, False])
async def test_single_ride_no_guarantee_but_ontop_subventions_bsx(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        bss,
        driver_trackstory,
        experiments3,
        use_ontop,
):
    common.add_single_ontop_experiment(
        experiments3, match_ontops=True, cover_in_summary=use_ontop,
    )

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_bsx_get(request):
        return {'rules': [SINGLE_ONTOP_RULE]}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    async def _mock_bsx_match(request):
        return {
            'matches': [
                {
                    'rule': SINGLE_ONTOP_RULE,
                    'type': 'single_ontop',
                    'amount': '100500',
                },
            ],
        }

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()

    filename = 'expected_response_test_no_single_ride_but_ontop_bsx.json'
    expected = load_json(filename) if use_ontop else {}

    assert response_data == expected


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_nmfg_subventions(
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
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if data['types'] == ['daily_guarantee']:
            return {
                'subventions': load_json(
                    'bs_response_test_nmfg_subventions.json',
                ),
            }
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(
        'expected_response_test_nmfg_subventions.json',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
@pytest.mark.parametrize(
    'prioritized_rule,deep_link,expected_response',
    [
        (
            'goals',
            'taximeter://screen/subvention_goals?show_no_data_dialog=true',
            'expected_response_test_rules_priority_goal.json',
        ),
        (
            'single_ride',
            'taximeter://screen/subvention_geo?show_no_data_dialog=true',
            'expected_response_test_rules_priority_single_ride.json',
        ),
        (
            'daily_guarantee',
            'taximeter://screen/subvention_goals?show_no_data_dialog=true',
            'expected_response_test_rules_priority_nmfg.json',
        ),
    ],
)
async def test_rules_priority(
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
        prioritized_rule,
        deep_link,
        expected_response,
        experiments3,
        ssch,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == prioritized_rule:
            settings['priority'] = 100500

    common.add_summary_exp3_config(
        experiments3, rules_settings=rules_settings, use_banner=True,
    )

    for rule_status in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(rule_status)

    ssch.set_schedules(
        _gen_schedule(
            [
                (
                    '2020-05-02T21:00:00+00:00',
                    '2021-05-30T21:00:00+00:00',
                    100500,
                ),
            ],
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        rule_types = data['types']
        subventions = []
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if rule_types == ['daily_guarantee']:
            subventions = load_json('bs_response_test_nmfg_subventions.json')
        elif rule_types == ['goal']:
            subventions = load_json('bs_response_test_goal_subventions.json')
        else:
            assert False, f'unexpected rule type {", ".join(rule_types)}'
        return {'subventions': subventions}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(expected_response)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_etag(
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
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if data['types'] == ['daily_guarantee']:
            return {
                'subventions': load_json(
                    'bs_response_test_nmfg_subventions.json',
                ),
            }
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    etag = response.headers['Etag']
    assert (
        etag
        == '"5920e1db74ac171bfa1c5d3f4e42a4be4dfa583e6a90b2e578707f07a9d62368"'
    )

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['If-None-Match'] = f'W/{etag}'
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=headers,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 304


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
async def test_selfreg(
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
):
    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        rule_types = data['types']
        subventions = []
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if rule_types == ['daily_guarantee']:
            subventions = load_json('bs_response_test_nmfg_subventions.json')
        elif rule_types == ['goal']:
            subventions = load_json('bs_response_goal_selfreg.json')
        else:
            assert False, f'unexpected rule type {", ".join(rule_types)}'
        return {'subventions': subventions}

    params = copy.deepcopy(DEFAULT_PARAMS)
    params.update({'selfreg_token': 'selfreg_token'})
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=SELFREG_HEADER,
        params=params,
    )

    assert mock_bs_by_driver.times_called == 0
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_test_selfreg.json')


@pytest.mark.parametrize('coordinate_not_found', (True, False))
@pytest.mark.config(RETURN_404_ON_NEAREST_ZONE_NOT_FOUND=True)
@pytest.mark.config(
    POLLING_DELAY={'__default__': 600, '/v1/view/summary_on_error': 45},
    TAXIMETER_POLLING_SWITCHER={'__default__': 'new'},
    TAXIMETER_POLLING_MANAGER={
        '__default__': {
            'policy_groups': {'__default__': {'full': 600, 'background': 0}},
        },
        '/v1/view/summary_on_error': {
            'policy_groups': {'__default__': {'full': 45, 'background': 0}},
        },
    },
)
@pytest.mark.now(MOCK_NOW)
async def test_polling_headers_on_404_error(
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
        coordinate_not_found,
        geoareas,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    if coordinate_not_found:
        geoareas.add_many(load_json('geoareas.json'))

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_position(request):
        if coordinate_not_found:
            return mockserver.make_response(
                json={'message': 'Not found'}, status=404,
            )
        return {
            'position': {
                'lat': 55.751244,
                'lon': 37.618423,
                'timestamp': 1552003200,
            },
            'type': 'adjusted',
        }

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 404
    assert response.headers['X-Polling-Delay'] == '45'
    assert response.headers[
        'X-Polling-Power-Policy'
    ] == common.make_polling_policy(45)


@pytest.mark.config(
    POLLING_DELAY={'__default__': 600, '/v1/view/summary_on_error': 45},
    TAXIMETER_POLLING_SWITCHER={'__default__': 'new'},
    TAXIMETER_POLLING_MANAGER={
        '__default__': {
            'policy_groups': {'__default__': {'full': 600, 'background': 0}},
        },
        '/v1/view/summary_on_error': {
            'policy_groups': {'__default__': {'full': 45, 'background': 0}},
        },
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.now(MOCK_NOW)
async def test_polling_headers_on_500_error(
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
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        if data['types'] == ['daily_guarantee']:
            return {
                'subventions': load_json('bs_response_test_wrong_rule.json'),
            }
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 500
    assert response.headers['X-Polling-Delay'] == '45'
    assert response.headers[
        'X-Polling-Power-Policy'
    ] == common.make_polling_policy(45)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_no_geo_map_icon_for_single_ride_rule(
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
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        assert data['time_range'] == BS_REQUEST_DATE_RANGE

        if data['types'] == ['daily_guarantee']:
            return {
                'subventions': load_json(
                    'bs_response_test_nmfg_subventions.json',
                ),
            }

        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(
        'expected_response_test_no_geo_map_icon_for_single_ride_rule.json',
    )


@pytest.mark.parametrize(
    'bsx_goals, bsx_by_driver, expected_response',
    [
        (
            'bsx_goal_bonus_more_than_bs.json',
            {'gA': 7},
            'expected_response_test_goal_subventions.json',
        ),
        (
            'bsx_goal_bonus_less_than_bs.json',
            {'gA': 12},
            'expected_response_test_goal_subventions.json',
        ),
        (None, None, 'expected_response_test_goal_subventions.json'),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
async def test_smart_goals(
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
        bsx_goals,
        bsx_by_driver,
        expected_response,
        experiments3,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    if bsx_goals:
        bsx.set_rules(load_json(bsx_goals))
    if bsx_by_driver:
        bsx.set_by_driver(bsx_by_driver)

    for subvention in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(subvention)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        subventions = []
        if data['types'] == ['goal']:
            assert data == {
                'status': 'enabled',
                'time_range': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-14T11:18:16+00:00',
                },
                'drivers': [{'unique_driver_id': 'udid'}],
                'types': ['goal'],
                'is_personal': True,
                'profile_tags': [],
                'limit': 1000,
            }
            subventions = load_json('bs_response_test_goal_subventions.json')
        return {'subventions': subventions}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(expected_response)

    if bsx_goals:
        assert bsx.by_driver.times_called == 1
        by_driver_request = bsx.by_driver.next_call()['request_data'].json
        assert by_driver_request == {
            'global_counters': ['gA'],
            'time_range': {
                'end': '2020-09-14T21:00:00+00:00',
                'start': '2020-09-13T21:00:00+00:00',
            },
            'unique_driver_id': 'udid',
            'timezone': 'Europe/Moscow',
        }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_USE_GOALS_FROM_BEGINNING_OF_DAY=True,
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
)
async def test_smart_goals_get_rule_end_bug(
        taxi_subvention_view,
        driver_authorizer,
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
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_goal_one_day_window_from_tomorrow.json'))
    bsx.set_by_driver({'gA': 0})

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    common.add_summary_exp3_links_config(
        experiments3, deeplink_args_supported=True,
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json(
        'expected_response_smart_goal_rule_end_bug.json',
    )


@pytest.mark.now('2021-05-19T19:30:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
async def test_smart_goals_wrong_tz(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
        driver_tags_mocks,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['rule_tag'])

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    bsx.set_rules(load_json('bsx_goal_bug_wrong_tz.json'))
    bsx.set_by_driver({'gA': 7})

    params = {'lon': '37.6', 'lat': '55.73', 'tz': 'Asia/Yekaterinburg'}
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_wrong_tz.json')


@pytest.mark.config(SUBVENTION_VIEW_PASS_503_ON_429=True)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_got_429(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 503


@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1260,
)
@pytest.mark.now('2021-05-19T19:30:16+0300')
@pytest.mark.parametrize(
    'goal_start_time, expected_code',
    [('2021-05-19T21:00:00+00:00', 200), ('2021-05-19T14:00:00+00:00', 500)],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_smart_goals_no_progress_for_goal(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
        driver_tags_mocks,
        goal_start_time,
        expected_code,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['rule_tag'])

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    bsx_goals = load_json('bsx_goal_bonus_more_than_bs.json')
    bsx_goals[0]['start'] = goal_start_time
    bsx.set_rules(bsx_goals)

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == load_json(
            'expected_response_no_progress_for_goal.json',
        )


@pytest.mark.parametrize(
    'agglomeration, node, bsx_called',
    [
        ('br_moscow', None, True),
        ('br_wtf_is_this', None, False),
        (None, 'moscow', True),
        (None, 'br_moscow_adm', True),
        (None, 'br_moscow', True),
        (None, 'br_wtf_is_this', False),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_smart_goals_exp_with_agglomeration(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
        agglomeration,
        node,
        bsx_called,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3,
        fetch_smart_goals=True,
        use_banner=False,
        summary_exp_data=common.SummaryExperimentData(
            agglomeration=agglomeration, node=node,
        ),
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    if bsx_called:
        assert bsx.rules_select.times_called > 0
    else:
        assert bsx.rules_select.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'use_goals_from_beginning_of_day,expected_range',
    [
        (False, BS_REQUEST_DATE_RANGE),
        (
            True,
            {
                'start': '2020-09-13T21:00:00+00:00',
                'end': '2020-09-14T11:18:16+00:00',
            },
        ),
    ],
)
async def test_range_from_beginning_of_day_for_goals(
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
        experiments3,
        taxi_config,
        use_goals_from_beginning_of_day,
        expected_range,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    taxi_config.set_values(
        {
            'SUBVENTION_VIEW_SUMMARY_USE_GOALS_FROM_BEGINNING_OF_DAY': (
                use_goals_from_beginning_of_day
            ),
        },
    )

    smart_goals_request_checked = False
    old_goals_request_checked = False

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _mock_bsx_rules_select(request):
        nonlocal smart_goals_request_checked
        data = request.json
        if data['rule_types'] == ['goal']:
            assert data['time_range'] == expected_range
            smart_goals_request_checked = True
        return {'rules': []}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_bs_rules_select(request):
        nonlocal old_goals_request_checked
        data = request.json
        if data['types'] == ['goal']:
            assert data['time_range'] == expected_range
            old_goals_request_checked = True
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200

    assert smart_goals_request_checked
    assert old_goals_request_checked


PROMOTED_MODE_RESPONSE1 = {
    'promoted_modes': [
        {
            'title': 'Новый режим работы',
            'subtitle': 'Повышенный бонус',
            'offer_id': 'mock_offer_id',
            'banner_type': 'new_workmode',
        },
        {
            'title': 'Режим, чтобы просто забить',
            'subtitle': 'И не показывать его',
            'offer_id': 'bad_offer_id',
            'banner_type': 'new_workmode',
        },
    ],
}

PROMOTED_MODE_RESPONSE2 = {
    'promoted_modes': [
        {
            'title': 'Новый режим работы',
            'subtitle': 'Повышенный бонус',
            'banner_type': 'super_workmode',
        },
    ],
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
    SUBVENTION_VIEW_SUMMARY_BANNER_UI={
        '__default__': {
            'gradient_colors': {
                'day': {'first': '#000000', 'second': '#111111'},
            },
        },
        'subventions': {
            'gradient_colors': {
                'day': {'first': '#0062C6', 'second': '#80D8F8'},
            },
            'icon_type': 'cash_money',
        },
        'new_workmode': {
            'gradient_colors': {
                'day': {'first': '#00DDDD', 'second': '#80CCCC'},
            },
        },
        'super_workmode': {
            'gradient_colors': {
                'day': {'first': '#00DDDD', 'second': '#80CCCC'},
                'night': {'first': '#00DDDD', 'second': '#80CCCC'},
            },
        },
    },
)
@pytest.mark.parametrize(
    'enable_workmode_banners,priority,promoted_mode_response,expected_banner',
    [
        (
            # enable_workmode_banners
            True,
            # priority
            'subventions',
            # promoted_mode_response
            PROMOTED_MODE_RESPONSE1,
            # expected_banner
            'expected_banner_of_subvention.json',
        ),
        (
            # enable_workmode_banners
            True,
            # priority
            'workmodes',
            # promoted_mode_response
            PROMOTED_MODE_RESPONSE1,
            # expected_banner
            'expected_banner_of_workmode1.json',
        ),
        (
            # enable_workmode_banners
            False,
            # priority
            'workmodes',
            # promoted_mode_response
            PROMOTED_MODE_RESPONSE1,
            # expected_banner
            'expected_banner_of_subvention.json',
        ),
        (
            # enable_workmode_banners
            True,
            # priority
            'workmodes',
            # promoted_mode_response
            PROMOTED_MODE_RESPONSE2,
            # expected_banner
            'expected_banner_of_workmode2.json',
        ),
        (
            # enable_workmode_banners
            True,
            # priority
            'workmodes',
            # promoted_mode_response
            500,
            # expected_banner
            'expected_banner_of_subvention.json',
        ),
    ],
)
async def test_dms_banner(
        taxi_subvention_view,
        experiments3,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        enable_workmode_banners,
        priority,
        promoted_mode_response,
        expected_banner,
        ssch,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_trackstory.set_position(MOCK_POSITION)

    common.add_summary_exp3_config(
        experiments3,
        rules_settings=common.DEFAULT_RULE_SETTINGS,
        use_banner=True,
    )

    experiments3.add_experiment(
        consumers=['subvention-view/v1/summary'],
        name='subvention_view_summary_workmode_banners',
        match={
            'enabled': enable_workmode_banners,
            'consumers': [{'name': 'subvention-view/v1/summary'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'enabled': True, 'first_priority': priority},
            },
        ],
    )

    for rule_status in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(rule_status)

    ssch.set_schedules(
        _gen_schedule(
            [
                (
                    '2020-05-02T21:00:00+00:00',
                    '2021-05-30T21:00:00+00:00',
                    100500,
                ),
            ],
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = request.json
        rule_types = data['types']
        subventions = []
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if rule_types == ['daily_guarantee']:
            subventions = load_json('bs_response_test_nmfg_subventions.json')
        elif rule_types == ['goal']:
            subventions = load_json('bs_response_test_goal_subventions.json')
        else:
            assert False, f'unexpected rule type {", ".join(rule_types)}'
        return {'subventions': subventions}

    @mockserver.json_handler(
        '/driver-mode-subscription/v1/promoted-modes-list',
    )
    def _mock_promoted_modes_list(request):
        assert common.is_floats_equal(
            float(request.query['lat']), float(MOCK_POSITION['lat']),
        )
        assert common.is_floats_equal(
            float(request.query['lon']), float(MOCK_POSITION['lon']),
        )
        assert request.query['tz'] == 'Europe/Moscow'
        assert request.query['park_id'] == 'dbid1'
        assert request.query['driver_profile_id'] == 'driver1'

        if isinstance(promoted_mode_response, int):
            return mockserver.make_response(status=promoted_mode_response)

        return promoted_mode_response

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()

    banners = [
        itm
        for itm in response_data['ui']['panel_body'][1]['items']
        if 'mode' in itm and itm['mode'] == 'banner'
    ]

    assert len(banners) == 1
    assert banners[0] == load_json(expected_banner)


@pytest.mark.now('2021-07-22T17:00:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
    SUBVENTION_VIEW_GOALS_DETAILS_DAYS_SCHEDULE={
        'days_backward': 7,
        'days_forward': 7,
    },
    SMART_SUBVENTIONS_SETTINGS={'rules_select_limit': 50, 'restrictions': []},
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
)
async def test_empty_window_schedule(
        taxi_subvention_view,
        mockserver,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
        driver_tags_mocks,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['rule_tag'])

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_rules_select(req):
        if req.json['rule_types'] == ['goal'] and req.json[
                'tags_constraint'
        ] == {'tags': ['rule_tag']}:
            return load_json('bsx_rs_response_empty_window_schedule.json')

        return {'rules': []}

    @mockserver.json_handler('/billing-subventions-x/v2/by_driver')
    async def _mock_by_driver(req):
        return load_json('bsx_by_driver_empty_window_schedule.json')

    params = {'lon': '37.5136518', 'lat': '55.7061852', 'tz': 'Europe/Moscow'}
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == {}  # no schedule for today


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_goals_deeplinks(
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
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=True,
    )
    common.add_summary_exp3_links_config(
        experiments3, deeplink_args_supported=True,
    )
    bsx.set_rules(load_json('bsx_goal_deeplinks_test.json'))
    bsx.set_by_driver({'gA': 7})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    banner = response.json()['ui']['panel_body'][1]['items'][0]

    expected_deeplink = (
        'taximeter://screen/subvention_goals_v2/details?'
        'date=2020-09-16&goal_counter=gA&'
        'rule_id=bsx%3A%5B2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8%5D'
    )
    assert common.parse_url_with_args(
        banner['payload']['url'],
    ) == common.parse_url_with_args(expected_deeplink)


@pytest.mark.now('2021-01-15T00:00:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_FETCH_GOALS_EXTRA_TARIFFS={'econom': ['courier']},
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
    rule_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rule_settings:
        if settings['rule_type'] == 'goals':
            settings['priority'] = 100500

    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rule_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx_response = 'bsx_rules_select_response_cargo_keys.json'
    rules = load_json(bsx_response)
    assert len(rules) == 1
    geonode = {
        'geonode': 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm',  # noqa: E501
    }
    rules[0].update(geonode)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 5})

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        if request.json['types'] == ['daily_guarantee']:
            return {
                'subventions': load_json(
                    'bs_response_test_nmfg_subventions.json',
                ),
            }
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response = response.json()
    assert response['ui']['panel_header']['title'] == '5 доставок до +100_₽'
    assert (
        response['ui']['panel_body'][1]['items'][0]['header']['subtitle'][
            'text'
        ]
        == '5 доставок до +100_₽'
    )
    assert (
        response['ui']['panel_body'][1]['items'][1]['footer']['title']['text']
        == 'еще 5 доставок'
    )

    assert (
        response['ui']['panel_body'][1]['items'][2]['footer']['title']['text']
        == '31 заказ'
    ), 'NMFG tile should still use the "order" term'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'request_headers,expected_header_subtitle',
    [(DEFAULT_HEADERS, 'Цели'), (IOS_HEADERS, None)],
)
async def test_ios_header_subtitle(
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
        request_headers,
        expected_header_subtitle,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=True,
    )
    common.add_summary_exp3_links_config(
        experiments3, deeplink_args_supported=True,
    )
    bsx.set_rules(load_json('bsx_goal_deeplinks_test.json'))
    bsx.set_by_driver({'gA': 7})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=request_headers,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    if expected_header_subtitle:
        assert (
            response.json()['ui']['panel_header']['subtitle']
            == expected_header_subtitle
        )
    else:
        assert 'subtitle' not in response.json()['ui']['panel_header']


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@common.smart_subventions_matching
@pytest.mark.experiments3(filename='experiment_single_ride_deeplinks.json')
@pytest.mark.parametrize(
    'schedules,expected',
    [
        (
            'ssch_single_ride_deeplinks_test.json',
            'expected_response_test_single_ride_deeplinks.json',
        ),
        (
            'ssch_single_ride_deeplinks_low_activity_test.json',
            'expected_response_test_single_ride_deeplinks_low_activity.json',
        ),
        (
            'ssch_single_ride_deeplinks_activity_test.json',
            'expected_response_test_single_ride_deeplinks_activity.json',
        ),
    ],
)
async def test_single_ride_deeplinks(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        ssch,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        bsx,
        experiments3,
        schedules,
        expected,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=True,
    )

    ssch.set_schedules(load_json(schedules))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected)


@common.TALLINN_GEONODES
@pytest.mark.parametrize(
    'mock_now',
    [
        # Estonia switches clocks on October 31
        '2021-10-30T17:00:00+0000',
        '2021-10-31T16:25:00+0000',
        '2021-10-31T01:01:00+0000',
        '2021-11-01T12:00:00+0000',
        # ...then switches back on March, 27
        '2022-03-26T14:00:00+0000',
        '2022-03-27T12:00:00+0000',
        '2022-03-28T08:00:00+0000',
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_only',
    SUBVENTION_VIEW_SUMMARY_USE_GOALS_FROM_BEGINNING_OF_DAY=True,
)
async def test_switch_to_winter_time(
        taxi_subvention_view,
        mocked_time,
        experiments3,
        load_json,
        driver_authorizer,
        bsx,
        bss,
        candidates,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        mock_now,
):
    mocked_time.set(common.parse_time(mock_now))
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(
        {
            'drivers': [
                {
                    'classes': ['econom', 'comfort', 'vip'],
                    'dbid': '777',
                    'position': [24.745137, 59.437425],
                    'uuid': '888',
                },
            ],
        },
    )
    driver_trackstory.set_position({'lat': 59.437425, 'lon': 24.745137})

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    bsx.set_rules(load_json('bsx_goal_tallinn_switching_clocks.json'))
    bsx.set_by_driver({'607700:A': 12})

    for subvention in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(subvention)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '24.745137',
            'lat': '59.437425',
            'tz': 'Europe/Tallinn',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    header = response_data['ui']['panel_body'][1]['items'][0]['header']
    # should be goal "for each day" if the schedule is valid
    assert header['title']['text'] == 'Цель на сегодня'
    assert header['subtitle']['text'] == '+30_€'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_summary_banner_and_tile_different_goal(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        bsx,
        experiments3,
        driver_trackstory,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 11)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=True,
    )
    common.add_summary_exp3_links_config(
        experiments3, deeplink_args_supported=True,
    )
    bsx.set_rules(load_json('bsx_goal_different_banner_and_tile_goals.json'))
    bsx.set_by_driver({'gA': 0})
    bsx.set_by_driver({'gB': 0})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    response = response.json()

    assert (
        response['ui']['panel_body'][1]['items'][0]['header']['subtitle'][
            'text'
        ]
        == '2 заказа до +100_₽'
    )
    assert (
        response['ui']['panel_body'][1]['items'][1]['header']['subtitle'][
            'text'
        ]
        == '+10_₽'
    )
    assert (
        response['ui']['panel_body'][1]['items'][1]['footer']['title']['text']
        == 'еще 3 заказа'
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true', 'init': {}}, 'enabled': True},
    is_config=True,
    name='subvention_view_summary_banner',
    consumers=['subvention-view/v1/summary:banner'],
    clauses=[
        {
            'title': '1',
            'value': {
                'goal_banner': {
                    'content': {
                        'title_key': (
                            'summary.patterns.goal.title.with_essential_time'
                        ),
                        'subtitle_key': 'summary.patterns.goal.subtitle',
                        'footer_key': 'summary.banner_footer',
                    },
                },
                'single_ride_banner': {
                    'content': {
                        'title_key': 'summary.patterns.bortsch',
                        'subtitle_key': (
                            'summary.patterns.single_ride.subtitle'
                        ),
                        'footer_key': 'summary.banner_footer',
                    },
                },
                'daily_guarantee_banner': {
                    'content': {
                        'title_key': 'summary.patterns.bortsch',
                        'subtitle_key': (
                            'summary.patterns.daily_guarantee.subtitle'
                        ),
                        'footer_key': 'summary.banner_footer',
                    },
                },
            },
            'enabled': True,
            'predicate': {'type': 'true', 'init': {}},
            'extension_method': 'replace',
        },
    ],
)
@pytest.mark.parametrize(
    'prioritized_rule,deep_link,expected_title,'
    'expected_subtitle,expected_footer',
    [
        (
            'goals',
            'taximeter://screen/subvention_goals?show_no_data_dialog=true',
            'Цель до 29 июня : )',
            '1 заказ до +200_₽ : )',
            'Подробнее',
        ),
        (
            'single_ride',
            'taximeter://screen/subvention_geo?show_no_data_dialog=true',
            'Тарелка борща кадому!',
            'До 100500_₽ за заказ!!!',
            'Подробнее',
        ),
        (
            'daily_guarantee',
            'taximeter://screen/subvention_goals?show_no_data_dialog=true',
            'Тарелка борща кадому!',
            'От 3800_₽!!!',
            'Подробнее',
        ),
    ],
)
async def test_banner_templating(
        taxi_subvention_view,
        driver_authorizer,
        experiments3,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        prioritized_rule,
        deep_link,
        expected_title,
        expected_subtitle,
        expected_footer,
        ssch,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == prioritized_rule:
            settings['priority'] = 100

    common.add_summary_exp3_config(
        experiments3, rules_settings=rules_settings, use_banner=True,
    )

    for rule_status in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(rule_status)

    ssch.set_schedules(
        _gen_schedule(
            [
                (
                    '2020-05-02T21:00:00+00:00',
                    '2021-05-30T21:00:00+00:00',
                    100500,
                ),
            ],
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        rule_types = data['types']
        subventions = []
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if rule_types == ['daily_guarantee']:
            subventions = load_json('bs_response_test_nmfg_subventions.json')
        elif rule_types == ['goal']:
            subventions = load_json('bs_response_test_goal_subventions.json')
        else:
            assert False, f'unexpected rule type {", ".join(rule_types)}'
        return {'subventions': subventions}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()

    banner = response_data['ui']['panel_body'][1]['items'][0]
    assert banner['header']['title']['text'] == expected_title
    assert banner['header']['subtitle']['text'] == expected_subtitle
    assert banner['footer']['title']['text'] == expected_footer


@pytest.mark.parametrize(
    'intervals,expected_period,expected_money,expected_deeplink',
    [
        (
            # intervals
            [
                (
                    '2020-09-14T14:20:00+03:00',
                    '2020-09-14T14:30:00+03:00',
                    350.0,
                ),
                (
                    '2020-09-14T14:20:00+03:00',
                    '2020-09-14T14:30:00+03:00',
                    350.0,
                ),
                (
                    '2020-09-14T14:30:00+03:00',
                    '2020-09-14T14:40:00+03:00',
                    370.0,
                ),
                (
                    '2020-09-14T14:55:00+03:00',
                    '2020-09-14T15:00:00+03:00',
                    400.0,
                ),
            ],
            # expected_period
            '14:20 -- 14:39',
            # expected_money
            '370_₽',
            # expected_deeplink
            'taximeter://screen/subvention_geo?date=2020-09-14'
            '&from_utc=2020-09-14T11:20:00%2B0000'
            '&to_utc=2020-09-14T11:29:00%2B0000',
        ),
        (
            # intervals
            [
                (
                    '2020-09-14T14:00:00+03:00',
                    '2020-09-14T14:30:00+03:00',
                    350.0,
                ),
                (
                    '2020-09-14T14:30:00+03:00',
                    '2020-09-14T14:40:00+03:00',
                    370.0,
                ),
                (
                    '2020-09-14T14:55:00+03:00',
                    '2020-09-14T15:00:00+03:00',
                    400.0,
                ),
            ],
            # expected_period
            '14:00 -- 14:39',
            # expected_money
            '370_₽',
            # expected_deeplink
            'taximeter://screen/subvention_geo?date=2020-09-14'
            '&from_utc=2020-09-14T11:00:00%2B0000'
            '&to_utc=2020-09-14T11:29:00%2B0000',
        ),
        (
            # intervals
            [
                (
                    '2020-09-15T13:00:00+03:00',
                    '2020-09-15T13:30:00+03:00',
                    350.0,
                ),
            ],
            # expected_period
            '13:00 -- 13:29',
            # expected_money
            '350_₽',
            # expected_deeplink
            'taximeter://screen/subvention_geo?date=2020-09-15'
            '&from_utc=2020-09-15T10:00:00%2B0000'
            '&to_utc=2020-09-15T10:29:00%2B0000',
        ),
        (
            # intervals
            [
                (
                    '2020-09-14T14:00:00+03:00',
                    '2020-09-14T14:20:00+03:00',
                    11.0,
                ),
                (
                    '2020-09-14T14:00:00+03:00',
                    '2020-09-14T14:30:00+03:00',
                    22.0,
                ),
                (
                    '2020-09-14T14:10:00+03:00',
                    '2020-09-14T14:50:00+03:00',
                    33.0,
                ),
            ],
            # expected_period
            '14:00 -- 14:49',
            # expected_money
            '33_₽',
            # expected_deeplink
            'taximeter://screen/subvention_geo?date=2020-09-14'
            '&from_utc=2020-09-14T11:00:00%2B0000'
            '&to_utc=2020-09-14T11:19:00%2B0000',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true', 'init': {}}, 'enabled': True},
    is_config=True,
    name='subvention_view_summary_banner',
    consumers=['subvention-view/v1/summary:banner'],
    clauses=[
        {
            'title': '1',
            'value': {
                'single_ride_banner': {
                    'content': {
                        'title_key': (
                            'summary.test.worktime_interval_max_bonus'
                        ),
                        'footer_key': 'summary.test.worktime_interval',
                    },
                    'deeplink_policy': 'next_unfinished_interval',
                },
            },
            'enabled': True,
            'predicate': {'type': 'true', 'init': {}},
            'extension_method': 'replace',
        },
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
)
async def test_banner_interval_placeholder_and_deeplink(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        experiments3,
        intervals,
        expected_period,
        expected_money,
        expected_deeplink,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == 'single_ride':
            settings['priority'] = 100
    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rules_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )

    ssch.set_schedules(_gen_schedule(intervals))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    banner = response.json()['ui']['panel_body'][1]['items'][0]

    assert banner['header']['title']['text'] == expected_money
    assert banner['footer']['title']['text'] == expected_period
    assert common.parse_url_with_args(
        banner['payload']['url'],
    ) == common.parse_url_with_args(expected_deeplink)


@pytest.mark.parametrize(
    'timerange_policy,expected_banner',
    [
        (
            # timerange_policy
            {'lookahead_minutes': 10},
            # expected_banner
            None,
        ),
        (
            # timerange_policy
            {'lookahead_minutes': 540},
            # expected_banner
            ('2_₽', '23:00 -- 23:59'),
        ),
        (
            # timerange_policy
            {'lookahead_minutes': 1440},
            # expected_banner
            ('3_₽', '08:00 -- 08:09'),
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
)
async def test_banner_single_ride_lookahead(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        experiments3,
        timerange_policy,
        expected_banner,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == 'single_ride':
            settings['priority'] = 100
    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rules_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_banner',
        consumers=['subvention-view/v1/summary:banner'],
        clauses=[
            {
                'title': '1',
                'value': {
                    'timerange_policy': timerange_policy,
                    'single_ride_banner': {
                        'content': {
                            'title_key': (
                                'summary.test.worktime_interval_max_bonus'
                            ),
                            'footer_key': 'summary.test.worktime_interval',
                        },
                    },
                },
                'enabled': True,
                'predicate': {'type': 'true', 'init': {}},
                'extension_method': 'replace',
            },
        ],
    )

    ssch.set_schedules(
        _gen_schedule(
            [
                ('2020-09-14T23:00:00+0300', '2020-09-15T00:00:00+0300', 2.0),
                ('2020-09-15T08:00:00+0300', '2020-09-15T08:10:00+0300', 3.0),
            ],
        ),
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    banner_candidate = response.json()['ui']['panel_body'][1]['items'][0]
    banner = (
        banner_candidate if banner_candidate.get('mode') == 'banner' else None
    )

    if expected_banner is None:
        assert banner is None
        return

    content = (
        banner['header']['title']['text'],
        banner['footer']['title']['text'],
    )

    assert content == expected_banner


@pytest.mark.parametrize(
    'rule_type,expected_banner',
    [
        (
            # rule_type
            'single_ride',
            # expected_banner
            ('Получите уже сегодня', 'До 100500_₽ за заказ'),
        ),
        (
            # rule_type
            'goal',
            # expected_banner
            ('Получите уже сегодня', '1 заказ до +200_₽'),
        ),
        (
            # rule_type
            'daily_guarantee',
            # expected_banner
            ('Получите уже сегодня', 'От 3800_₽'),
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.config(
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
)
async def test_banner_priority(
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
        experiments3,
        rule_type,
        expected_banner,
        ssch,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    common.add_summary_exp3_config(
        experiments3,
        rules_settings=common.DEFAULT_RULE_SETTINGS,
        use_banner=True,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_banner',
        consumers=['subvention-view/v1/summary:banner'],
        clauses=[
            {
                'title': '1',
                'value': {'rule_type': rule_type},
                'enabled': True,
                'predicate': {'type': 'true', 'init': {}},
                'extension_method': 'replace',
            },
        ],
    )

    for rule_status in load_json(
            'by_driver_response_test_goal_subventions.json',
    ):
        bss.add_by_driver_subvention(rule_status)

    ssch.set_schedules(
        _gen_schedule(
            [
                (
                    '2020-05-02T21:00:00+00:00',
                    '2021-05-30T21:00:00+00:00',
                    100500,
                ),
            ],
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        rule_types = data['types']
        subventions = []
        assert data['time_range'] == BS_REQUEST_DATE_RANGE
        if rule_types == ['daily_guarantee']:
            subventions = load_json('bs_response_test_nmfg_subventions.json')
        elif rule_types == ['goal']:
            subventions = load_json('bs_response_test_goal_subventions.json')
        else:
            assert False, f'unexpected rule type {", ".join(rule_types)}'
        return {'subventions': subventions}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    banner_candidate = response.json()['ui']['panel_body'][1]['items'][0]
    banner = (
        banner_candidate if banner_candidate.get('mode') == 'banner' else None
    )

    if expected_banner is None:
        assert banner is None
        return

    content = (
        banner['header']['title']['text'],
        banner['header']['subtitle']['text'],
    )

    assert content == expected_banner


@pytest.mark.parametrize(
    'timerange_policy, money_key, expected_banner',
    [
        ({'lookahead_minutes': 10}, 'max_rule_next_step_bonus', None),
        (
            {'lookahead_minutes': 1440},
            'max_rule_next_step_bonus',
            ('2_₽', '16:00 -- 17:59'),
        ),
        (
            {'lookahead_minutes': 1440},
            'max_rule_last_step_bonus',
            ('22_₽', '16:00 -- 17:59'),
        ),
        (
            {'lookahead_minutes': 2880},
            'max_rule_next_step_bonus',
            ('3_₽', '08:00 -- 10:59'),
        ),
        (
            {'lookahead_minutes': 2880},
            'max_rule_last_step_bonus',
            ('33_₽', '08:00 -- 10:59'),
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=4320,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
)
async def test_banner_goal_lookahead(
        taxi_subvention_view,
        driver_authorizer,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        experiments3,
        timerange_policy,
        money_key,
        expected_banner,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_goal_exp_with_interval_for_banner.json'))
    bsx.set_by_driver({'gA': 0, 'gB': 0})

    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == 'goals':
            settings['priority'] = 100
    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rules_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_banner',
        consumers=['subvention-view/v1/summary:banner'],
        clauses=[
            {
                'title': '1',
                'value': {
                    'timerange_policy': timerange_policy,
                    'goal_banner': {
                        'content': {
                            'title_key': 'summary.test.' + money_key,
                            'footer_key': 'summary.test.worktime_interval',
                        },
                    },
                },
                'enabled': True,
                'predicate': {'type': 'true', 'init': {}},
                'extension_method': 'replace',
            },
        ],
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    banner_candidate = response.json()['ui']['panel_body'][1]['items'][0]
    banner = (
        banner_candidate if banner_candidate.get('mode') == 'banner' else None
    )
    if expected_banner is None:
        assert banner is None
        return
    content = (
        banner['header']['title']['text'],
        banner['footer']['title']['text'],
    )
    assert content == expected_banner


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=4320,
)
async def test_optional_panel_header(
        taxi_subvention_view,
        driver_authorizer,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        experiments3,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_goal_exp_with_interval_for_banner.json'))
    bsx.set_by_driver({'gA': 0, 'gB': 0})

    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == 'goals':
            settings['priority'] = 100
    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rules_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_notification',
        consumers=['subvention-view/v1/summary'],
        clauses=[
            {
                'title': '1',
                'value': {'enabled': False},
                'enabled': True,
                'predicate': {'type': 'true', 'init': {}},
                'extension_method': 'replace',
            },
        ],
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200

    ui_value = response.json()['ui']
    assert 'panel_body' in ui_value
    assert 'panel_header' not in ui_value


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
)
@pytest.mark.parametrize(
    'expected_ranges',
    [
        pytest.param(
            {
                'daily_guarantee': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
                'goal': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
                'single-ride': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
            },
            id='Only the default period set',
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'type': 'true', 'init': {}},
                        'enabled': True,
                    },
                    is_config=True,
                    name='subvention_view_summary_subvention_fetch_period',
                    consumers=['subvention-view/v1/summary'],
                    default_value={'default_fetch_period_mins': 1440},
                ),
            ],
        ),
        pytest.param(
            {
                'daily_guarantee': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T12:15:16+00:00',
                },
                'goal': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T12:45:16+00:00',
                },
                'single-ride': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T13:00:16+00:00',
                },
            },
            id='All periods are different',
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'type': 'true', 'init': {}},
                        'enabled': True,
                    },
                    is_config=True,
                    name='subvention_view_summary_subvention_fetch_period',
                    consumers=['subvention-view/v1/summary'],
                    default_value={
                        'default_fetch_period_mins': 1440,
                        'nmfg_fetch_period_mins': 1500,
                        'goal_fetch_period_mins': 1530,
                        'single_ride_fetch_period_mins': 1545,
                    },
                ),
            ],
        ),
        pytest.param(
            {
                'daily_guarantee': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
                'goal': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
                'single-ride': {
                    'start': '2020-09-14T11:15:16+00:00',
                    'end': '2020-09-15T11:15:16+00:00',
                },
            },
            id='No config 3.0, falling back to the regular config',
        ),
    ],
)
async def test_summary_fetch_periods(
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
        experiments3,
        taxi_config,
        expected_ranges,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _mock_bsx_rules_select(request):
        data = request.json
        rule_types = data['rule_types']

        assert len(rule_types) == 1
        assert data['time_range'] == expected_ranges[rule_types[0]]

        return {'rules': []}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_bs_rules_select(request):
        data = request.json
        rule_types = data['types']

        assert len(rule_types) == 1
        assert data['time_range'] == expected_ranges[rule_types[0]]

        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
)
@pytest.mark.experiments3(
    filename='experiment_subvention_view_commission_subventions.json',
)
@pytest.mark.parametrize(
    'tag, counter, rides, bsx_rules, expected',
    [
        (
            'comission_A',
            'global_counter1',
            15,
            'bsx_rules_select_response_test_goals_comissions_A.json',
            'expected_response_comissions_A.json',
        ),
        (
            'comission_A',
            'global_counter1',
            20,
            'bsx_rules_select_response_test_goals_comissions_A.json',
            'expected_response_comissions_A_completed.json',
        ),
        (
            'comission_B',
            'global_counter1',
            15,
            'bsx_rules_select_response_test_goals_comissions_B.json',
            'expected_response_comissions_B.json',
        ),
        (
            'comission_B',
            'global_counter1',
            20,
            'bsx_rules_select_response_test_goals_comissions_B.json',
            'expected_response_comissions_B_completed.json',
        ),
    ],
)
async def test_comission_goals(
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
        rides,
        bsx_rules,
        expected,
        experiments3,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', [tag])
    bsx.set_rules(load_json(bsx_rules))
    bsx.set_by_driver({counter: rides})

    rules_settings = copy.deepcopy(common.DEFAULT_RULE_SETTINGS)
    for settings in rules_settings:
        if settings['rule_type'] == 'goals':
            settings['priority'] = 100
    common.add_summary_exp3_config(
        experiments3,
        rules_settings=rules_settings,
        fetch_smart_goals=True,
        use_banner=True,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_summary_banner',
        consumers=['subvention-view/v1/summary:banner'],
        clauses=[
            {
                'title': '1',
                'value': {
                    'timerange_policy': {'lookahead_minutes': 1440},
                    'goal_banner': {
                        'content': {
                            'title_key': (
                                'summary.test.max_rule_last_step_bonus'
                            ),
                            'footer_key': 'summary.test.worktime_interval',
                        },
                    },
                },
                'enabled': True,
                'predicate': {'type': 'true', 'init': {}},
                'extension_method': 'replace',
            },
        ],
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json() == load_json(expected)
    assert bsx.by_driver.times_called == 1

    by_driver_request = bsx.by_driver.next_call()['request_data'].json
    assert sorted(by_driver_request['global_counters']) == [counter]
    assert by_driver_request['time_range'] == {
        'end': '2020-09-14T21:00:00+00:00',
        'start': '2020-09-13T21:00:00+00:00',
    }
    assert by_driver_request['unique_driver_id'] == 'udid'


@pytest.mark.now('2022-04-13T20:58:48+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@common.smart_subventions_matching
@pytest.mark.experiments3(filename='experiment_single_ride_deeplinks.json')
@pytest.mark.config(SUBVENTION_VIEW_ENABLE_STRANGE_SCHEDULE_HOTFIX=True)
async def test_from_lt_to_invariant(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        ssch,
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
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=True,
    )

    ssch.set_schedules(load_json('ssch_single_ride_strange_schedule.json'))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'schedule_type, now, expected_title',
    [
        pytest.param(
            'round_the_clock',
            (2022, 6, 12, 0),
            'Цель',
            id='not active, same schedule, 0-24',
        ),
        pytest.param(
            'same_schedule',
            (2022, 6, 12, 0),
            'Цель / 12:00 -- 14:59',
            id='not active, same schedule, not 0-24',
        ),
        pytest.param(
            'not_same_schedule',
            (2022, 6, 12, 0),
            'Цель / по расписанию',
            id='not active, not same schedule',
        ),
        pytest.param(
            'same_schedule',
            (2022, 6, 15, 0),
            'Цель / 12:00 -- 14:59',
            id='active, not last window day, same schedule',
        ),
        pytest.param(
            'not_same_schedule',
            (2022, 6, 16, 0),
            'Цель / по расписанию',
            id='active, not last window day, not same schedule',
        ),
        pytest.param(
            'not_same_schedule',
            (2022, 6, 19, 16),
            'Цель / до 17:59',
            id='active, last window day, last range',
        ),
        pytest.param(
            'not_same_schedule',
            (2022, 6, 19, 11),
            'Цель / 10:00 -- 11:59, 15:00 -- 17:59',
            id='active, last window day, not last range',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
    SUBVENTION_VIEW_SHOW_GOAL_SCHEDULE_IN_SUMMARY_TILE=True,
)
async def test_goal_schedule_tile_title(
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
        experiments3,
        schedule_type,
        now,
        expected_title,
        mocked_time,
):
    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1')

    bsx_goal_rule = load_json(
        'bsx_goal_response_template_without_counters_schedule_field.json',
    )

    if schedule_type == 'round_the_clock':
        bsx_goal_rule[0]['counters'].update(
            {
                'schedule': [
                    {'counter': 'A', 'start': '00:00', 'week_day': 'mon'},
                ],
            },
        )
    elif schedule_type == 'same_schedule':
        bsx_goal_rule[0]['counters'].update({'schedule': []})
        for week_day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            bsx_goal_rule[0]['counters']['schedule'].extend(
                [
                    {'counter': 'A', 'start': '12:00', 'week_day': week_day},
                    {'counter': '0', 'start': '15:00', 'week_day': week_day},
                ],
            )
    else:  # 'not_same_schedule'
        bsx_goal_rule[0]['counters'].update(
            {
                'schedule': [
                    {'counter': 'A', 'start': '00:00', 'week_day': 'thu'},
                    {'counter': '0', 'start': '12:00', 'week_day': 'fri'},
                    {'counter': 'A', 'start': '10:00', 'week_day': 'sun'},
                    {'counter': '0', 'start': '12:00', 'week_day': 'sun'},
                    {'counter': 'A', 'start': '15:00', 'week_day': 'sun'},
                    {'counter': '0', 'start': '18:00', 'week_day': 'sun'},
                ],
            },
        )

    bsx.set_rules(bsx_goal_rule)
    bsx.set_by_driver({'gA': 0})

    mocked_time.set(
        datetime.datetime(now[0], now[1], now[2], now[3]).astimezone(
            pytz.timezone('Europe/Moscow'),
        ),
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response = response.json()
    assert (
        response['ui']['panel_body'][1]['items'][0]['header']['title']['text']
        == expected_title
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('is_cargo', [False, True])
@pytest.mark.parametrize('progress', [0, 20])
@pytest.mark.parametrize(
    'now, window, start, end, expected_footer_end',
    [
        (
            (2022, 6, 12, 0),
            1,
            '2022-06-13T00:00:00+03:00',
            '2022-06-27T00:00:00+03:00',
            '13 июня',
        ),
        (
            (2022, 6, 19, 0),
            7,
            '2022-06-20T00:00:00+03:00',
            '2022-06-27T00:00:00+03:00',
            'с 20 по 26 июня',
        ),
        (
            (2022, 6, 26, 0),
            7,
            '2022-06-27T00:00:00+03:00',
            '2022-07-04T00:00:00+03:00',
            'с 27 июня по 3 июля',
        ),
        (
            (2022, 6, 16, 0),
            7,
            '2022-06-13T00:00:00+03:00',
            '2022-06-27T00:00:00+03:00',
            'до 19 июня',
        ),
        (
            (2022, 6, 19, 11),
            7,
            '2022-06-13T00:00:00+03:00',
            '2022-06-27T00:00:00+03:00',
            None,
        ),
    ],
)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SUBVENTIONS_FETCH_PERIOD_MINUTES=1440,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
    SUBVENTION_VIEW_SHOW_GOAL_SCHEDULE_IN_SUMMARY_TILE=True,
)
async def test_goal_schedule_tile_footer(
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
        experiments3,
        mocked_time,
        is_cargo,
        progress,
        now,
        window,
        start,
        end,
        expected_footer_end,
):
    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_view_use_cargo_tanker_keys',
        consumers=['subvention-view/v1/summary'],
        clauses=[],
        default_value={'use_cargo_keys': is_cargo},
    )

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1')

    bsx_goal_rule = load_json(
        'bsx_goal_response_template_without_start_end_window_fields.json',
    )
    bsx_goal_rule[0].update({'start': start, 'end': end, 'window': window})
    bsx.set_rules(bsx_goal_rule)
    bsx.set_by_driver({'gA': progress})

    mocked_time.set(
        datetime.datetime(now[0], now[1], now[2], now[3]).astimezone(
            pytz.timezone('Europe/Moscow'),
        ),
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    expected_footer = ''
    expected_footer_begin = ''
    if progress > 0:
        expected_footer_begin = '20 из 30'
    else:
        expected_footer_begin = '15'
    if is_cargo:
        expected_footer_begin += ' вручений'
    else:
        expected_footer_begin += ' заказов'

    expected_footer = expected_footer_begin
    if expected_footer_end is not None:
        expected_footer += ' / ' + expected_footer_end

    assert response.status_code == 200
    response = response.json()
    assert (
        response['ui']['panel_body'][1]['items'][0]['footer']['title']['text']
        == expected_footer
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
    SUBVENTION_RULE_UTILS_ENABLE_GOAL_STOP_TAGS=True,
)
@pytest.mark.parametrize(
    'driver_tags,expect_rule_disabled',
    [(['some_tag'], False), (['some_tag', 'stop_tag'], True)],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_goal_stop_tag(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        experiments3,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        driver_trackstory,
        candidates,
        driver_tags_mocks,
        driver_tags,
        expect_rule_disabled,
):
    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', driver_tags)

    bsx.set_rules(load_json('bsx_goal_with_stop_tag.json'))
    bsx.set_by_driver({'gA': 0})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()

    if expect_rule_disabled:
        assert response_data == {}
    else:
        assert response_data != {}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(SUBVENTION_VIEW_GET_GEO_EXPERIMENT_TAGS_FOR_ALL=True)
@common.smart_subventions_matching
@common.enable_single_ontop
async def test_geo_expriment_tags_for_all(
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
        driver_tags_mocks,
        experiments3,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['driver_tag'])

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    common.add_geo_experiment(
        experiments3, name='geo_exp_1', geo_exp_tag='geo_exp_tag_1',
    )

    expected_tags = {'driver_tag', 'geo_exp_tag_1'}
    covered_types = set()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _mock_v2_rules_select(request):
        nonlocal covered_types
        tags_constraint = request.json.get('tags_constraint')
        if tags_constraint is not None and 'tags' in tags_constraint:
            assert set(tags_constraint['tags']) == expected_tags
            for type_ in request.json['rule_types']:
                covered_types.add('bsx_' + type_)
        return {'rules': []}

    @mockserver.json_handler(
        '/subvention-schedule/internal/subvention-schedule/v1/schedule',
    )
    async def _mock_v1_schedule(request):
        nonlocal covered_types
        assert set(request.json['tags']) == expected_tags
        for type_ in request.json['types']:
            covered_types.add('ssch_' + type_)
        return {'schedules': []}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        # we don't use tags for personal requests
        if not request.json['is_personal']:
            assert set(request.json['profile_tags']) == expected_tags
            for type_ in request.json['types']:
                covered_types.add('bs_' + type_)
        return {'subventions': []}

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    assert _mock_v2_rules_select.times_called > 0
    assert _mock_v1_schedule.times_called > 0
    assert covered_types == {
        'ssch_single_ride',
        'bsx_single_ontop',
        'bsx_goal',
        'bs_daily_guarantee',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_SUMMARY_SHOW_END_TIME_FOR_GOALS='date_and_time',
    SUBVENTION_RULE_UTILS_DROP_ZERO_RULES=True,
)
async def test_degenerate_goal(
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
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    common.add_summary_exp3_config(
        experiments3, fetch_smart_goals=True, use_banner=False,
    )

    bsx.set_rules(load_json('bsx_degenerate_goal.json'))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/summary',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {}
