import datetime
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


async def _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', '5926ff8fe5d69219ff4bf49a')
    activity.add_driver('5926ff8fe5d69219ff4bf49a', 90.0)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))


@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.config(HIDDEN_PERSONAL_SUBVENTION_COUNTRIES=['kzt'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('disable_personal_status', [True, False])
async def test_subvention_rules(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        driver_trackstory,
        activity,
        vehicles,
        taxi_config,
        disable_personal_status,
):
    bss.add_rules(load_json('bs_response.json'))
    taxi_config.set_values(
        {'SUBVENTION_VIEW_DISABLE_PERSONAL_STATUS': disable_personal_status},
    )
    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    if disable_personal_status:
        assert response.json() == {'items': []}
    else:
        response_data = response.json()

        expected_data = load_json('expected_response.json')
        assert response_data == expected_data

        assert bss.calls == 2
        assert bss.by_driver_calls == 1
        bs_requests = sorted(
            [json.loads(req) for req in bss.rules_select_call_params],
            key=lambda r: r['is_personal'],
        )
        assert bs_requests == [
            {
                'driver_branding': 'sticker',
                'is_personal': False,
                'limit': 1000,
                'status': 'enabled',
                'tariff_zone': 'moscow',
                'time_range': {
                    'end': '2020-06-23T13:10:01+00:00',
                    'start': '2020-06-23T13:10:00+00:00',
                },
                'types': ['goal'],
                'profile_tags': [],
            },
            {
                'drivers': [{'unique_driver_id': '5926ff8fe5d69219ff4bf49a'}],
                'is_personal': True,
                'limit': 1000,
                'status': 'enabled',
                'time_range': {
                    'end': '2020-06-23T13:10:01+00:00',
                    'start': '2020-06-23T13:10:00+00:00',
                },
                'types': ['goal'],
                'profile_tags': [],
            },
        ]


@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.config(HIDDEN_PERSONAL_SUBVENTION_COUNTRIES=['kzt'])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_by_driver_orders_completed(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        driver_trackstory,
        activity,
        vehicles,
):
    bss.add_rules(load_json('bs_response.json'))

    for rule_status in load_json('by_driver_response.json'):
        bss.add_by_driver_subvention(rule_status)

    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_response2.json')
    assert response_data == expected_data

    assert bss.by_driver_calls == 1
    by_driver_request = json.loads(bss.by_driver_call_params[0])
    by_driver_request['subvention_rule_ids'].sort()
    assert by_driver_request == {
        'time': '2020-06-23T13:10:00+00:00',
        'is_personal': True,
        'unique_driver_id': '5926ff8fe5d69219ff4bf49a',
        'subvention_rule_ids': [
            'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e7',
            'group_id/fcc640e3ccf238a514672df5202e82ae71bf2169',
        ],
    }


@pytest.mark.parametrize(
    'vtags,expected_rs_requests',
    [
        (
            None,
            [
                {
                    'driver_branding': 'sticker',
                    'is_personal': False,
                    'limit': 1000,
                    'status': 'enabled',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'end': '2020-06-23T13:10:01+00:00',
                        'start': '2020-06-23T13:10:00+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': [],
                },
                {
                    'drivers': [
                        {'unique_driver_id': '5926ff8fe5d69219ff4bf49a'},
                    ],
                    'is_personal': True,
                    'limit': 1000,
                    'status': 'enabled',
                    'time_range': {
                        'end': '2020-06-23T13:10:01+00:00',
                        'start': '2020-06-23T13:10:00+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': [],
                },
            ],
        ),
        (
            ['vtag_1', 'vtag_2'],
            [
                {
                    'driver_branding': 'sticker',
                    'is_personal': False,
                    'limit': 1000,
                    'status': 'enabled',
                    'tariff_zone': 'moscow',
                    'time_range': {
                        'end': '2020-06-23T13:10:01+00:00',
                        'start': '2020-06-23T13:10:00+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': ['vtag_1', 'vtag_2'],
                },
                {
                    'drivers': [
                        {'unique_driver_id': '5926ff8fe5d69219ff4bf49a'},
                    ],
                    'is_personal': True,
                    'limit': 1000,
                    'status': 'enabled',
                    'time_range': {
                        'end': '2020-06-23T13:10:01+00:00',
                        'start': '2020-06-23T13:10:00+00:00',
                    },
                    'types': ['goal'],
                    'profile_tags': ['vtag_1', 'vtag_2'],
                },
            ],
        ),
    ],
)
@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_virtual_tags(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        driver_trackstory,
        activity,
        vehicles,
        dmi,
        bss,
        vtags,
        expected_rs_requests,
):
    if vtags:
        dmi.set_virtual_tags(vtags)

    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    assert dmi.virtual_tags.times_called == 1

    assert bss.by_driver_calls == 0
    assert bss.calls == 2
    bs_requests = sorted(
        [json.loads(req) for req in bss.rules_select_call_params],
        key=lambda r: r['is_personal'],
    )
    assert bs_requests == expected_rs_requests


@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.config(
    HIDDEN_PERSONAL_SUBVENTION_COUNTRIES=['kzt'],
    SUBVENTION_VIEW_USE_V2_TAGS_MATCH_PROFILE=True,
    SUBVENTION_VIEW_EXTRA_INFO_FOR_NON_PERSONAL_RULES=True,
    RETURN_404_ON_NEAREST_ZONE_NOT_FOUND=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.parametrize(
    'is_position_provided,expected_response',
    [(False, 'expected_response2.json'), (True, 'expected_response3.json')],
)
async def test_non_personal_goal(
        taxi_subvention_view,
        driver_authorizer,
        driver_tags_mocks,
        load_json,
        mockserver,
        unique_drivers,
        vehicles,
        dmi,
        activity,
        experiments3,
        expected_response,
        is_position_provided,
):
    rules_select_checksum = 0
    by_driver_checksum = 0
    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )
    driver_tags_mocks.set_tags_info(
        'dbid1',
        'driver1',
        tags_info={'normal_tag': {'ttl': '2020-06-23T12:34:00+0300'}},
    )
    dmi.set_virtual_tags(['v_tag1', 'v_tag2'])
    await taxi_subvention_view.invalidate_caches()

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_position(request):
        data = json.loads(request.get_data())
        assert data['driver_id'] == 'dbid1_driver1'
        assert data['type'] == 'adjusted'
        if not is_position_provided:
            raise mockserver.TimeoutError()
        return {
            'position': {
                'lat': 55.751244,
                'lon': 37.618423,
                'timestamp': 1552003200,
            },
            'type': 'adjusted',
        }

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        nonlocal rules_select_checksum
        data = json.loads(request.get_data())
        is_personal = data['is_personal']
        rules_select_checksum += is_personal
        if is_personal:
            assert data == {
                'is_personal': True,
                'drivers': [{'unique_driver_id': '5926ff8fe5d69219ff4bf49a'}],
                'limit': 1000,
                'status': 'enabled',
                'profile_tags': ['v_tag1', 'v_tag2'],
                'time_range': {
                    'end': '2020-06-23T13:10:01+00:00',
                    'start': '2020-06-23T13:10:00+00:00',
                },
                'types': ['goal'],
            }
            return {'subventions': load_json('bs_response.json')}
        assert data == {
            'is_personal': False,
            'limit': 1000,
            'status': 'enabled',
            'driver_branding': 'sticker',
            'profile_tags': ['normal_tag', 'v_tag1', 'v_tag2'],
            'tariff_zone': 'moscow',
            'time_range': {
                'end': '2020-06-23T13:10:01+00:00',
                'start': '2020-06-23T13:10:00+00:00',
            },
            'types': ['goal'],
        }
        return {'subventions': load_json('bs_response_non_personal.json')}

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    def _get_by_driver(request):
        nonlocal by_driver_checksum
        data = json.loads(request.get_data())
        is_personal = data['is_personal']
        by_driver_checksum += is_personal
        data['subvention_rule_ids'].sort()
        if is_personal:
            assert data == {
                'is_personal': True,
                'time': '2020-06-23T13:10:00+00:00',
                'unique_driver_id': '5926ff8fe5d69219ff4bf49a',
                'subvention_rule_ids': [
                    'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e7',
                    'group_id/fcc640e3ccf238a514672df5202e82ae71bf2169',
                ],
            }

            return {'subventions': load_json('by_driver_response.json')}
        assert data == {
            'is_personal': False,
            'time': '2020-06-23T13:10:00+00:00',
            'unique_driver_id': '5926ff8fe5d69219ff4bf49a',
            'subvention_rule_ids': [
                'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e8',
                'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e9',
                'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3f1',
                'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3f2',
            ],
        }

        return {
            'subventions': load_json('by_driver_response_non_personal.json'),
        }

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    if is_position_provided:
        assert response.status_code == 200
        response_data = response.json()
        response_data['items'] = sorted(
            response_data['items'], key=lambda item: item['id'],
        )
        expected_data = load_json(expected_response)
        assert expected_data == response_data

        assert _mock_rules_select.times_called == 2
        assert rules_select_checksum == 1

        assert _get_by_driver.times_called == 2
        assert by_driver_checksum == 1

        assert _mock_position.times_called == 1
    else:
        assert response.status_code == 404
        assert _mock_position.times_called == 3
        assert _mock_rules_select.times_called == 0
        assert _get_by_driver.times_called == 0


@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.config(HIDDEN_PERSONAL_SUBVENTION_COUNTRIES=['kzt'])
@pytest.mark.config(SUBVENTION_VIEW_USE_BY_DRIVER_FALLBACK_CACHE=True)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_by_driver_fallback_cache(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        load_json,
        unique_drivers,
        mockserver,
        statistics,
        driver_trackstory,
        activity,
        vehicles,
):
    await taxi_subvention_view.invalidate_caches()

    bss.add_rules(load_json('bs_response.json'))

    for rule_status in load_json('by_driver_response.json'):
        bss.add_by_driver_subvention(rule_status)

    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    statistics.fallbacks = ['subvention_view.bs-by_driver.fallback']

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_response2.json')
    assert response_data == expected_data
    assert bss.by_driver_calls == 1
    assert mock_bs_by_driver.times_called == 0


@pytest.mark.config(SUBVENTION_VIEW_PERSONAL_MATCH_SMART_GOALS_EXP=True)
@pytest.mark.parametrize('fetch_smart_goals', (True, False))
@pytest.mark.now('2020-06-23T16:10:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_match_smart_goals_exp(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        unique_drivers,
        fetch_smart_goals,
        experiments3,
        mockserver,
        vehicles,
        load_json,
        activity,
        driver_trackstory,
):
    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )
    common.add_summary_exp3_config(
        experiments3, rules_settings=None, fetch_smart_goals=fetch_smart_goals,
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_position(request):
        data = json.loads(request.get_data())
        assert data['driver_id'] == 'dbid1_driver1'
        assert data['type'] == 'adjusted'
        return {
            'position': {
                'lat': 55.751244,
                'lon': 37.618423,
                'timestamp': 1552003200,
            },
            'type': 'adjusted',
        }

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}
    bss_calls = 0 if fetch_smart_goals else 2
    assert bss.calls == bss_calls


@pytest.mark.config(SUBVENTION_VIEW_PASS_503_ON_429=True)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_got_429(
        taxi_subvention_view,
        driver_authorizer,
        mockserver,
        unique_drivers,
        vehicles,
        load_json,
        activity,
        driver_trackstory,
):
    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 503


@pytest.mark.config(
    SUBVENTION_VIEW_PERSONAL_USE_QUERY_POSITIONS=True,
    SUBVENTION_VIEW_PERSONAL_MATCH_SMART_GOALS_EXP=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_query_position(
        taxi_subvention_view,
        driver_authorizer,
        bss,
        unique_drivers,
        mockserver,
        vehicles,
        load_json,
        activity,
        driver_trackstory,
):
    await _init_common_mocks(
        load_json, driver_authorizer, unique_drivers, activity, vehicles,
    )

    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def driver_trackstory_mock(request):
        response = {
            'results': [
                [
                    {
                        'source': 'Raw',
                        'position': {
                            'lat': 55.7737,
                            'lon': 37.4594,
                            'timestamp': int(
                                datetime.datetime.now().timestamp(),
                            ),
                        },
                    },
                ],
            ],
        }
        return mockserver.make_response(json.dumps(response), status=200)

    response = await taxi_subvention_view.get(
        '/v1/personal/status', headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}
    assert driver_trackstory_mock.times_called == 1
    assert driver_trackstory_mock.next_call()['request'].json == {
        'driver_ids': ['dbid1_driver1'],
        'max_age': 100,
        'prefered_sources': 'all',
        'parameterized_algorithm': {
            'max_retries': 1,
            'timeout': 30,
            'min_positions_required_count': -1,
            'algorithm': 'WithRetry',
        },
    }
