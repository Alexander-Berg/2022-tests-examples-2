# pylint: disable=C0302
import datetime
import enum
import json
import typing

import pytest

from . import common


DEFAULT_HEADER = {
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

VEHICLE_BINDING_FULL_BRANDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle2'},
        },
    ],
}

MOSCOW_POINT = [37.4594, 55.7737]
EKB_POINT = [60.606674, 56.838178]
MOSCOW_ZONE = 'moscow'
EKB_ZONE = 'ekb'

GEO_NODES = [
    {
        'name': 'br_kazakhstan',
        'name_en': 'Kazakhstan',
        'name_ru': 'Казахстан',
        'node_type': 'country',
        'parent_name': 'br_root',
        'tanker_key': 'name.br_kazakhstan',
    },
    {
        'name': 'br_almaty',
        'name_en': 'Almaty',
        'name_ru': 'Алматы',
        'node_type': 'agglomeration',
        'parent_name': 'br_kazakhstan',
        'tariff_zones': ['almaty', 'almaty_hub'],
        'tanker_key': 'name.br_almaty',
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
    },
    {
        'name': 'br_tsentralnyj_fo',
        'name_en': 'Central Federal District',
        'name_ru': 'Центральный ФО',
        'node_type': 'node',
        'parent_name': 'br_russia',
        'tanker_key': 'name.br_tsentralnyj_fo',
    },
    {
        'name': 'br_uralskij_fo',
        'name_en': 'Ural Federal District',
        'name_ru': 'Уральский ФО',
        'node_type': 'node',
        'parent_name': 'br_russia',
        'tanker_key': 'name.br_uralskij_fo',
    },
    {
        'name': 'br_sverdlovskaja_obl',
        'name_en': 'Sverdlovsk Region',
        'name_ru': 'Свердловская область',
        'node_type': 'node',
        'parent_name': 'br_uralskij_fo',
        'tanker_key': 'name.br_sverdlovskaja_obl',
    },
    {
        'name': 'br_ekaterinburg',
        'name_en': 'Ekaterinburg',
        'name_ru': 'Екатеринбург',
        'node_type': 'agglomeration',
        'parent_name': 'br_sverdlovskaja_obl',
        'tariff_zones': ['ekb'],
        'tanker_key': 'name.br_ekaterinburg',
    },
]


def get_exp_config(load_json, exp_name, consumer):
    config = load_json('generic_exp3_config.json')

    config[0]['match']['consumers'] = [{'name': consumer}]
    config[0]['match']['name'] = exp_name

    return config


class HandleType(enum.Enum):
    GET = 1
    POST = 2


def _check_404_response(response) -> None:
    assert response.status_code == 404
    data = response.json()
    assert data['code'] == 'NEAREST_ZONE_NOT_FOUND'
    assert data['message'] == 'nearest zone not found'
    assert response.headers['X-YaTaxi-Error-Code'] == data['code']


async def _init_mocks(
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))


async def _perform_call(
        taxi_subvention_view,
        handle_type: HandleType,
        handle_path: str,
        handle_params: typing.Mapping[str, str],
):
    if handle_type is HandleType.GET:
        return await taxi_subvention_view.get(
            handle_path, params=handle_params, headers=DEFAULT_HEADER,
        )
    if handle_type is HandleType.POST:
        return await taxi_subvention_view.post(
            handle_path, json=handle_params, headers=DEFAULT_HEADER,
        )
    assert False


def _get_profiles_by_zone():
    profiles_msk = {
        'drivers': [
            {
                'classes': ['econom', 'comfort', 'vip'],
                'dbid': 'dbid1',
                'position': [0.0, 0.0],
                'uuid': 'driver1',
            },
        ],
    }
    profiles_ekb = {
        'drivers': [
            {
                'classes': ['econom', 'comfort', 'comfortplus', 'vip'],
                'dbid': 'dbid1',
                'position': [0.0, 0.0],
                'uuid': 'driver1',
            },
        ],
    }
    return {'moscow': profiles_msk, 'ekb': profiles_ekb}


