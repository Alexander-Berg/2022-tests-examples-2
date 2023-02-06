import json

import pytest

from tests_reposition_graph_relocator.utils import timestamp

NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.skip('Graph router is deprecated for now')
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_WORKFLOW_DEBUG=[
        'Testsuite route_candidates workflow',
    ],
    GRAPH_JAMS_LIFETIME=0,
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put(
        taxi_reposition_graph_relocator,
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 37.526510
        lat = 55.698854
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
                'DOWNLOAD_INPUTS': timestamp.format_execution_timestamp(
                    now, 2,
                ),
                'PROCESS_OPERATION': timestamp.format_execution_timestamp(
                    now, 3,
                ),
                'UPLOAD_OUTPUTS': timestamp.format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    for request in expected_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    stored_drivers = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/ae5208e9-e169-4106-b388-704db9061557',
        ),
    )
    assert stored_drivers == {
        'drivers': [],
        'meta': {'created_at': '2018-11-26T08:00:00+00:00'},
    }

    assert mock_adjuster.times_called == 1


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_WORKFLOW_DEBUG=[
        'Testsuite route_candidates workflow',
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_hex_zones(
        taxi_reposition_graph_relocator,
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
        json.dumps(load_json('requests_hex.json')).encode('utf-8'),
    )

    request = load_json('request.json')
    request['data']['options']['search_hexagonal_zones'] = True
    request['data']['options']['min_route_time'] = 1
    request['data']['options']['min_route_distance'] = 1
    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
                'DOWNLOAD_INPUTS': timestamp.format_execution_timestamp(
                    now, 2,
                ),
                'PROCESS_OPERATION': timestamp.format_execution_timestamp(
                    now, 3,
                ),
                'UPLOAD_OUTPUTS': timestamp.format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results_hex.json')
    for request in expected_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_WORKFLOW_DEBUG=[
        'Testsuite route_candidates workflow',
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_hex_zones_excluded(
        taxi_reposition_graph_relocator,
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

    requests = load_json('requests_hex.json')
    requests['data'][0]['candidates']['1488_driverSS']['position'] = [0, 0]
    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(requests).encode('utf-8'),
    )

    request = load_json('request.json')
    request['data']['options']['search_hexagonal_zones'] = True
    request['data']['options']['min_route_time'] = 1
    request['data']['options']['min_route_distance'] = 1

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
                'DOWNLOAD_INPUTS': timestamp.format_execution_timestamp(
                    now, 2,
                ),
                'PROCESS_OPERATION': timestamp.format_execution_timestamp(
                    now, 3,
                ),
                'UPLOAD_OUTPUTS': timestamp.format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    stored_drivers = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/ae5208e9-e169-4106-b388-704db9061557',
        ),
    )

    assert stored_drivers == {
        'drivers': [{'park_id': '1488', 'driver_profile_id': 'driverSS'}],
        'meta': {'created_at': '2018-11-26T08:00:00+00:00'},
    }


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('missing_type', ['inputs', 'outputs'])
async def test_put_missing_io(
        taxi_reposition_graph_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        missing_type,
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

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
            'message': 'Operation routing/route_candidates runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.skip('Graph router is deprecated for now')
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_router_error(
        taxi_reposition_graph_relocator,
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 37.25113923155032
        lat = 55.52370600028711
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
                'DOWNLOAD_INPUTS': timestamp.format_execution_timestamp(
                    now, 2,
                ),
                'PROCESS_OPERATION': timestamp.format_execution_timestamp(
                    now, 3,
                ),
                'UPLOAD_OUTPUTS': timestamp.format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = {
        'data': [],
        'meta': {'created_at': '2018-11-26T08:00:00+00:00'},
    }

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert expected_result == stored_result

    # 3 retries is default
    assert mock_adjuster.times_called == 1


@pytest.mark.skip('Graph router is deprecated for now')
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.parametrize('fail_kind', ['server_error', 'adjusted_outside'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_adjusting_error(
        taxi_reposition_graph_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        fail_kind,
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        if fail_kind == 'server_error':
            return mockserver.make_response(
                '{}', status=500, content_type='application/json',
            )

        lon = 37
        lat = 55
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
                'CHECK_AUTH': timestamp.format_execution_timestamp(now, 0),
                'CREATE_OPERATION': timestamp.format_execution_timestamp(
                    now, 1,
                ),
                'DOWNLOAD_INPUTS': timestamp.format_execution_timestamp(
                    now, 2,
                ),
                'PROCESS_OPERATION': timestamp.format_execution_timestamp(
                    now, 3,
                ),
                'UPLOAD_OUTPUTS': timestamp.format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')

    if fail_kind == 'server_error':
        expected_result['data'] = []

        assert mock_adjuster.times_called == 3
    elif fail_kind == 'adjusted_outside':
        expected_result['data'] = []

        assert mock_adjuster.times_called == 1

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert expected_result == stored_result


@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_forbidden(
        taxi_reposition_graph_relocator, pgsql, mockserver, load_json,
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

    response = await taxi_reposition_graph_relocator.put(
        'v2/call/route_candidates/' + NIRVANA_CALL_INSTANCE_ID,
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
async def test_disabled(taxi_reposition_graph_relocator, load_json):
    response = await taxi_reposition_graph_relocator.put(
        'v2/call/echo/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'Disabled in config',
            'message': 'Processor is disabled',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }
