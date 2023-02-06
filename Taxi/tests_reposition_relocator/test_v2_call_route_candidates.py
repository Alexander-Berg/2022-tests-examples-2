# pylint: disable=import-error, import-only-modules
import copy
import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from .utils import format_execution_timestamp

NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_ROUTER_BY_TRANSPORT_TYPE={
        '__default__': 'car',
        'bicycle': 'pedestrian',
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put(
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 37.2511
        lat = 55.5237
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
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
    assert mock_router.times_called == 1
    assert mock_pedestrian_router.times_called == 1


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_ROUTER_BY_TRANSPORT_TYPE={
        '__default__': 'car',
        'bicycle': 'pedestrian',
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow_good_default.json')
async def test_put_good_default(
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 0
        lat = 0
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    await taxi_reposition_relocator.invalidate_caches()

    request = load_json('requests.json')
    request['data'][0]['destinations']['1']['descriptor'][
        'descriptor_value'
    ] = 'moscow_default'
    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(request).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    expected_result['data'][0]['destinations']['1']['descriptor'][
        'descriptor_value'
    ] = 'moscow_default'
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

    assert mock_adjuster.times_called == 0
    assert mock_router.times_called == 1
    assert mock_pedestrian_router.times_called == 1


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    REPOSITION_RELOCATOR_PARALLEL_REQUEST_PROCESSING_COUNT=6,
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_multiple_requests(
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 37.2511
        lat = 55.5237
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    for i in range(1, request_cnt):
        new_data = copy.deepcopy(expected_result['data'][0])
        new_data['request_info']['request_id'] += '_' + str(i)
        expected_result['data'].append(new_data)

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

    assert mock_adjuster.times_called == request_cnt
    assert mock_router.times_called == 2 * request_cnt


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('missing_type', ['inputs', 'outputs'])
async def test_put_missing_io(
        taxi_reposition_relocator,
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

    response = await taxi_reposition_relocator.put(
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_router_error(
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

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def mock_adjuster(request):
        lon = 37.25113923155032
        lat = 55.52370600028711
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response('', 500)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
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
    assert mock_router.times_called == 6


@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.parametrize('fail_kind', ['server_error', 'adjusted_outside'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_adjusting_error(
        taxi_reposition_relocator,
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
            return mockserver.make_response('', 500)

        lon = 37
        lat = 55
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 0},
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
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
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')

    if fail_kind == 'server_error':
        for request in expected_result['data']:
            request['routes'] = {
                '1': {
                    'points': [
                        [37.25133, 55.487779],
                        [37.63615515249695, 55.73924389726113],
                    ],
                    'router_distance': 10500.0,
                    'router_time': 2500.0,
                },
                '2': {
                    'points': [
                        [70.0, 70.0],
                        [37.63615515249695, 55.73924389726113],
                    ],
                    'router_distance': 10500.0,
                    'router_time': 2500.0,
                },
            }

        assert mock_adjuster.times_called == 3
        assert mock_router.times_called == 2
    elif fail_kind == 'adjusted_outside':
        expected_result['data'] = []

        assert mock_adjuster.times_called == 1
        assert mock_router.times_called == 0

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert expected_result == stored_result


@pytest.mark.geoareas(filename='geoareas_moscow.json')
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
