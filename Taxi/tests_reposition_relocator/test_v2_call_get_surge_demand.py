# pylint: disable=import-only-modules
import copy
import json

import pytest

from .utils import format_execution_timestamp

NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.surge_heatmap(
    cell_size_meter=250.0,
    envelope={'br': [38.619049, 55.971148], 'tl': [37.251251, 55.485152]},
    values=[
        {'x': 0, 'y': 1, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 20, 'surge': 3, 'weight': 0.0},
        {'x': 1, 'y': 2, 'surge': 5.5, 'weight': 0.0},
        {
            'x': 1,
            'y': 18,
            'surge': 2.1,
            'weight': 0.0,
            'pin_info': {'pins_count': 10, 'avg_cost': 0, 'cost_count': 0},
        },
    ],
)
@pytest.mark.geoareas(
    filename='geoareas_moscow.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.parametrize('use_subventions', [False, True])
@pytest.mark.parametrize('excluded_geoareas', [None, ['moscow']])
async def test_put(
        taxi_reposition_relocator,
        heatmap_storage_fixture,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        use_subventions,
        excluded_geoareas,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    patched_request = load_json('request.json')
    if use_subventions:
        del patched_request['data']['options']['geoareas']
        patched_request['data']['options']['subvention_geoareas'] = [
            'moscow-driver-fix',
        ]
    elif excluded_geoareas:
        patched_request['data']['options'][
            'excluded_geoareas'
        ] = excluded_geoareas

    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected = load_json('results.json')
    for request in expected['data']:
        if use_subventions:
            request['request_info']['geoarea'] = {
                'name': 'moscow-driver-fix',
                'type': 'subvention_zone',
            }

    if not use_subventions and excluded_geoareas:
        expected['data'] = []

    actual = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in actual['data']:
        assert 'request_info' in request
        del request['request_info']['request_id']

    assert expected == actual


@pytest.mark.surge_heatmap(
    cell_size_meter=250.0,
    envelope={'br': [38.619049, 55.971148], 'tl': [37.251251, 55.485152]},
    values=[
        {'x': 0, 'y': 1, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 20, 'surge': 3, 'weight': 0.0},
        {'x': 1, 'y': 2, 'surge': 5.5, 'weight': 0.0},
        {
            'x': 1,
            'y': 18,
            'surge': 2.1,
            'weight': 0.0,
            'pin_info': {'pins_count': 10, 'avg_cost': 0, 'cost_count': 0},
        },
    ],
)
@pytest.mark.geoareas(
    filename='geoareas_moscow.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.now('2119-01-02T00:00:02+0000')
@pytest.mark.config(REPOSITION_RELOCATOR_SURGE_MAP_TTL=1)
async def test_put_outdated_surge_map(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    patched_request = load_json('request.json')
    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'Exception: No relevant surge maps were obtained',
            'message': 'Operation search/get_surge_demand runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.surge_heatmap(
    cell_size_meter=250.0,
    envelope={'br': [38.619049, 55.971148], 'tl': [37.251251, 55.485152]},
    values=[
        {'x': 0, 'y': 1, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 20, 'surge': 3, 'weight': 0.0},
        {'x': 1, 'y': 2, 'surge': 5.5, 'weight': 0.0},
        {
            'x': 1,
            'y': 18,
            'surge': 2.1,
            'weight': 0.0,
            'pin_info': {'pins_count': 10, 'avg_cost': 0, 'cost_count': 0},
        },
    ],
)
@pytest.mark.config(REPOSITION_RELOCATOR_PARALLEL_REQUEST_PROCESSING_COUNT=6)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_multiple_requests(
        taxi_reposition_relocator,
        heatmap_storage_fixture,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    request = load_json('request.json')
    request['data']['options']['geoareas'].append('moscow_activation')
    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected = load_json('results.json')
    new_data = copy.deepcopy(expected['data'][0])
    expected['data'].append(new_data)
    expected['data'][1]['request_info']['geoarea'][
        'name'
    ] = 'moscow_activation'
    expected['data'].sort(key=lambda x: x['request_info']['geoarea']['name'])

    actual = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert (
        actual['data'][0]['request_info']['request_id']
        != actual['data'][1]['request_info']['request_id']
    )
    for request in actual['data']:
        assert 'request_info' in request
        del request['request_info']['request_id']
    actual['data'].sort(key=lambda x: x['request_info']['geoarea']['name'])

    assert expected == actual


@pytest.mark.filldb()
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_missing_output(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    missing_type = 'outputs'
    patched_request = load_json('request.json')
    patched_request['data'][missing_type] = {}

    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    expected_details = (
        'Exception: Operation required outputs: '
        '[results], missing: [results]'
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': expected_details,
            'message': 'Operation search/get_surge_demand runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.filldb()
async def test_forbidden(
        taxi_reposition_relocator, pgsql, mockserver, load_json,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'any',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'any'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'User is not allowed to perform this action',
            'message': 'Unauthorized user',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.nofilldb()
@pytest.mark.config(REPOSITION_RELOCATOR_PROCESSOR_ENABLED=False)
async def test_disabled(taxi_reposition_relocator, load_json):
    response = await taxi_reposition_relocator.put(
        'v2/call/echo/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'Switcher is off in config',
            'message': 'Processor is disabled',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.surge_heatmap(
    cell_size_meter=250.0,
    envelope={'br': [38.619049, 55.971148], 'tl': [37.251251, 55.485152]},
    values=[
        {'x': 0, 'y': 1, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 20, 'surge': 3, 'weight': 0.0},
        {'x': 1, 'y': 2, 'surge': 5.5, 'weight': 0.0},
        {
            'x': 1,
            'y': 18,
            'surge': 2.1,
            'weight': 0.0,
            'pin_info': {'pins_count': 10, 'avg_cost': 0, 'cost_count': 0},
        },
    ],
)
@pytest.mark.geoareas(
    filename='geoareas_moscow.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.parametrize('fltr', [False, True])
async def test_surge_points_filtration(
        taxi_reposition_relocator,
        heatmap_storage_fixture,
        mockserver,
        taxi_config,
        load_json,
        now,
        mds_s3_storage,
        fltr,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    taxi_config.set_values(
        {
            'SURGE_FIXED_POINTS_FROM_ADMIN': False,
            'SURGE_SAMPLES_POSITIONS': [[37.2511, 55.4867]],
        },
    )

    request = load_json('request.json')
    request['data']['options']['use_surge_points_as_destinations'] = fltr
    del request['data']['options']['geoareas']
    request['data']['options']['subvention_geoareas'] = ['moscow-driver-fix']

    response = await taxi_reposition_relocator.put(
        'v2/call/get_surge_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected = load_json('results.json')
    expected['data'][0]['request_info']['geoarea'] = {
        'name': 'moscow-driver-fix',
        'type': 'subvention_zone',
    }
    if fltr:
        del expected['data'][0]['destinations']['2']
        del expected['data'][0]['destinations_demands']['2']
        del expected['data'][0]['demands']['2']

    actual = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in actual['data']:
        assert 'request_info' in request
        del request['request_info']['request_id']

    assert expected == actual
