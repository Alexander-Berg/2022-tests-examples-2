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

CURRENT_DAY = '2021-03-15'
MOCK_NOW = f'{CURRENT_DAY}T14:15:16+0300'

DEFAULT_PARAMS = {
    'lon': '37.6',
    'lat': '55.73',
    'tz': 'Europe/Moscow',
    'date': CURRENT_DAY,
}


# returns non personal without tags, non personal with tags,
# personal without tags, personal with tags
def _partition_rules_select_requests(mock_bsx, times_called):
    assert mock_bsx.rules_select.times_called == times_called
    requests = []
    for _i in range(times_called):
        requests.append(mock_bsx.rules_select.next_call()['request_data'].json)
    return sorted(
        requests,
        key=lambda x: int('drivers' in x) * 10
        + int('tags_constraint' in x and 'tags' in x['tags_constraint']),
    )


def _test_check_bsx_params(mock_bsx):
    requests = _partition_rules_select_requests(mock_bsx, times_called=4)
    assert requests == [
        {
            'zones': [
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow',
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow/br_moscow_adm',
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow',
            ],
            'tariff_classes': ['comfort', 'econom', 'vip'],
            'branding': [
                'sticker',
                'no_full_branding',
                'sticker_and_lightbox',
                'any_branding',
            ],
            'time_range': {
                'start': '2021-03-14T21:00:00+00:00',
                'end': '2021-03-15T21:00:00+00:00',
            },
            'tags_constraint': {'has_tag': False},
            'rule_types': ['goal'],
            'limit': 1000,
        },
        {
            'zones': [
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow',
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow/br_moscow_adm',
                'br_root/br_russia/br_tsentralnyj_fo/'
                'br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow',
            ],
            'tariff_classes': ['comfort', 'econom', 'vip'],
            'branding': [
                'sticker',
                'no_full_branding',
                'sticker_and_lightbox',
                'any_branding',
            ],
            'time_range': {
                'start': '2021-03-14T21:00:00+00:00',
                'end': '2021-03-15T21:00:00+00:00',
            },
            'tags_constraint': {'tags': ['normal_tag', 'v_tag1', 'v_tag2']},
            'rule_types': ['goal'],
            'limit': 1000,
        },
        {
            'time_range': {
                'start': '2021-03-14T21:00:00+00:00',
                'end': '2021-03-15T21:00:00+00:00',
            },
            'tags_constraint': {'has_tag': False},
            'rule_types': ['goal'],
            'drivers': ['udid'],
            'limit': 1000,
            'tariff_classes': ['comfort', 'econom', 'vip'],
            'branding': [
                'sticker',
                'no_full_branding',
                'sticker_and_lightbox',
                'any_branding',
            ],
        },
        {
            'time_range': {
                'start': '2021-03-14T21:00:00+00:00',
                'end': '2021-03-15T21:00:00+00:00',
            },
            'tags_constraint': {'tags': ['normal_tag', 'v_tag1', 'v_tag2']},
            'rule_types': ['goal'],
            'drivers': ['udid'],
            'limit': 1000,
            'tariff_classes': ['comfort', 'econom', 'vip'],
            'branding': [
                'sticker',
                'no_full_branding',
                'sticker_and_lightbox',
                'any_branding',
            ],
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS=True,
)
async def test_empty_subventions(
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

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'appbar': {'title': 'Цели'},
        'goals': [{'text': 'В этот день субсидий нет', 'type': 'text'}],
    }
    _test_check_bsx_params(bsx)
    assert bss.rules_select.times_called == 1
    assert json.loads(bss.rules_select_call_params[0]) == {
        'drivers': [{'unique_driver_id': 'udid'}],
        'is_personal': True,
        'limit': 1000,
        'profile_tags': ['v_tag1', 'v_tag2'],
        'status': 'enabled',
        'time_range': {
            'end': '2021-03-15T21:00:00+00:00',
            'start': '2021-03-14T21:00:00+00:00',
        },
        'types': ['goal'],
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_FETCH_GOALS_EXTRA_TARIFFS={
        'econom': ['comfort', 'comfort_plus'],
        'vip': ['business'],
    },
)
async def test_additional_classes_from_config(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        driver_tags_mocks,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['mock_tag_1'])
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'appbar': {'title': 'Цели'},
        'goals': [{'text': 'В этот день субсидий нет', 'type': 'text'}],
    }
    requests = _partition_rules_select_requests(bsx, times_called=4)
    assert sorted(requests[0]['tariff_classes']) == [
        'business',
        'comfort',
        'comfort_plus',
        'econom',
        'vip',
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_goals(
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
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_rules_select_response_test_goals.json'))
    bsx.set_by_driver(
        {'global_counter1': 20, 'global_counter2': 4, 'global_counter3': 0},
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('goals_response.json')
    assert bsx.by_driver.times_called == 1

    by_driver_request = bsx.by_driver.next_call()['request_data'].json
    assert sorted(by_driver_request['global_counters']) == [
        'global_counter1',
        'global_counter2',
        'global_counter3',
    ]
    assert by_driver_request['time_range'] == {
        'end': '2021-03-15T21:00:00+00:00',
        'start': '2021-03-14T21:00:00+00:00',
    }
    assert by_driver_request['unique_driver_id'] == 'udid'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'disabled_tag', ('subv_disable_goal', 'subv_disable_all'),
)
async def test_disabled_by_tags_goals(
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
        bsx,
        disabled_tag,
        driver_tags_mocks,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_rules_select_response_test_goals.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', [disabled_tag])
    bsx.set_by_driver(
        {'global_counter1': 20, 'global_counter2': 0, 'global_counter3': 0},
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'test_disabled_by_tag_goals_response.json',
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={'mapping_econom': {'classes': ['econom']}},
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
        bsx,
):

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(
        {
            'drivers': [
                {
                    'classes': ['mapping_econom'],
                    'dbid': '777',
                    'position': [37.590533, 55.733863],
                    'uuid': '888',
                },
            ],
        },
    )

    bsx_rules = load_json('bsx_rules_select_response_mapping_econom.json')
    bsx_rules[0]['tariff_class'] = 'mapping_econom'
    bsx.set_rules(bsx_rules)

    bsx.set_by_driver({'global_counter1': 20, 'global_counter2': 4})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('goals_response_mapping.json')
    assert bsx.by_driver.times_called == 1
    by_driver_request = bsx.by_driver.next_call()['request_data'].json
    assert by_driver_request == {
        'global_counters': ['global_counter2', 'global_counter1'],
        'time_range': {
            'end': '2021-03-15T21:00:00+00:00',
            'start': '2021-03-14T21:00:00+00:00',
        },
        'unique_driver_id': 'udid',
        'timezone': 'Europe/Moscow',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_wrong_client_tz(
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
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    bsx.set_rules(load_json('bsx_rules_select_response_test_goals.json'))
    bsx.set_by_driver(
        {'global_counter1': 20, 'global_counter2': 0, 'global_counter3': 0},
    )

    params = copy.deepcopy(DEFAULT_PARAMS)
    params['tz'] = 'Asia/Yekaterinburg'
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=params,
    )
    assert response.status_code == 200
    requests = _partition_rules_select_requests(bsx, times_called=3)
    assert requests[0]['time_range'] == {
        'end': '2021-03-15T21:00:00+00:00',
        'start': '2021-03-14T21:00:00+00:00',
    }


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
        candidates,
        driver_trackstory,
        driver_tags_mocks,
        dmi,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 503


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('fetch_bss_goals', (True, False))
async def test_disable_bss_goals(
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
        bsx,
        fetch_bss_goals,
        taxi_config,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    taxi_config.set(
        SUBVENTION_VIEW_GOALS_FETCH_OLD_PERSONAL_GOALS=fetch_bss_goals,
    )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert bss.rules_select.times_called == fetch_bss_goals


@pytest.mark.geoareas(filename='geoareas.json')
async def test_got_404(
        taxi_subvention_view,
        driver_authorizer,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_tags_mocks,
        dmi,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 1)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_position(request):
        return mockserver.make_response(
            json={'message': 'Not found'}, status=404,
        )

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 404


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_FETCH_GOALS_EXTRA_TARIFFS={'econom': ['courier']},
    SUBVENTION_VIEW_USE_INLINE_BRANDING_TANKER_KEYS=True,
)
@pytest.mark.parametrize(
    'rule_requirements,expected_response',
    [
        pytest.param(  # show only tariff
            {'tariff_class': 'econom'},
            'goals_response_requirements_match.json',
            id='match',
        ),
        pytest.param(  # show tariff violated
            {'tariff_class': 'courier'},
            'goals_response_requirements_tariff_mismatch.json',
            id='tariff_mismatch',
        ),
        pytest.param(  # show branding violated and tariff ok
            {'tariff_class': 'econom', 'branding_type': 'sticker'},
            'goals_response_requirements_branding_mismatch.json',
            id='branding_mismatch',
        ),
        pytest.param(  # show activity and tariff violated
            {'tariff_class': 'courier', 'activity_points': 100},
            'goals_response_requirements_activity_tariff_mismatch.json',
            id='activity_tariff_mismatch',
        ),
        pytest.param(  # show all requirements (except location) violated
            {
                'tariff_class': 'courier',
                'activity_points': 100,
                'branding_type': 'sticker_and_lightbox',
            },
            'goals_response_requirements_total_mismatch.json',
            id='total_mismatch',
        ),
    ],
)
async def test_bsx_goal_requirements(
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
        rule_requirements,
        expected_response,
        taxi_config,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    rules = load_json('bsx_rules_select_response_test_goal_requirements.json')
    assert len(rules) == 1
    rules[0].update(rule_requirements)
    bsx.set_rules(rules)
    bsx.set_by_driver({'global_counter1': 20})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
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
            'region_id': '1',
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
    bsx.set_by_driver({'global_counter1': 20})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2021-07-15T08:30:00+0000')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True)
async def test_goal_starts_tomorrow(
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
        bsx,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    bsx.set_rules(load_json('bsx_rules_select_response_tomorrow_goal.json'))
    bsx.set_by_driver({})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '37.6',
            'lat': '55.73',
            'tz': 'Europe/Moscow',
            'date': '2021-07-16',
        },
    )
    assert response.status_code == 200

    assert response.json() == load_json('goals_response_tomorrow_goal.json')


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
            'region_id': '162',
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

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '37.6',
            'lat': '55.73',
            'tz': 'Europe/Moscow',
            'date': '2021-07-16',
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response['goals'][0]['items'][0]['subtitle'] == '5 из 20 доставок'
    assert (
        response['goals'][0]['items'][2]['items'][0]['subtitle']
        == '10 доставок'
    )
    assert (
        response['goals'][0]['items'][2]['items'][1]['subtitle']
        == '20 доставок'
    )
    assert (
        response['goals'][0]['items'][3]['rows'][2]['key']['text']
        == 'Место доставок:'
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
    'list_with_geonodes',
    [
        pytest.param(
            [{'geonode': 'br_root/br_bad_geonode/inactive_tariff_zone'}],
            id='one_inactive_tariff_zone',
        ),
        pytest.param(
            [{'geonode': 'br_root/br_bad_geonode'}],
            id='one_geonode_with_inactive_tariff_zone',
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
        list_with_geonodes,
):
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
    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '76.9',
            'lat': '43.2',
            'tz': 'Europe/Moscow',
            'date': '2021-07-16',
        },
    )
    assert response.status_code == 200
    expected_response = {
        'goals': [{'type': 'text', 'text': 'В этот день субсидий нет'}],
        'appbar': {'title': 'Цели'},
    }
    assert response.json() == expected_response


@common.TALLINN_GEONODES
@pytest.mark.parametrize(
    'mock_now,date,expected_title',
    [
        # Estonia switches clocks on October 31
        ('2021-10-30T12:00:00+0000', '2021-10-30', 'сегодня'),
        ('2021-10-31T16:00:00+0000', '2021-10-30', 'до 23:59, 30 октября'),
        ('2021-10-31T16:00:00+0000', '2021-11-01', 'до 23:59, 1 ноября'),
        ('2021-10-31T16:25:00+0000', '2021-10-31', 'сегодня'),
        ('2021-10-31T16:25:00+0000', '2021-10-30', 'до 23:59, 30 октября'),
        ('2021-10-31T16:25:00+0000', '2021-11-01', 'до 23:59, 1 ноября'),
        #
        # ...then switches back on March, 27
        ('2022-03-26T14:00:00+0000', '2022-03-27', 'до 23:59, 27 марта'),
        ('2022-03-26T14:00:00+0000', '2022-03-28', 'до 23:59, 28 марта'),
        ('2022-03-27T08:00:00+0000', '2022-03-27', 'сегодня'),
        ('2022-03-27T08:00:00+0000', '2022-03-26', 'до 23:59, 26 марта'),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_BUILD_SCHEDULE_FOR_FUTURE_GOALS=True,
    SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False,
)
async def test_switch_to_winter_time(
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
        bsx,
        mocked_time,
        mock_now,
        date,
        expected_title,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_trackstory.set_position({'lat': 59.437425, 'lon': 24.745137})
    mocked_time.set(common.parse_time(mock_now))

    bsx.set_rules(load_json('bsx_goal_tallinn_switching_clocks.json'))
    bsx.set_by_driver({'607700:A': 12})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params={
            'lon': '24.745137',
            'lat': '59.437425',
            'tz': 'Europe/Tallinn',
            'date': date,
        },
    )
    assert response.status_code == 200

    assert response.json()['goals'][0]['items'][0]['title'] == expected_title


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SUBVENTION_VIEW_FETCH_GOALS_EXTRA_TARIFFS={'econom': ['courier']},
    SUBVENTION_VIEW_GOALS_SHOW_SCHEDULE_IN_CARDS=True,
)
@pytest.mark.parametrize(
    'show_last_minute_in_schedule, expected_schedules',
    [
        (
            True,
            ('03:30 — 04:40', '01:10 — 02:20, 10:11 — 20:02, 20:22 — 00:00'),
        ),
        (
            False,
            ('03:30 — 04:39', '01:10 — 02:19, 10:11 — 20:01, 20:22 — 23:59'),
        ),
    ],
)
async def test_goals_schedule_in_cards(
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
        show_last_minute_in_schedule,
        expected_schedules,
):
    taxi_config.set(
        SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=show_last_minute_in_schedule,  # noqa: E501
    )

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 90)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(
        load_json('parks_cars_list_no_branding.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    rules = load_json('bsx_rules_select_response_test_schedule_in_cards.json')
    assert len(rules) == 2
    bsx.set_rules(rules)
    bsx.set_by_driver({'530935:A': 0, '530936:A': 0})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200

    response = response.json()
    assert (
        response['goals'][0]['items'][3]['rows'][0]['value']['text']
        == expected_schedules[0]
    )
    assert (
        response['goals'][1]['items'][3]['rows'][0]['value']['text']
        == expected_schedules[1]
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
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
            'goals_comissions_response_A.json',
        ),
        (
            'comission_A',
            'global_counter1',
            20,
            'bsx_rules_select_response_test_goals_comissions_A.json',
            'goals_comissions_response_A_completed.json',
        ),
        (
            'comission_B',
            'global_counter1',
            15,
            'bsx_rules_select_response_test_goals_comissions_B.json',
            'goals_comissions_response_B.json',
        ),
        (
            'comission_B',
            'global_counter1',
            20,
            'bsx_rules_select_response_test_goals_comissions_B.json',
            'goals_comissions_response_B_completed.json',
        ),
    ],
)
async def test_goals_comissions(
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

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
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
        'end': '2021-03-15T21:00:00+00:00',
        'start': '2021-03-14T21:00:00+00:00',
    }
    assert by_driver_request['unique_driver_id'] == 'udid'


@pytest.mark.parametrize(
    'v2_by_driver_optimization,mock_now,goal_start,'
    'expect_v2_by_driver_request',
    [
        pytest.param(
            # v2_by_driver_optimization
            True,
            # mock_now
            '2020-06-01T14:15:16+0300',
            # goal_start
            '2020-06-01T00:00:00+03:00',
            # expect_v2_by_driver_request
            True,
            id='current goal',
        ),
        pytest.param(
            # v2_by_driver_optimization
            True,
            # mock_now
            '2020-06-01T14:15:16+0300',
            # goal_start
            '2020-06-02T00:00:00+03:00',
            # expect_v2_by_driver_request
            False,
            id='future goal',
        ),
        pytest.param(
            # v2_by_driver_optimization
            False,
            # mock_now
            '2020-06-01T14:15:16+0300',
            # goal_start
            '2020-06-02T00:00:00+03:00',
            # expect_v2_by_driver_request
            True,
            id='old behaviour',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v2_by_driver_optimization(
        taxi_subvention_view,
        mocked_time,
        taxi_config,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        activity,
        vehicles,
        candidates,
        driver_trackstory,
        bsx,
        v2_by_driver_optimization,
        mock_now,
        goal_start,
        expect_v2_by_driver_request,
):
    taxi_config.set_values(
        {
            'SUBVENTION_VIEW_SKIP_FUTURE_GOALS_IN_V2_BY_DRIVER': (
                v2_by_driver_optimization
            ),
        },
    )

    mocked_time.set(common.parse_time(mock_now))
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid')
    activity.add_driver('udid', 100)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    goal = load_json('bsx_goal_proto.json')
    goal['start'] = goal_start

    bsx.set_rules([goal])
    bsx.set_by_driver({'gA': 0})

    response = await taxi_subvention_view.get(
        '/driver/v1/subvention-view/v1/view/goals',
        headers=DEFAULT_HEADERS,
        params=DEFAULT_PARAMS,
    )

    assert response.status_code == 200
    assert bsx.by_driver.times_called == int(expect_v2_by_driver_request)

    items = response.json()['goals'][0]['items']
    progress = [itm for itm in items if itm.get('type') == 'progress'][0]
    assert progress['current_value'] == 0
