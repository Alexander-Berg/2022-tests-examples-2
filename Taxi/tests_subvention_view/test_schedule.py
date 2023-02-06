# pylint: disable=too-many-lines, pointless-string-statement, bad-whitespace

import json

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

SELFREG_HEADERS = {
    'Accept-Language': 'ru',
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

VEHICLE_BINDING_FULL_BRANDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle2'},
        },
    ],
}


def make_selfreg_activity(expected_data, headers):
    if 'X-YaTaxi-Driver-Profile-Id' not in headers:
        for elem in expected_data['items_for_map']:
            if 'driver_points_current' in elem:
                elem['driver_points_current'] = 100.0
        for elem in expected_data['items_for_schedule']:
            for rule in elem['rules']:
                if 'driver_points_current' in rule:
                    rule['driver_points_current'] = 100.0


async def request_schedule(taxi_sv, lat_lon, headers):
    request_params = lat_lon
    request_params['selfreg_token'] = 'selfreg_token'
    return await taxi_sv.get(
        '/v1/schedule', params=request_params, headers=headers,
    )


async def request_admin_schedule(taxi_sv, lat_lon, headers):
    request_params = lat_lon
    request_params['park_id'] = 'dbid1'
    request_params['driver_profile_id'] = 'driver1'
    return await taxi_sv.get(
        '/admin/v1/schedule', params=request_params, headers=headers,
    )


def transform_expected_for_ontop(expected):
    for item in expected['items_for_schedule']:
        for rule in item['rules']:
            rule['type'] = 'add'
            for descr_item in rule['description_items']:
                if 'payload' in descr_item:
                    descr_item['payload']['description_type'] = 'add'

    if 'items_for_map' in expected:
        for item in expected['items_for_map']:
            item['type'] = 'add'
            for descr_item in item['description_items']:
                if 'payload' in descr_item:
                    descr_item['payload']['description_type'] = 'add'


@pytest.mark.now('2020-06-25T12:05:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            'expected_moscow_merged_steps.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                        'split_geoareas': True,
                        'merge_geoareas': False,
                        'merge_different_steps': True,
                    },
                ),
            ],
        ),
        pytest.param(
            'expected_moscow_not_merged_steps.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                        'split_geoareas': True,
                        'merge_geoareas': False,
                        'merge_different_steps': False,
                    },
                ),
            ],
        ),
    ],
)
async def test_merged_steps_bug(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        expected,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    bss.add_rules(load_json('billing_rules_merged_steps.json'))
    candidates.load_profiles(
        load_json('candidates_profiles_response_merged_steps.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json(expected)
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert expected_data == response_data


@pytest.mark.now('2020-06-25T12:05:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_gebooking_steps(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    bss.add_rules(load_json('billing_rules_gebooking_steps.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200


@pytest.mark.now('2020-06-19T16:05:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_merge_bug(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90.0)
    bss.add_rules(load_json('billing_rules_merge_bug.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_merge_bug.json')
    make_selfreg_activity(expected_data, headers)
    assert expected_data == response_data


@pytest.mark.now('2020-06-11T16:15:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_empty_geoareas(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_multiple.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_no_subventions(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    if use_admin:
        response2 = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response2 = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response2.status_code == 200
    response_data2 = response2.json()

    assert response_data == response_data2
    assert response_data == load_json('expected_empty.json')


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_billing_subvention_rules_multiple_geoareas(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('geobooking_rule_moscow_multiple_geoareas.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    if use_admin:
        response2 = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response2 = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response2.status_code == 200
    response_data2 = response2.json()

    assert response_data == response_data2
    expected_json = load_json('expected_moscow_multiple_geoareas.json')
    make_selfreg_activity(expected_json, headers)
    assert response_data == expected_json


@pytest.mark.now('2020-06-17T12:59:16+0300')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_class_filtering(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 89.0)
    bss.add_rules(load_json('billing_rules_filter_tariff.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_empty.json')
    assert expected_data == response_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_onorder_subvention_groups(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow.json')
    make_selfreg_activity(expected_data, headers)
    assert expected_data == response_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_last_minute_in_schedule(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        taxi_config,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    taxi_config.set(SUBVENTION_VIEW_SHOW_LAST_MINUTE_IN_SCHEDULE=False)

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_last_schedule_last_minute.json',
    )


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 7, 'almaty': 4},
    # 590 minutes = 9 hours, 50 minutes
    # now + ~10 hours is the next day (2017-07-07)
    SCHEDULE_MAP_DISPLAYING_START_LIMIT=590,
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='driver1', tags=['almaty_tag'],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_onorder_subvention_groups_almaty(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_almaty.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '43.238286', 'lon': '76.945456'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    assert load_json('expected_almaty.json') == response.json()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 1})
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_onorder_subvention_groups_empty(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()
    expected_json = {
        'items_for_map': [],
        'items_for_schedule': [
            {
                'date': '2017-07-06',
                'localized_date': 'Ближайшие сутки',
                'localized_price': '600_₽',
                'rules': [
                    {
                        'driver_points_current': 90.0,
                        'driver_points_required': 70.0,
                        'from': '00:00',
                        'from_utc': '2017-07-05T21:00:00+0000',
                        'id': '_id/57def69d3d11433ca46fa4c8',
                        'is_active': True,
                        'localized_driver_points': 'Карма',
                        'localized_geo_description': 'По всему городу',
                        'localized_requirements_status': 'выполнено',
                        'localized_time': 'Круглосуточно',
                        'steps': [{'localized_sum': '600_₽', 'sum': 600.0}],
                        'to': '00:00',
                        'to_utc': '2017-07-06T21:00:00+0000',
                        'type': 'add',
                    },
                ],
                'slider_from_utc': '2017-07-06T11:00:00+0000',
                'slider_to_utc': '2017-07-07T11:00:00+0000',
            },
        ],
        'localized_required_for_bonuses': 'Требуется для получения доплат:',
        'localized_requirements': 'Требования для получения доплат:',
        'localized_steps': 'Этапы получения бонуса',
        'subvention_descriptions': [
            {
                'text': (
                    'Необходимо быть в синей зоне ... Пусть гарантия '
                    '800_₽, заработок 600_₽, бонус - 200_₽ '
                    '(200_₽ + 600_₽ = 800_₽)'
                ),
                'title': 'Подробнее о гарантии',
                'type': 'geo_booking',
            },
            {
                'text': 'Минималка за заказ',
                'title': 'Подробнее о доплате',
                'type': 'guarantee',
            },
        ],
    }
    make_selfreg_activity(expected_json, headers)
    assert response_data == expected_json


@pytest.mark.now('2017-07-07T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 3})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='driver1', tags=['almaty_tag'],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_onorder_subvention_groups_almaty_friday(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_almaty.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '43.238286', 'lon': '76.945456'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == load_json('expected_almaty_friday.json')


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_enabled_subventions_by_driver_points_default(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_driver_points.json')
    make_selfreg_activity(expected_data, headers)
    assert response_data == expected_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_enabled_subventions_by_driver_points_city(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_driver_points.json')
    make_selfreg_activity(expected_data, headers)
    assert response_data == expected_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_billing_subvention_rules(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    bss.add_rules(load_json('geobooking_rule_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_booking.json')
    make_selfreg_activity(expected_data, headers)
    assert response_data == expected_data
    bss.clean_rules()


@pytest.mark.parametrize('return_multiple_tariff_classes', (None, False, True))
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_billing_subvention_rules_with_multiple_tariff_classes(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        taxi_config,
        candidates,
        vehicles,
        return_multiple_tariff_classes,
        headers,
        use_admin,
):
    def _check_rule(rule: dict):
        nonlocal return_multiple_tariff_classes
        tariff_class = rule['tariff_class']
        localized_tariff_class = rule['localized_tariff_class']
        if return_multiple_tariff_classes:
            assert tariff_class == [
                'econom',
                'comfort',
                'business',
                'new_tariff',
                'new_tariff1',
            ]
            assert localized_tariff_class == [
                'Эконом',
                'Комфорт',
                'Бизнес',
                'Новый тариф',
                '1Новый тариф',
            ]
        else:
            assert tariff_class == ['econom']
            assert localized_tariff_class == ['Эконом']

    if return_multiple_tariff_classes is not None:
        taxi_config.set_values(
            dict(
                SUBVENTION_VIEW_RETURN_ALL_RULE_TARIFFS=(
                    return_multiple_tariff_classes
                ),
            ),
        )
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_multiple_tariff_classes.json'))
    bss.add_rules(load_json('geobooking_rule_multiple_tariff_classes.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()
    items_for_schedule = response_data['items_for_schedule']
    assert items_for_schedule
    for item_for_schedule in items_for_schedule:
        rules = item_for_schedule['rules']
        for rule in rules:
            _check_rule(rule)

    items_for_map = response_data['items_for_map']
    assert items_for_map
    for rule in items_for_map:
        _check_rule(rule)

    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'billing_rules_file, expected_result_file',
    [
        ('billing_rules_moscow2.json', 'expected_moscow_booking2.json'),
        ('billing_rules_moscow.json', 'expected_moscow_booking3.json'),
    ],
)
async def test_order_nums_from_by_driver(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        billing_rules_file,
        expected_result_file,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json(billing_rules_file))
    bss.add_rules(load_json('geobooking_rule_moscow.json'))

    bss.add_by_driver_subventions(load_json('by_driver_response.json'))

    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    if (
            billing_rules_file == 'billing_rules_moscow2.json'
            and 'X-YaTaxi-Driver-Profile-Id' in headers
    ):
        assert bss.by_driver_calls == 1
        by_driver_request = json.loads(bss.by_driver_call_params[0])
        by_driver_request['subvention_rule_ids'].sort()
        assert by_driver_request == {
            'time': '2017-07-06T11:15:16+00:00',
            'is_personal': False,
            'unique_driver_id': '59648321ea19f1bacf079756',
            'subvention_rule_ids': [
                'group_id/fcc640e3ccf238a514672df5202e82ae71bf2160',
                'group_id/fcc640e3ccf238a514672df5202e82ae71bf2161',
            ],
        }
    else:
        assert bss.by_driver_calls == 0
    bss.clean_rules()

    expected_data = load_json(expected_result_file)
    make_selfreg_activity(expected_data, headers)
    if (
            'X-YaTaxi-Driver-Profile-Id' in headers
            or billing_rules_file != 'billing_rules_moscow2.json'
    ):
        assert response_data == expected_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.config(SUBVENTION_VIEW_USE_BY_DRIVER_FALLBACK_CACHE=True)
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_by_driver_fallback_cache(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        mockserver,
        statistics,
        use_admin,
):
    await taxi_subvention_view.invalidate_caches()

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow2.json'))
    bss.add_rules(load_json('geobooking_rule_moscow.json'))

    bss.add_by_driver_subventions(load_json('by_driver_response.json'))

    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        await request_admin_schedule(taxi_subvention_view, lat_lon, headers)
    else:
        await request_schedule(taxi_subvention_view, lat_lon, headers)

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    statistics.fallbacks = ['subvention_view.bs-by_driver.fallback']

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    assert mock_bs_by_driver.times_called == 0
    assert bss.by_driver_calls == 1
    by_driver_request = json.loads(bss.by_driver_call_params[0])
    by_driver_request['subvention_rule_ids'].sort()
    assert by_driver_request == {
        'time': '2017-07-06T11:15:16+00:00',
        'is_personal': False,
        'unique_driver_id': '59648321ea19f1bacf079756',
        'subvention_rule_ids': [
            'group_id/fcc640e3ccf238a514672df5202e82ae71bf2160',
            'group_id/fcc640e3ccf238a514672df5202e82ae71bf2161',
        ],
    }

    bss.clean_rules()

    expected_data = load_json('expected_moscow_booking2.json')
    assert response_data == expected_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_onorder_subvention_groups_billing(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_billing.json')
    make_selfreg_activity(expected_data, headers)
    assert response_data == expected_data
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SCHEDULE_DESCRIPTION_PARAMS={
        '__default__': {'__default__': {'orders_sum': 15.1, 'bonus': 1.7}},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 1}},
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_dynamic_description_decimals(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_decimals.json')
    make_selfreg_activity(expected_data, headers)
    assert response_data == expected_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_error_when_no_cache_available(
        taxi_subvention_view,
        mockserver,
        driver_authorizer,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_external(request):
        return mockserver.make_response('', 500)

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 500


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='driver1', tags=['luxary'])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_billing_subvention_rules_request_body_required_types(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('geobooking_rule_moscow_with_tags.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    bss_requests = bss.rules_select_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    expected_bss_request = {
        'is_personal': False,
        'limit': 1000,
        'types': ['geo_booking', 'goal'],
        'driver_branding': 'sticker',
        'profile_tags': ['luxary'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2017-07-13T11:15:16+00:00',
            'start': '2017-07-06T11:15:16+00:00',
        },
    }
    if 'X-YaTaxi-Driver-Profile-Id' not in headers:
        expected_bss_request['driver_branding'] = 'no_branding'
        expected_bss_request['profile_tags'] = ['selfreg_v2_profi_unreg']
    assert json.loads(bss_requests[0]) == expected_bss_request
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_billing_subvention_500_on_bad_subvention(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules([load_json('bad_rule.json')])
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'split,merge,bs_response,expected',
    [
        (
            True,
            False,
            'billing_rules_merge_bug.json',
            'expected_moscow_merge_bug.json',
        ),
        (
            False,
            False,
            'billing_rules_merge_bug.json',
            'expected_no_split.json',
        ),
        (
            False,
            True,
            'billing_rules_merge_geoareas.json',
            'expected_no_split_and_merge.json',
        ),
    ],
)
@pytest.mark.now('2020-06-19T16:05:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_merge_and_geoareas_split(
        taxi_subvention_view,
        load_json,
        taxi_config,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        split,
        merge,
        bs_response,
        expected,
        headers,
        use_admin,
):
    taxi_config.set_values(
        dict(
            SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                'split_geoareas': split,
                'merge_geoareas': merge,
            },
        ),
    )

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90.0)
    bss.add_rules(load_json(bs_response))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json(expected)
    make_selfreg_activity(expected_data, headers)
    assert expected_data == response_data


@pytest.mark.now('2020-07-23T11:44:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'bs_response,expected_response',
    [
        pytest.param(
            'billing_rules_moscow_courier_merge.json',
            'expected_moscow_courier_merge.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                        'split_geoareas': False,
                        'merge_geoareas': False,
                    },
                ),
            ],
        ),
        pytest.param(
            'billing_rules_moscow_courier_merge.json',
            'expected_moscow_courier_merge.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                        'split_geoareas': False,
                        'merge_geoareas': False,
                        'merge_geobooking': True,
                    },
                ),
            ],
        ),
        pytest.param(
            'billing_rules_moscow_courier_merge.json',
            'expected_moscow_courier_no_merge.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
                        'split_geoareas': False,
                        'merge_geoareas': False,
                        'merge_geobooking': False,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_billing_subvention_moscow_courier(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        bs_response,
        expected_response,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 100)
    bss.add_rules(load_json(bs_response))
    candidates.load_profiles(
        load_json('candidates_profiles_response_courier.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json(expected_response)
    assert expected_data == response_data


@pytest.mark.config(
    SCHEDULE_SUBVENTION_GEOAREAS_MERGE_SETTINGS={
        'split_geoareas': False,
        'merge_geoareas': False,
        'merge_geobooking': False,
    },
    SCHEDULE_DISPLAYING_DAYS={'__default__': 2},
)
@pytest.mark.now('2020-07-23T11:44:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'bs_response,expected_response',
    [
        pytest.param(
            'geobooking_rules_shift_end_bug.json',
            'expected_geobooking_rules_shift_end_bug.json',
        ),
        pytest.param(
            'geobooking_rules_shift_end_bug.json',
            'expected_geobooking_rules_shift_end_bug_fix.json',
            marks=[
                pytest.mark.config(
                    SCHEDULE_SUBVENTION_SCHEDULE_DAY_END_FIX=True,
                    SCHEDULE_DISPLAYING_DAYS={'__default__': 2},
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_geobooking_rules_shift_end_bug(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        bs_response,
        expected_response,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 100)
    bss.add_rules(load_json(bs_response))
    candidates.load_profiles(
        load_json('candidates_profiles_response_courier.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json(expected_response)
    assert expected_data == response_data


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SUBVENTION_VIEW_USE_DRIVER_TAGS_CACHE=True,
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_driver_tags_cache(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('geobooking_rule_moscow_multiple_geoareas.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert driver_tags_mocks.v1_match_profile.times_called == 1
    else:
        assert driver_tags_mocks.v1_match_profile.times_called == 0
    response_data = response.json()

    if use_admin:
        response2 = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response2 = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response2.status_code == 200
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert driver_tags_mocks.v1_match_profile.times_called == 1
    else:
        assert driver_tags_mocks.v1_match_profile.times_called == 0
    response_data2 = response2.json()

    assert response_data == response_data2
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response_data == load_json(
            'expected_moscow_multiple_geoareas.json',
        )


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(SUBVENTION_VIEW_MAP_TARIFF_CLASSES=True)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_tariff_classes_mapping(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        taxi_config,
        candidates,
        vehicles,
        headers,
        use_admin,
):
    def _check_rule(rule: dict):
        tariff_class = rule['tariff_class']
        localized_tariff_class = rule['localized_tariff_class']
        assert tariff_class == [
            'econom',
            'comfort',
            'business',
            'new_tariff',
            'new_tariff1',
            'vip',
        ]
        assert localized_tariff_class == [
            'Эконом',
            'Комфорт',
            'Бизнес',
            'Новый тариф',
            '1Новый тариф',
            'Вип',
        ]

    taxi_config.set_values(dict(SUBVENTION_VIEW_RETURN_ALL_RULE_TARIFFS=True))
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_multiple_tariff_classes.json'))
    bss.add_rules(load_json('geobooking_rule_uber_classes.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()
    items_for_schedule = response_data['items_for_schedule']
    assert items_for_schedule
    for item_for_schedule in items_for_schedule:
        rules = item_for_schedule['rules']
        for rule in rules:
            _check_rule(rule)

    items_for_map = response_data['items_for_map']
    assert items_for_map
    for rule in items_for_map:
        _check_rule(rule)

    bss.clean_rules()


@pytest.mark.now('2020-06-17T12:59:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'classes,expected_bs_call',
    [
        (
            ['econom', 'comfort', 'vip'],
            {
                'driver_branding': 'sticker',
                'is_personal': False,
                'limit': 1000,
                'order_tariff_classes': ['comfort', 'econom', 'vip'],
                'profile_tags': [],
                'profile_tariff_classes': ['comfort', 'econom', 'vip'],
                'status': 'enabled',
                'tariff_zone': 'moscow',
                'time_range': {
                    'end': '2020-06-24T09:59:16+00:00',
                    'start': '2020-06-17T09:59:16+00:00',
                },
                'types': ['geo_booking', 'goal'],
            },
        ),
        (
            [],
            {
                'driver_branding': 'sticker',
                'is_personal': False,
                'limit': 1000,
                'order_tariff_classes': [],
                'profile_tags': [],
                'profile_tariff_classes': [],
                'status': 'enabled',
                'tariff_zone': 'moscow',
                'time_range': {
                    'end': '2020-06-24T09:59:16+00:00',
                    'start': '2020-06-17T09:59:16+00:00',
                },
                'types': ['geo_booking', 'goal'],
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
@pytest.mark.config(SCHEDULE_ENABLE_TARIFF_FILTER_IN_REQUEST=True)
async def test_class_filtering_by_bs_call(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        classes,
        expected_bs_call,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(
        {
            'drivers': [
                {
                    'classes': classes,
                    'dbid': 'dbid1',
                    'position': [0.0, 0.0],
                    'uuid': 'driver1',
                },
            ],
        },
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert candidates.mock_profiles.times_called == 1
        candidates_request = json.loads(
            candidates.mock_profiles.next_call()['request'].get_data(),
        )
        assert candidates_request == {
            'data_keys': ['classes', 'payment_methods'],
            'driver_ids': [{'dbid': 'dbid1', 'uuid': 'driver1'}],
        }

        assert bss.calls == 1
        assert json.loads(bss.rules_select_call_params[0]) == expected_bs_call


@pytest.mark.now('2020-06-17T12:59:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'expected_subvention_types', [(['geo_booking', 'goal'])],
)
@pytest.mark.parametrize('use_admin', [False, True])
async def test_step_goals_in_bs_call(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        experiments3,
        expected_subvention_types,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    assert bss.calls == 1
    assert (
        json.loads(bss.rules_select_call_params[0])['types']
        == expected_subvention_types
    )


def _build_ssch_response_item(rule_id, tariff_zone, geoarea, rate):
    doc = {
        'type': 'single_ride',
        'items': [
            {
                'rule_id': rule_id,
                'draft_id': '1234abcd',
                'schedule_ref': '1234abcd',
                'time_range': {
                    'from': '2020-09-11T21:00:00+00:00',
                    'to': '2020-09-24T11:15:16+00:00',
                },
                'rate': rate,
                'tariff_zone': tariff_zone,
                'tariff_class': 'comfort',
            },
        ],
    }
    if geoarea is not None:
        doc['items'][0]['geoarea'] = geoarea
    return doc


def _build_rs_response_item(rule_id, tariff_zone, geoarea, rate):
    doc = {
        'rule_type': 'single_ride',
        'start': '2020-05-02T21:00:00+00:00',
        'end': '2021-05-30T21:00:00+00:00',
        'rates': [
            {'week_day': 'mon', 'start': '00:00', 'bonus_amount': str(rate)},
        ],
        'id': rule_id,
        'budget_id': 'abcd1234',
        'draft_id': '1234abcd',
        'schedule_ref': '1234abcd',
        'zone': tariff_zone,
        'tariff_class': 'comfort',
        'updated_at': '2020-05-02T21:00:00+00:00',
    }
    if geoarea is not None:
        doc['geoarea'] = geoarea
    return doc


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json',
    sg_filename='test_radius_subvention_geoareas.json',
)
@pytest.mark.tariffs(filename='tariffs.json')
@common.smart_subventions_matching
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'match_split_by': ['zone', 'geoarea'],
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
    USE_GEOINDEX={
        'to_find_nearest_zone': True,
        'to_find_nearest_zone_by_radius': True,
    },
)
@pytest.mark.parametrize(
    'radius_config,expected_tariff_zones,expected_rules',
    [
        pytest.param(
            # radius_config
            {},
            # expected_tariff_zones
            ['moscow'],
            # expected_rules
            ['moscow_near', 'moscow_far', 'moscow_full'],
            id='case1',
        ),
        pytest.param(
            # radius_config
            {'moscow': {'radius_km': 10}},
            # expected_tariff_zones
            ['moscow'],
            # expected_rules
            ['moscow_near', 'moscow_full'],
            id='case2',
        ),
        pytest.param(
            # radius_config
            {'moscow': {'adjacent_zones': ['khimki']}},
            # expected_tariff_zones
            ['moscow', 'khimki'],
            # expected_rules
            [
                'moscow_near',
                'moscow_far',
                'moscow_full',
                'khimki_near',
                'khimki_far',
            ],
            id='case3',
        ),
        pytest.param(
            # radius_config
            {'moscow': {'radius_km': 10, 'adjacent_zones': ['khimki']}},
            # expected_tariff_zones
            ['moscow', 'khimki'],
            # expected_rules
            ['moscow_near', 'moscow_full', 'khimki_near', 'khimki_far'],
            id='case4',
        ),
        pytest.param(
            # radius_config
            {
                'moscow': {
                    'adjacent_zone_default_radius': 6,
                    'adjacent_zones': ['khimki'],
                },
            },
            # expected_tariff_zones
            ['moscow', 'khimki'],
            # expected_rules
            ['moscow_near', 'moscow_far', 'moscow_full', 'khimki_near'],
            id='case5',
        ),
        pytest.param(
            # radius_config
            {
                'moscow': {
                    'radius_km': 10,
                    'adjacent_zone_default_radius': 6,
                    'adjacent_zones': ['khimki'],
                },
            },
            # expected_tariff_zones
            ['moscow', 'khimki'],
            # expected_rules
            ['moscow_near', 'moscow_full', 'khimki_near'],
            id='case6',
        ),
        pytest.param(
            # radius_config
            {
                'moscow': {
                    'adjacent_zones': [
                        'krasnogorsk',
                        {'name': 'khimki', 'radius_km': 6},
                    ],
                },
            },
            # expected_tariff_zones
            ['moscow', 'krasnogorsk', 'khimki'],
            # expected_rules
            [
                'moscow_near',
                'moscow_far',
                'moscow_full',
                'krasnogorsk_near',
                'krasnogorsk_far',
                'khimki_near',
            ],
            id='case7',
        ),
        pytest.param(
            # radius_config
            {
                'moscow': {
                    'adjacent_zone_default_radius': 6,
                    'adjacent_zones': [
                        'krasnogorsk',
                        {'name': 'khimki', 'radius_km': 1},
                    ],
                },
            },
            # expected_tariff_zones
            ['moscow', 'krasnogorsk', 'khimki'],
            # expected_rules
            ['moscow_near', 'moscow_far', 'moscow_full', 'krasnogorsk_near'],
            id='case8',
        ),
        pytest.param(
            # radius_config
            {
                'moscow': {
                    'radius_km': 10,
                    'adjacent_zone_default_radius': 6,
                    'adjacent_zones': [
                        'krasnogorsk',
                        {'name': 'khimki', 'radius_km': 1},
                    ],
                },
            },
            # expected_tariff_zones
            ['moscow', 'krasnogorsk', 'khimki'],
            # expected_rules
            ['moscow_near', 'moscow_full', 'krasnogorsk_near'],
            id='case9',
        ),
    ],
)
@pytest.mark.parametrize('use_admin', [False, True])
async def test_smart_subventions_radius(
        mockserver,
        experiments3,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        taxi_config,
        radius_config,
        expected_tariff_zones,
        expected_rules,
        use_admin,
):
    # geoarea          | distance to driver point (37.429651, 55.850930)
    # ------------------------------------------------------------------
    # moscow_near      | 3.5 km
    # moscow_far       | 15 km
    # khimki_near      | 3.5 km
    # khimki_far       | 11 km
    # krasnogorsk_near | 4 km
    # krasnogorsk_far  | 10 km

    # fmt: off
    schedule_items = [
        # rule_id            tariff_zone     geoarea             rate
        ('moscow_near',      'moscow',       'moscow_near',      1.0),
        ('moscow_far',       'moscow',       'moscow_far',       2.0),
        ('moscow_full',      'moscow',       None,               3.0),
        ('khimki_near',      'khimki',       'khimki_near',      4.0),
        ('khimki_far',       'khimki',       'khimki_far',       5.0),
        ('khimki_full',      'khimki',       None,               6.0),
        ('krasnogorsk_near', 'krasnogorsk',  'krasnogorsk_near', 7.0),
        ('krasnogorsk_far',  'krasnogorsk',  'krasnogorsk_far',  8.0),
        ('krasnogorsk_full', 'krasnogorsk',  None,               9.0),
    ]
    # fmt: on

    def _recognize_rules_from_schedule_response(response):
        result = []
        for item in response['items_for_schedule']:
            for rule in item['rules']:
                assert (
                    len(rule['steps']) == 1
                ), 'Wrong test logic, expected only 1 step'
                rate = rule['steps'][0]['sum']
                candidates = [i for i in schedule_items if i[3] == rate]
                assert (
                    len(candidates) <= 1
                ), 'Expected that rules have unique rates'
                assert candidates != [], 'Unexpected rule in response?'
                rule_id, _, _, _ = candidates[0]
                result.append(rule_id)
        return result

    @mockserver.json_handler(
        '/subvention-schedule/internal/subvention-schedule/v1/schedule',
    )
    async def _mock_v1_schedule(request):
        assert set(request.json['zones']) == set(expected_tariff_zones)
        response_items = []
        for item in schedule_items:
            rule_id, tariff_zone, geoarea, rate = item
            if tariff_zone in request.json['zones']:
                response_items.append(
                    _build_ssch_response_item(
                        rule_id, tariff_zone, geoarea, rate,
                    ),
                )
        return {'schedules': response_items}

    experiments3.add_experiments_json(
        {
            'configs': [
                {
                    'clauses': [
                        {
                            'predicate': {'type': 'true'},
                            'title': 'always true',
                            'value': radius_config,
                        },
                    ],
                    'default_value': {},
                    'match': {
                        'consumers': [{'name': 'subvention-view/v1/schedule'}],
                        'enabled': True,
                        'predicate': {'init': {}, 'type': 'true'},
                    },
                    'name': 'smart_subventions_radius_settings',
                },
            ],
        },
    )

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.850930', 'lon': '37.429651'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    actual_used_rules = _recognize_rules_from_schedule_response(
        response.json(),
    )
    assert set(actual_used_rules) == set(expected_rules)


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'arg_name': 'park_id',
                            'arg_type': 'string',
                            'value': 'dbid1',
                        },
                        'type': 'eq',
                    },
                    {
                        'init': {
                            'arg_name': 'driver_profile_id',
                            'arg_type': 'string',
                            'value': 'driver1',
                        },
                        'type': 'eq',
                    },
                ],
            },
            'type': 'all_of',
        },
        'enabled': True,
    },
    name='subvention_view_smart_matching',
    consumers=['subvention-view/v1/schedule'],
    clauses=[],
    default_value=True,
)
@pytest.mark.parametrize(
    'rules,lat,lon,expected',
    [
        (
            [
                {
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'rule_id': 'rule_01',
                    'tariff_class': 'econom',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
                {
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'rule_id': 'rule_02',
                    'tariff_class': 'comfort',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
            ],
            '55.733863',
            '37.590533',
            'expected_smart_merge_no_geaoares.json',
        ),
        (
            [
                {
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'rule_id': 'rule_01',
                    'geoarea': 'north-butovo-2',
                    'tariff_class': 'econom',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
                {
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'geoarea': 'moscow_walking',
                    'rule_id': 'rule_02',
                    'tariff_class': 'comfort',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
            ],
            '55.733863',
            '37.590533',
            'expected_smart_merge_geaoares.json',
        ),
        (
            [
                {
                    'geoarea': 'north-butovo-2',
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'rule_id': 'rule_01',
                    'tariff_class': 'econom',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
                {
                    'draft_id': '1234abcd',
                    'rate': 100500.0,
                    'rule_id': 'rule_02',
                    'tariff_class': 'comfort',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'from': '2020-09-13T21:00:00+00:00',
                        'to': '2020-09-21T11:15:16+00:00',
                    },
                },
            ],
            '55.733863',
            '37.590533',
            'expected_smart_no_merge.json',
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
)
@pytest.mark.parametrize(
    'split_by',
    [
        None,
        (['zone']),
        (['tariff_class']),
        (['geoarea']),
        (['zone', 'tariff_class', 'geoarea']),
    ],
)
@pytest.mark.parametrize(
    'headers, use_admin',
    [
        (DEFAULT_HEADERS, False),
        (SELFREG_HEADERS, False),
        (DEFAULT_HEADERS, True),
    ],
)
async def test_smart_subventions_drafts(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        rules,
        lat,
        lon,
        expected,
        taxi_config,
        split_by,
        headers,
        use_admin,
):
    if split_by:
        original_settings = dict(taxi_config.get('SMART_SUBVENTIONS_SETTINGS'))
        original_settings['match_split_by'] = split_by
        taxi_config.set_values(
            dict(SMART_SUBVENTIONS_SETTINGS=original_settings),
        )

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler(
        '/subvention-schedule/internal/subvention-schedule/v1/schedule',
    )
    async def _mock_ssch_get(request):
        return {'schedules': [{'type': 'single_ride', 'items': rules}]}

    lat_lon = {'lat': lat, 'lon': lon}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response_data == load_json(expected)
    else:
        assert not response_data['items_for_map']
        assert not response_data['items_for_schedule']


@pytest.mark.parametrize(
    'filter_not_active_rules, expected_rule_ids',
    [
        (
            True,
            ['_id/57def69d45af870f17d36f66', '_id/57def69d45af870f17d36f68'],
        ),
        (
            False,
            [
                '_id/57def69d45af870f17d36f66',
                '_id/57def69d45af870f17d36f68',
                '_id/57def69d45af870f17d36f67',
            ],
        ),
    ],
)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize('use_admin', [False, True])
async def test_filter_not_active_rules(
        now,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        taxi_config,
        candidates,
        vehicles,
        filter_not_active_rules,
        expected_rule_ids,
        use_admin,
):
    taxi_config.set(
        SUBVENTION_VIEW_SCHEDULE_FILTER_NOT_ACTIVE_RULES=(
            filter_not_active_rules
        ),
    )
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(
        load_json('billing_rules_have_not_active_in_active_rule_geoarea.json'),
    )
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    assert [
        item['id'] for item in response_data['items_for_map']
    ] == expected_rule_ids
    assert response_data['items_for_schedule'] == load_json(
        'expected_response_for_schedule.json',
    )
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SCHEDULE_DESCRIPTION_PARAMS={
        '__default__': {'__default__': {'orders_sum': 15.1, 'bonus': 1.7}},
    },
    SUBVENTION_VIEW_CURRENCY_FORMATTING={
        'enabled': True,
        'by_default': {'whole': 0, 'fractional': 0},
        'RUB': {
            'by_default': {'whole': 0, 'fractional': 0},
            'schedule': {'whole': 1, 'fractional': 1},
            'do_x_get_y': {'whole': 2, 'fractional': 2},
            'geobooking_bonus': {'whole': 3, 'fractional': 3},
        },
    },
)
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_currency_formatting(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    bss.add_rules(load_json('billing_rules_moscow.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_currency_formatting.json')
    make_selfreg_activity(expected_data, DEFAULT_HEADERS)
    assert response_data == expected_data


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.parametrize(
    'schedule,lat,lon,expected,zone',
    [
        (
            {
                'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                'draft_id': '1234abcd',
                'tariff_zone': 'moscow',
                'tariff_class': 'comfort',
                'rate': 100500,
                'time_range': {
                    'from': '2020-09-11T21:00:00+00:00',
                    'to': '2020-09-24T11:15:16+00:00',
                },
            },
            '55.733863',
            '37.590533',
            'expected_smart_moscow.json',
            'moscow',
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'clamp_activity': True,
    },
    SUBVENTION_VIEW_GET_GEO_EXPERIMENT_TAGS=True,
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS])
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.parametrize(
    'expected_geo_tags, send_to_yt',
    [
        pytest.param(
            ['geo_exp_tag_1'],
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='geo_experiments_ok_with_wrong_consumer.json',
                )
            ),
        ),
        pytest.param(
            ['geo_exp_tag_1', 'geo_exp_tag_2'],
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='geo_experiments_two_oks.json',
                )
            ),
        ),
        pytest.param(
            ['geo_exp_tag_1', 'geo_exp_tag_2'],
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='geo_experiments_two_oks.json',
                )
            ),
        ),
        pytest.param(
            [],
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='geo_experiments_wrong_consumer.json',
                )
            ),
        ),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='dbid1', uuid='driver1', tags=['geo_exp_stop_tag_1'],
)
async def test_smart_subventions_with_geo_experiments(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        ssch,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        schedule,
        lat,
        lon,
        expected,
        zone,
        taxi_config,
        headers,
        use_admin,
        expected_geo_tags,
        testpoint,
        send_to_yt,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'udid1')
    activity.add_driver('udid1', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    taxi_config.set(SUBVENTION_VIEW_SEND_GEO_EXPERIMENT_TAGS_TO_YT=send_to_yt)
    ssch.set_schedules([{'type': 'single_ride', 'items': [schedule]}])

    lat_lon = {'lat': lat, 'lon': lon}

    @testpoint('yt_geo_experiment_tags')
    def yt_geo_experiment_tags(geo_tags_json):
        assert geo_tags_json['park_id'] == 'dbid1'
        assert geo_tags_json['driver_profile_id'] == 'driver1'
        assert geo_tags_json['tags'] == expected_geo_tags

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 200

    await taxi_subvention_view.invalidate_caches()

    assert yt_geo_experiment_tags.times_called == send_to_yt
    expected_tags = ['geo_exp_stop_tag_1']
    for expected_geo_tag in expected_geo_tags:
        expected_tags.append(expected_geo_tag)

    if not expected_geo_tags:
        pass

    ssch_request = ssch.requests['schedule'][0]
    ssch_request['tags'].sort()

    assert {
        'activity_points': 100 if 'activity_points' in schedule else 90,
        'branding': {'has_lightbox': False, 'has_sticker': True},
        'tags': expected_tags,
        'tariff_classes': ['comfort', 'econom', 'vip'],
        'zones': [zone],
        'types': ['single_ride'],
        'time_range': {
            'from': '2020-09-14T11:15:16+00:00',
            'to': '2020-09-21T11:15:16+00:00',
        },
        'ignored_restrictions': [],
    } == ssch_request

    response_data = response.json()
    assert response_data == load_json(expected)


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.parametrize(
    'rule,lat,lon,expected,zone,start,reference_time',
    [
        (
            {
                'rule_type': 'single_ride',
                'start': '2020-05-02T21:00:00+00:00',
                'end': '2021-05-30T21:00:00+00:00',
                'rates': [
                    {
                        'week_day': 'mon',
                        'start': '18:00',
                        'bonus_amount': '10',
                    },
                ],
                'id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                'budget_id': 'abcd1234',
                'draft_id': '1234abcd',
                'schedule_ref': '1234abcd',
                'zone': 'moscow',
                'tariff_class': 'comfort',
                'updated_at': '2020-05-02T21:00:00+00:00',
            },
            '55.733863',
            '37.590533',
            'expected_smart_moscow.json',
            'moscow',
            '21:00:00+00:00',
            '2020-09-13T21:00:00+00:00',
        ),
    ],
)
@pytest.mark.config(SCHEDULE_DISPLAYING_DAYS={'__default__': 4})
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS])
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.parametrize(
    'ignored_restrictions',
    [[], ['activity'], ['branding'], ['activity', 'branding']],
)
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='driver1', tags=['tag_1'])
async def test_smart_subventions_use_ssch_experiment(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        rule,
        lat,
        lon,
        expected,
        zone,
        start,
        reference_time,
        taxi_config,
        headers,
        use_admin,
        ignored_restrictions,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    bsx.set_rules([rule])

    taxi_config.set_values(
        dict(
            SMART_SUBVENTIONS_SETTINGS={
                'restrictions': ['activity', 'geoarea'],
                'ignored_restrictions': ignored_restrictions,
                'clamp_activity': True,
            },
        ),
    )

    lat_lon = {'lat': lat, 'lon': lon}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 200

    assert ssch.calls['schedule'] == 1
    ssch_request = ssch.requests['schedule'][0]
    assert ssch_request == {
        'types': ['single_ride'],
        'ignored_restrictions': ignored_restrictions,
        'time_range': {
            'to': '2020-09-21T11:15:16+00:00',
            'from': '2020-09-14T11:15:16+00:00',
        },
        'activity_points': 90,
        'branding': {'has_lightbox': False, 'has_sticker': True},
        'tags': ['tag_1'],
        'tariff_classes': ['comfort', 'econom', 'vip'],
        'zones': [zone],
    }

    assert bsx.calls['rules_match'] == 0

    await taxi_subvention_view.invalidate_caches()


"""
Тестируется, что ответ от ssch/schedule успешно парсится и обрабатывается
"""


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.parametrize(
    'schedule_response,lat,lon,expected,zone,start,reference_time',
    [
        (
            [
                {
                    'type': 'single_ride',
                    'items': [
                        {
                            'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                            'draft_id': '1234abcd',
                            'time_range': {
                                'from': '2020-09-11T21:00:00+00:00',
                                'to': '2020-09-24T11:15:16+00:00',
                            },
                            'rate': 100500,
                            'tariff_zone': 'moscow',
                            'tariff_class': 'comfort',
                        },
                    ],
                },
            ],
            '55.733863',
            '37.590533',
            'expected_smart_moscow.json',
            'moscow',
            '21:00:00+00:00',
            '2020-09-13T21:00:00+00:00',
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'ignored_restrictions': [],
        'clamp_activity': True,
    },
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS])
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='driver1', tags=['tag_1'])
async def test_smart_subventions_use_ssch(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        schedule_response,
        lat,
        lon,
        expected,
        zone,
        start,
        reference_time,
        taxi_config,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    ssch.set_schedules(schedule_response)

    lat_lon = {'lat': lat, 'lon': lon}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 200

    assert ssch.calls['schedule'] == 1
    ssch_request = ssch.requests['schedule'][0]
    assert ssch_request == {
        'types': ['single_ride'],
        'ignored_restrictions': [],
        'time_range': {
            'to': '2020-09-21T11:15:16+00:00',
            'from': '2020-09-14T11:15:16+00:00',
        },
        'activity_points': 90,
        'branding': {'has_lightbox': False, 'has_sticker': True},
        'tags': ['tag_1'],
        'tariff_classes': ['comfort', 'econom', 'vip'],
        'zones': [zone],
    }

    assert bsx.calls['rules_match'] == 0

    response_data = response.json()
    assert response_data == load_json(expected)

    await taxi_subvention_view.invalidate_caches()


"""
Тестируется, что если в ответе кандидатов нет тарифных классов, запрос в ssch
сделан не будет, а вернется пустое расписание.
"""


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.parametrize(
    'schedule_response,lat,lon,expected,zone,start,reference_time',
    [
        (
            [
                {
                    'type': 'single_ride',
                    'items': [
                        {
                            'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                            'draft_id': '1234abcd',
                            'time_range': {
                                'from': '2020-09-11T21:00:00+00:00',
                                'to': '2020-09-24T11:15:16+00:00',
                            },
                            'rate': 100500,
                            'tariff_zone': 'moscow',
                            'tariff_class': 'comfort',
                        },
                    ],
                },
            ],
            '55.733863',
            '37.590533',
            'expected_smart_moscow.json',
            'moscow',
            '21:00:00+00:00',
            '2020-09-13T21:00:00+00:00',
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'ignored_restrictions': [],
        'clamp_activity': True,
    },
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS])
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='driver1', tags=['tag_1'])
async def test_smart_subventions_use_ssch_without_classes(
        mockserver,
        taxi_subvention_view,
        driver_authorizer,
        bss,
        bsx,
        ssch,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        schedule_response,
        lat,
        lon,
        expected,
        zone,
        start,
        reference_time,
        taxi_config,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(
        load_json('candidates_profiles_response_without_classes.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    lat_lon = {'lat': lat, 'lon': lon}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 200

    assert ssch.calls['schedule'] == 0
    assert bsx.calls['rules_match'] == 0

    response_data = response.json()
    assert response_data == {'items_for_map': [], 'items_for_schedule': []}

    await taxi_subvention_view.invalidate_caches()


@pytest.mark.now('2020-09-14T14:15:16+0300')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@common.smart_subventions_matching
@pytest.mark.parametrize(
    'schedule_response,lat,lon',
    [
        (
            [
                {
                    'type': 'single_ride',
                    'items': [
                        {
                            'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                            'draft_id': '1234abcd',
                            'time_range': {
                                'from': '2020-09-15T12:00:00+00:00',
                                'to': '2020-09-15T12:00:01+00:00',
                            },
                            'rate': 100500,
                            'tariff_zone': 'moscow',
                            'tariff_class': 'comfort',
                        },
                    ],
                },
            ],
            '55.733863',
            '37.590533',
        ),
    ],
)
@pytest.mark.config(
    SCHEDULE_DISPLAYING_DAYS={'__default__': 4},
    SMART_SUBVENTIONS_SETTINGS={
        'restrictions': ['activity', 'geoarea'],
        'ignored_restrictions': [],
        'clamp_activity': True,
    },
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS])
@pytest.mark.parametrize('use_admin', [False, True])
@pytest.mark.driver_tags_match(dbid='dbid1', uuid='driver1', tags=['tag_1'])
async def test_ssch_short_time_range(
        taxi_subvention_view,
        driver_authorizer,
        ssch,
        load_json,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        schedule_response,
        lat,
        lon,
        taxi_config,
        headers,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 90)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    ssch.set_schedules(schedule_response)

    lat_lon = {'lat': lat, 'lon': lon}

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 200
    assert ssch.calls['schedule'] == 1
    assert response.json() == {
        'items_for_map': [],
        'items_for_schedule': [
            {
                'slider_from_utc': '2020-09-14T11:00:00+0000',
                'slider_to_utc': '2020-09-15T11:00:00+0000',
                'date': '2020-09-14',
                'localized_date': 'Ближайшие сутки',
                'rules': [],
            },
            {
                'slider_from_utc': '2020-09-14T21:00:00+0000',
                'slider_to_utc': '2020-09-15T21:00:00+0000',
                'date': '2020-09-15',
                'localized_date': 'Вторник',
                'rules': [],
            },
            {
                'slider_from_utc': '2020-09-15T21:00:00+0000',
                'slider_to_utc': '2020-09-16T21:00:00+0000',
                'date': '2020-09-16',
                'localized_date': 'Среда',
                'rules': [],
            },
            {
                'slider_from_utc': '2020-09-16T21:00:00+0000',
                'slider_to_utc': '2020-09-17T21:00:00+0000',
                'date': '2020-09-17',
                'localized_date': 'Четверг',
                'rules': [],
            },
        ],
        'localized_required_for_bonuses': 'Требуется для получения доплат:',
        'localized_requirements': 'Требования для получения доплат:',
        'localized_steps': 'Этапы получения бонуса',
        'subvention_descriptions': [
            {
                'type': 'geo_booking',
                'title': 'Подробнее о гарантии',
                'text': (
                    'Необходимо быть в синей зоне ... Пусть гарантия'
                    ' 800_₽, заработок 600_₽'
                    ', бонус - 200_₽ (200_₽ + 600_₽ = 800_₽)'
                ),
            },
            {
                'type': 'guarantee',
                'title': 'Подробнее о доплате',
                'text': 'Минималка за заказ',
            },
        ],
    }


@pytest.mark.config(SUBVENTION_VIEW_PASS_503_ON_429=True)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('use_admin', [False, True])
async def test_got_429(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        mockserver,
        use_admin,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    bss.add_rules(load_json('billing_rules_merged_steps.json'))
    candidates.load_profiles(
        load_json('candidates_profiles_response_merged_steps.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    if use_admin:
        response = await request_admin_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    else:
        response = await request_schedule(
            taxi_subvention_view, lat_lon, headers,
        )
    assert response.status_code == 503


@pytest.mark.config(
    SUBVENTION_VIEW_ON_TOP_BRANDING_SETTINGS={
        'filter_by_branding': True,
        'omit_branding_in_response': True,
    },
)
@common.enable_single_ontop
@pytest.mark.now('2022-01-26T14:05:16+0300')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_branding_on_top(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        mockserver,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(
        load_json('candidates_profiles_response_merged_steps.json'),
    )
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _mock_rules_select(request):
        return {
            'rules': [
                {
                    'id': '1bea3e30-1156-4438-9e5b-2313453b6ab0',
                    'start': '2022-01-26T14:00:00+00:00',
                    'end': '2023-01-27T14:00:00+00:00',
                    'updated_at': '2022-01-26T13:28:13.085115+00:00',
                    'activity_points': 55,
                    'rates': [
                        {
                            'week_day': 'mon',
                            'start': '00:00',
                            'bonus_amount': '669',
                        },
                        {
                            'week_day': 'sun',
                            'start': '00:00',
                            'bonus_amount': '0',
                        },
                    ],
                    'budget_id': '895a8f6e-8d73-4f19-8c28-890151c63ba5',
                    'schedule_ref': '4d034d85-8393-48ea-b9ab-b6b9b2528d96',
                    'draft_id': '527975',
                    'zone': 'moscow',
                    'tariff_class': 'econom',
                    'rule_type': 'single_ontop',
                },
                {
                    'id': 'b5ebbc23-f838-41fd-b8c8-6a2eddac6291',
                    'start': '2022-01-18T13:00:00+00:00',
                    'end': '2022-02-19T13:00:00+00:00',
                    'updated_at': '2022-01-18T12:53:22.468451+00:00',
                    'branding_type': 'sticker',
                    'activity_points': 43,
                    'rates': [
                        {
                            'week_day': 'mon',
                            'start': '00:00',
                            'bonus_amount': '456',
                        },
                        {
                            'week_day': 'sun',
                            'start': '00:00',
                            'bonus_amount': '0',
                        },
                    ],
                    'budget_id': '209db600-1359-41ad-a15c-f8d111158915',
                    'schedule_ref': '4dc41583-aa28-43a6-a54a-ab505f2e46fa',
                    'draft_id': '522014',
                    'zone': 'moscow',
                    'tariff_class': 'econom',
                    'rule_type': 'single_ontop',
                },
            ],
        }

    lat_lon = {'lat': '55.733863', 'lon': '37.590533'}
    headers = DEFAULT_HEADERS

    response = await request_schedule(taxi_subvention_view, lat_lon, headers)
    assert response.status_code == 200
    assert _mock_rules_select.times_called == 1
    assert _mock_rules_select.next_call()['request'].json == {
        'limit': 1000,
        'rule_types': ['single_ontop'],
        'tags_constraint': {'has_tag': False},
        'tariff_classes': ['courier', 'express'],
        'time_range': {
            'end': '2022-02-02T11:05:16+00:00',
            'start': '2022-01-25T21:00:00+00:00',
        },
        'zones': ['moscow'],
        'branding': ['any_branding', 'sticker', 'no_full_branding'],
    }
    assert response.json() == load_json('expected_on_top_no_branding.json')