@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params,expected_delay',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'lon': 37.618423,
                'lat': 55.751244,
                'from': '2020-09-23',
                'to': '2020-09-24',
                'types': ['daily_guarantee'],
            },
            66,
        ),
        (
            HandleType.GET,
            '/v1/personal/status',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
            77,
        ),
        (
            HandleType.GET,
            '/v1/schedule',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
            88,
        ),
        (
            HandleType.GET,
            '/v1/status',
            {
                'park_id': 'dbid1',
                'lat': '55.733863',
                'lon': '37.590533',
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
            },
            99,
        ),
        (
            HandleType.POST,
            '/driver/v1/subvention_view/v2/status'
            '?park_id=dbid1&lat=55.733863&lon=37.590533',
            {
                'subventions_id': ['_id/subvention_1'],
                'order_id': 'non_existing_order_id',
            },
            99,
        ),
    ],
)
@pytest.mark.config(
    POLLING_DELAY={
        '__default__': 22,
        '/v1/nmfg/status': 66,
        '/v1/personal/status': 77,
        '/v1/schedule': 88,
        '/v1/status': 99,
    },
    TAXIMETER_POLLING_SWITCHER={'__default__': 'new'},
    TAXIMETER_POLLING_MANAGER={
        '__default__': {
            'policy_groups': {'__default__': {'full': 22, 'background': 0}},
        },
        '/v1/nmfg/status': {
            'policy_groups': {'__default__': {'full': 66, 'background': 0}},
        },
        '/v1/personal/status': {
            'policy_groups': {'__default__': {'full': 77, 'background': 0}},
        },
        '/v1/schedule': {
            'policy_groups': {'__default__': {'full': 88, 'background': 0}},
        },
        '/v1/status': {
            'policy_groups': {'__default__': {'full': 99, 'background': 0}},
        },
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_polling_policy_headers(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        expected_delay,
        driver_trackstory,
):
    await _init_mocks(
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
    )
    response = await _perform_call(
        taxi_subvention_view, handle_type, handle_path, handle_params,
    )

    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == str(expected_delay)
    assert response.headers[
        'X-Polling-Power-Policy'
    ] == common.make_polling_policy(expected_delay)


@pytest.mark.now('2020-07-26T12:00:00+0000')
@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params,expected_requests',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'lon': 37.618423,
                'lat': 55.751244,
                'from': '2020-07-26',
                'to': '2020-08-03',
                'types': ['daily_guarantee'],
            },
            [
                {
                    'tariff_zone': 'moscow',
                    'status': 'enabled',
                    'time_range': {
                        'start': '2020-07-25T21:00:00+00:00',
                        'end': '2020-08-02T21:00:00+00:00',
                    },
                    'types': ['daily_guarantee'],
                    'is_personal': False,
                    'profile_tags': [],
                    'driver_branding': 'sticker',
                    'profile_tariff_classes': ['comfort', 'econom', 'vip'],
                    'order_tariff_classes': ['comfort', 'econom', 'vip'],
                    'limit': 1000,
                },
            ],
        ),
        (
            HandleType.GET,
            '/v1/personal/status',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
            [
                {
                    'driver_branding': 'sticker',
                    'is_personal': False,
                    'limit': 1000,
                    'status': 'enabled',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'start': '2020-07-26T12:00:00+00:00',
                        'end': '2020-07-26T12:00:01+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': [],
                },
                {
                    'drivers': [
                        {'unique_driver_id': '59648321ea19f1bacf079756'},
                    ],
                    'is_personal': True,
                    'limit': 1000,
                    'status': 'enabled',
                    'time_range': {
                        'start': '2020-07-26T12:00:00+00:00',
                        'end': '2020-07-26T12:00:01+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': [],
                },
            ],
        ),
        (
            HandleType.GET,
            '/v1/schedule',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
            [
                {
                    'tariff_zone': 'moscow',
                    'status': 'enabled',
                    'time_range': {
                        'start': '2020-07-26T12:00:00+00:00',
                        'end': '2020-08-02T12:00:00+00:00',
                    },
                    'types': ['geo_booking', 'goal'],
                    'is_personal': False,
                    'profile_tags': [],
                    'driver_branding': 'sticker',
                    'limit': 1000,
                },
            ],
        ),
        (
            HandleType.GET,
            '/v1/status',
            {
                'park_id': 'dbid1',
                'lat': '55.733863',
                'lon': '37.590533',
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
            },
            [
                {
                    'rule_ids': ['_id/subvention_1'],
                    'tariff_zone': 'moscow',
                    'status': 'enabled',
                    'limit': 1,
                },
            ],
        ),
        (
            HandleType.POST,
            '/driver/v1/subvention_view/v2/status'
            '?park_id=dbid1&lat=55.733863&lon=37.590533',
            {
                'subventions_id': ['_id/subvention_1'],
                'order_id': 'non_existing_order_id',
            },
            [
                {
                    'rule_ids': ['_id/subvention_1'],
                    'tariff_zone': 'moscow',
                    'status': 'enabled',
                    'limit': 1,
                },
            ],
        ),
    ],
)
@pytest.mark.config(USE_GEOINDEX={'to_find_nearest_zone': True})
@pytest.mark.parametrize('enable_bs_cache', [True, False])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_bs_request(
        taxi_subvention_view,
        load_json,
        taxi_config,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        bss,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        expected_requests,
        enable_bs_cache,
        driver_trackstory,
):
    if enable_bs_cache:
        params_begin = handle_path.find('?')
        handle_name = (
            handle_path if params_begin == -1 else handle_path[:params_begin]
        )
        taxi_config.set_values(dict(HANDLES_USING_RS_CACHE=[handle_name]))

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    response = None
    if handle_type is HandleType.GET:
        response = await taxi_subvention_view.get(
            handle_path, params=handle_params, headers=DEFAULT_HEADER,
        )
    elif handle_type is HandleType.POST:
        response = await taxi_subvention_view.post(
            handle_path, json=handle_params, headers=DEFAULT_HEADER,
        )
    else:
        assert False

    assert response.status_code == 200
    if not enable_bs_cache:
        assert bss.calls == len(expected_requests)
        if len(expected_requests) > 1:
            assert (
                sorted(
                    (
                        json.loads(param)
                        for param in bss.rules_select_call_params
                    ),
                    key=lambda item: item['is_personal'],
                )
                == expected_requests
            )
        else:
            assert (
                json.loads(bss.rules_select_call_params[0])
                == expected_requests[0]
            )


@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params,' 'expected_profile_tags',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'lon': 37.618423,
                'lat': 55.751244,
                'from': '2020-09-23',
                'to': '2020-09-24',
                'types': ['daily_guarantee'],
            },
            ['normal_tag', 'v_tag1', 'v_tag2'],
        ),
        (
            HandleType.GET,
            '/v1/schedule',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
            ['normal_tag', 'v_tag1', 'v_tag2'],
        ),
    ],
)
@pytest.mark.config(USE_GEOINDEX={'to_find_nearest_zone': True})
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_virtual_tags(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        driver_tags_mocks,
        bss,
        dmi,
        experiments3,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        expected_profile_tags,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    response = None
    if handle_type is HandleType.GET:
        response = await taxi_subvention_view.get(
            handle_path, params=handle_params, headers=DEFAULT_HEADER,
        )
    elif handle_type is HandleType.POST:
        response = await taxi_subvention_view.post(
            handle_path, json=handle_params, headers=DEFAULT_HEADER,
        )
    else:
        assert False

    assert response.status_code == 200

    assert bss.calls == 1
    assert (
        json.loads(bss.rules_select_call_params[0])['profile_tags']
        == expected_profile_tags
    )


@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'lon': 37.618423,
                'lat': 55.751244,
                'from': '2020-09-23',
                'to': '2020-09-24',
                'types': ['daily_guarantee'],
            },
        ),
        (
            HandleType.GET,
            '/v1/schedule',
            {'park_id': 'dbid1', 'lat': '55.733863', 'lon': '37.590533'},
        ),
    ],
)
@pytest.mark.config(USE_GEOINDEX={'to_find_nearest_zone': True})
@pytest.mark.parametrize('topics', [None, [], ['efficency'], ['eff', 'test']])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_tags_topics(
        taxi_subvention_view,
        taxi_config,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        driver_tags_mocks,
        bss,
        dmi,
        experiments3,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        topics,
):
    if topics:
        taxi_config.set_values(dict(TAGS_TOPICS={'topics': topics}))

    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    response = None
    if handle_type is HandleType.GET:
        response = await taxi_subvention_view.get(
            handle_path, params=handle_params, headers=DEFAULT_HEADER,
        )
    elif handle_type is HandleType.POST:
        response = await taxi_subvention_view.post(
            handle_path, json=handle_params, headers=DEFAULT_HEADER,
        )
    else:
        assert False

    assert response.status_code == 200

    assert driver_tags_mocks.v1_match_profile.times_called == 1
    expected_tags_request = {'dbid': 'dbid1', 'uuid': 'driver1'}
    if topics:
        expected_tags_request['topics'] = topics
    assert (
        json.loads(
            driver_tags_mocks.v1_match_profile.next_call()[
                'request'
            ].get_data(),
        )
        == expected_tags_request
    )


@pytest.mark.parametrize('return_404', (None, False, True))
@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params,expected_not_found_code_old,'
    'expected_not_found_code_new',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'lon': 1.0,
                'lat': 1.0,
                'from': '2020-09-23',
                'to': '2020-09-24',
                'types': ['daily_guarantee'],
            },
            200,
            404,
        ),
        (
            HandleType.GET,
            '/v1/personal/status',
            {'park_id': 'dbid1', 'lat': 1.0, 'lon': 1.0},
            200,
            200,
        ),
        (
            HandleType.GET,
            '/v1/schedule',
            {'park_id': 'dbid1', 'lat': 1.0, 'lon': 1.0},
            500,
            404,
        ),
        (
            HandleType.GET,
            '/v1/status',
            {
                'park_id': 'dbid1',
                'lat': 1.0,
                'lon': 1.0,
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
            },
            500,
            404,
        ),
        (
            HandleType.POST,
            '/driver/v1/subvention_view/v2/status'
            '?park_id=dbid1&lat=1.0&lon=1.0',
            {
                'subventions_id': ['_id/subvention_1'],
                'order_id': 'non_existing_order_id',
            },
            500,
            404,
        ),
    ],
)
@pytest.mark.config(USE_GEOINDEX={'to_find_nearest_zone': True})
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_nearest_zone_not_found(
        taxi_subvention_view,
        load_json,
        candidates,
        driver_authorizer,
        unique_drivers,
        activity,
        taxi_config,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        return_404,
        expected_not_found_code_old,
        expected_not_found_code_new,
        driver_trackstory,
):
    if return_404 is not None:
        taxi_config.set_values(
            dict(RETURN_404_ON_NEAREST_ZONE_NOT_FOUND=return_404),
        )

    await _init_mocks(
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
    )
    response = await _perform_call(
        taxi_subvention_view, handle_type, handle_path, handle_params,
    )

    if return_404:
        assert response.status_code == expected_not_found_code_new
        if expected_not_found_code_new == 404:
            _check_404_response(response)
    else:
        assert response.status_code == expected_not_found_code_old


@pytest.mark.parametrize(
    'handle_type,handle_path,handle_params',
    [
        (
            HandleType.POST,
            '/v1/nmfg/status',
            {
                'from': '2020-09-23',
                'to': '2020-09-24',
                'types': ['daily_guarantee'],
            },
        ),
        (HandleType.GET, '/v1/personal/status', {'park_id': 'dbid1'}),
        (HandleType.GET, '/v1/schedule', {'park_id': 'dbid1'}),
        (
            HandleType.GET,
            '/v1/status',
            {
                'park_id': 'dbid1',
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
            },
        ),
        (
            HandleType.POST,
            '/driver/v1/subvention_view/v2/status?park_id=dbid1',
            {
                'subventions_id': ['_id/subvention_1'],
                'order_id': 'non_existing_order_id',
            },
        ),
        (
            HandleType.GET,
            '/driver/v1/subvention-view/v1/view/summary',
            {'tz': 'Europe/Moscow'},
        ),
        (  # skipping /goals/details case due to similarity
            HandleType.GET,
            '/driver/v1/subvention-view/v1/view/goals',
            {'tz': 'Europe/Moscow', 'date': '2020-09-23'},
        ),
    ],
)
@pytest.mark.parametrize(
    [
        'candidates_request_mode',
        'is_position_provided',
        'is_query_position_provided',
        'is_position_changed',
    ],
    [
        ('by_driver', True, True, False),
        ('by_driver', False, True, False),
        ('by_driver_fetch_query_zone_comparing', True, True, False),
        ('by_driver_fetch_query_zone_comparing', False, True, False),
        ('by_driver_by_query_zone_comparing', True, True, False),
        ('by_driver_by_query_zone_comparing', True, True, True),
        ('by_driver_by_query_zone_comparing', True, False, False),
        ('by_driver_by_query_zone_comparing', False, True, False),
        ('by_query_zone_comparing', True, True, False),
        ('by_query_zone_comparing', True, True, True),
        ('by_query_zone_comparing', False, True, False),
        ('by_query_zone_comparing', True, False, False),
        ('by_query_zone', True, True, False),
        ('by_query_zone', True, True, True),
        ('by_query_zone', False, True, False),
        ('by_query_zone', True, False, False),
    ],
)
@pytest.mark.config(
    USE_GEOINDEX={'to_find_nearest_zone': True},
    SUBVENTION_VIEW_GOALS_FETCH_OLD_PERSONAL_GOALS=True,
    SUBVENTION_VIEW_PERSONAL_MATCH_SMART_GOALS_EXP=True,
    RETURN_404_ON_NEAREST_ZONE_NOT_FOUND=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(GEO_NODES)
async def test_fetch_tariff_classes_from_candidates(
        taxi_subvention_view,
        taxi_subvention_view_monitor,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        experiments3,
        vehicles,
        handle_type,
        handle_path,
        handle_params,
        mockserver,
        candidates_request_mode,
        is_position_changed,
        bsx,
        taxi_config,
        is_position_provided,
        is_query_position_provided,
):
    handle_params['lon'] = MOSCOW_POINT[0]
    handle_params['lat'] = MOSCOW_POINT[1]
    if handle_path == '/driver/v1/subvention_view/v2/status?park_id=dbid1':
        handle_path = (
            f'{handle_path}&lon={MOSCOW_POINT[0]}&lat={MOSCOW_POINT[1]}'
        )

    common.add_candidates_request_mode_exp(
        experiments3, candidates_request_mode,
    )

    def dts_error():
        return mockserver.make_response(
            json={'message': 'Driver not found'}, status=404,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def dts_position_mock(request):
        data = request.json
        assert data['driver_id'] == 'dbid1_driver1'
        assert data['type'] == 'adjusted'
        if not is_position_provided:
            return dts_error()
        return {
            'position': {
                'lon': MOSCOW_POINT[0],
                'lat': MOSCOW_POINT[1],
                'timestamp': 1552003200,
            },
            'type': 'adjusted',
        }

    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    last_good_position = EKB_POINT if is_position_changed else MOSCOW_POINT

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def dts_query_position_mock(request):
        if not is_query_position_provided:
            return dts_error()
        response = {
            'results': [
                [
                    {
                        'source': 'Raw',
                        'position': {
                            'lon': last_good_position[0],
                            'lat': last_good_position[1],
                            'timestamp': int(
                                datetime.datetime.now().timestamp(),
                            ),
                        },
                    },
                ],
            ],
        }
        return mockserver.make_response(json.dumps(response), status=200)

    await _init_mocks(
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
    )

    candidates.load_profiles_by_zone(_get_profiles_by_zone())

    await taxi_subvention_view.tests_control(reset_metrics=True)

    response = await _perform_call(
        taxi_subvention_view, handle_type, handle_path, handle_params,
    )

    is_position_call_expected = handle_path in (
        '/v1/personal/status',
        '/driver/v1/subvention-view/v1/view/summary',
        '/driver/v1/subvention-view/v1/view/goals',
        '/driver/v1/subvention-view/v1/view/goals/details',
    )
    is_current_position_required = candidates_request_mode in (
        'by_driver',
        'by_driver_fetch_query_zone_comparing',
        'by_driver_by_query_zone_comparing',
    )
    is_query_position_required = candidates_request_mode in (
        'by_query_zone_comparing',
        'by_query_zone',
    )
    is_query_zone_fetch_required = candidates_request_mode in (
        'by_driver_fetch_query_zone_comparing',
        'by_driver_by_query_zone_comparing',
        'by_query_zone_comparing',
        'by_query_zone',
    )
    is_by_driver_request = candidates_request_mode in (
        'by_driver',
        'by_driver_fetch_query_zone_comparing',
        'by_driver_by_query_zone_comparing',
        'by_query_zone_comparing',
    )
    is_by_zone_request = candidates_request_mode in (
        'by_driver_by_query_zone_comparing',
        'by_query_zone_comparing',
        'by_query_zone',
    )
    is_classes_comparing = candidates_request_mode in (
        'by_driver_by_query_zone_comparing',
        'by_query_zone_comparing',
    )

    if (
            not is_position_provided
            and is_position_call_expected
            and is_current_position_required
    ) or (not is_query_position_provided and is_query_position_required):
        assert response.status_code == 404
    else:
        assert response.status_code == 200

    if is_position_call_expected:
        dts_position_mock.times_calles = 1
    else:
        dts_position_mock.times_calles = 0

    if response.status_code == 200:
        if handle_path == '/v1/personal/status':
            assert candidates.mock_profiles.times_called == 0
        else:
            if is_query_zone_fetch_required:
                assert dts_query_position_mock.times_called == 1

            if is_classes_comparing and is_query_position_provided:
                assert candidates.mock_profiles.times_called == 2
            else:
                assert candidates.mock_profiles.times_called == 1

            if is_by_driver_request:
                candidates_request = json.loads(
                    candidates.mock_profiles.next_call()['request'].get_data(),
                )
                assert candidates_request == {
                    'data_keys': ['classes', 'payment_methods'],
                    'driver_ids': [{'dbid': 'dbid1', 'uuid': 'driver1'}],
                }

            expect_by_zone_request = is_by_zone_request and (
                is_query_position_required or is_query_position_provided
            )
            if expect_by_zone_request:
                candidates_request = json.loads(
                    candidates.mock_profiles.next_call()['request'].get_data(),
                )
                assert candidates_request == {
                    'data_keys': ['classes', 'payment_methods'],
                    'driver_ids': [{'dbid': 'dbid1', 'uuid': 'driver1'}],
                    'zone_id': (
                        EKB_ZONE if is_position_changed else MOSCOW_ZONE
                    ),
                }


@pytest.mark.config(
    SUBVENTION_VIEW_USE_DRIVER_TAGS_CACHE=True,
    USE_GEOINDEX={'to_find_nearest_zone': True},
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_driver_tags_cache(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        driver_tags_mocks,
        bss,
        dmi,
        experiments3,
        vehicles,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])

    handle_params = {
        'lon': 37.618423,
        'lat': 55.751244,
        'from': '2020-09-23',
        'to': '2020-09-24',
        'types': ['daily_guarantee'],
    }

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status', json=handle_params, headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200

    expected_tags = ['normal_tag', 'v_tag1', 'v_tag2']
    assert driver_tags_mocks.v1_match_profile.times_called == 1
    assert bss.calls == 1
    assert (
        json.loads(bss.rules_select_call_params[0])['profile_tags']
        == expected_tags
    )

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status', json=handle_params, headers=DEFAULT_HEADER,
    )

    assert driver_tags_mocks.v1_match_profile.times_called == 1

    assert bss.calls == 2
    assert (
        json.loads(bss.rules_select_call_params[0])['profile_tags']
        == expected_tags
    )


@pytest.mark.config(
    SUBVENTION_VIEW_DRIVER_TAGS_DMP_CACHE_SETTINGS={
        'expiration_time_seconds': 0,
        'max_size': 5000,
        'dmp_timeout_ms': 1,
    },
    SUBVENTION_VIEW_USE_DRIVER_TAGS_CACHE=True,
    USE_GEOINDEX={'to_find_nearest_zone': True},
)
@pytest.mark.parametrize('empty_fallback_cache', [False, True])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_driver_tags_cache_fallback(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        driver_tags_mocks,
        bss,
        dmi,
        experiments3,
        vehicles,
        statistics,
        mockserver,
        empty_fallback_cache,
):
    driver_authorizer.set_session('dbid1', 'test_session', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '59648321ea19f1bacf079756')
    activity.add_driver('59648321ea19f1bacf079756', 88.0)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['normal_tag'])
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])
    statistics.fallbacks = ['subvention_view.driver-tags-dmp.fallback']

    handle_params = {
        'lon': 37.618423,
        'lat': 55.751244,
        'from': '2020-09-23',
        'to': '2020-09-24',
        'types': ['daily_guarantee'],
    }

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status', json=handle_params, headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200

    expected_tags = ['normal_tag', 'v_tag1', 'v_tag2']
    assert driver_tags_mocks.v1_match_profile.times_called == 1
    assert bss.calls == 1
    assert (
        json.loads(bss.rules_select_call_params[0])['profile_tags']
        == expected_tags
    )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_v1_match_profile(request):
        return mockserver.make_response(status=500)

    if empty_fallback_cache:
        await taxi_subvention_view.invalidate_caches()

    response = await taxi_subvention_view.post(
        f'/v1/nmfg/status', json=handle_params, headers=DEFAULT_HEADER,
    )

    if empty_fallback_cache:
        assert response.status_code == 500
    else:
        assert response.status_code == 200

        assert driver_tags_mocks.v1_match_profile.times_called == 1

        assert bss.calls == 2
        assert (
            json.loads(bss.rules_select_call_params[0])['profile_tags']
            == expected_tags
        )
