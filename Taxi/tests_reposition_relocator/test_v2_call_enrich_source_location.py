# pylint: disable=import-only-modules
import copy
import json

import pytest

from .utils import format_execution_timestamp


NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.surge_heatmap(
    cell_size_meter=5000.0,
    envelope={'br': [37.654000, 55.734000], 'tl': [37.627000, 55.757000]},
    values=[
        {'x': 0, 'y': 0, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 1, 'surge': 2, 'weight': 0.0},
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put(
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

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
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

    expected_results = load_json('results.json')
    expected_results['data'][0]['demands_sources']['2'].sort()

    results = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    results['data'][0]['demands_sources']['2'].sort()

    assert results == expected_results


@pytest.mark.surge_heatmap(
    cell_size_meter=5000.0,
    envelope={'br': [37.654000, 55.734000], 'tl': [37.627000, 55.757000]},
    values=[
        {'x': 0, 'y': 0, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 1, 'surge': 2, 'weight': 0.0},
    ],
)
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(REPOSITION_RELOCATOR_PARALLEL_REQUEST_PROCESSING_COUNT=6)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
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

    request_cnt = 25
    requests = load_json('requests.json')

    for i in range(1, request_cnt):
        new_data = copy.deepcopy(requests['data'][0])
        new_data['request_info']['request_id'] += '_' + str(i)
        requests['data'].append(new_data)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(requests).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
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

    expected_results = load_json('results.json')
    for i in range(1, request_cnt):
        new_data = copy.deepcopy(expected_results['data'][0])
        new_data['request_info']['request_id'] += '_' + str(i)
        expected_results['data'].append(new_data)

    results = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for i in range(request_cnt):
        results['data'][i]['demands_sources']['2'].sort()
        expected_results['data'][i]['demands_sources']['2'].sort()

    assert results == expected_results


@pytest.mark.nofilldb()
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_empty_surge_map(
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

    requests = load_json('requests.json')
    requests['data'][0]['demands']['1']['descriptor']['descriptor_value'][
        'category'
    ] = 'comfort'
    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(requests).encode('utf-8'),
    )

    request = load_json('request.json')
    request['data']['options']['default_category'] = 'nonexistent_category'

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
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

    expected_results = load_json('results_empty_surge.json')
    expected_results['data'][0]['demands_sources']['2'].sort()

    results = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    results['data'][0]['demands_sources']['2'].sort()

    assert results == expected_results


@pytest.mark.surge_heatmap(
    cell_size_meter=5000.0,
    envelope={'br': [37.654000, 55.734000], 'tl': [37.627000, 55.757000]},
    values=[
        {'x': 0, 'y': 0, 'surge': 0.5, 'weight': 0.0},
        {'x': 0, 'y': 1, 'surge': 2, 'weight': 0.0},
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2119-01-02T00:00:02+0000')
@pytest.mark.config(REPOSITION_RELOCATOR_SURGE_MAP_TTL=1)
async def test_put_outdated_surge_map(
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

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'Exception: No relevant surge maps were obtained',
            'message': (
                'Operation enrich/enrich_source_location runtime failure'
            ),
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


@pytest.mark.filldb()
@pytest.mark.parametrize('missing_type', ['inputs', 'outputs'])
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_missing_io(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        missing_type,
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
    patched_request['data'][missing_type] = {}

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    expected_details = ''
    if missing_type == 'inputs':
        expected_details = (
            'Exception: Operation required inputs: '
            '[requests], missing: [requests]'
        )
    else:
        expected_details = (
            'Exception: Operation required outputs: '
            '[results], missing: [results]'
        )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': expected_details,
            'message': (
                'Operation enrich/enrich_source_location runtime failure'
            ),
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
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
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
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(REPOSITION_RELOCATOR_PROCESSOR_ENABLED=False)
async def test_disabled(taxi_reposition_relocator, load_json, now):
    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_source_location/' + NIRVANA_CALL_INSTANCE_ID,
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
