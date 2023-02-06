# pylint: disable=import-only-modules
import json

import pytest

from .utils import format_execution_timestamp

NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.filldb()
@pytest.mark.config(
    REPOSITION_RELOCATOR_AIRPORT_QUEUE_DEMAND_FORMULA_CONFIG={
        '__default__': {
            '__default__': {'ar_reverse': 1.0, 'cr': 1.0, 'constant': 0.0},
        },
        'led_airport_queue_id': {
            '__default__': {'ar_reverse': 1.0, 'cr': 1.0, 'constant': 0.0},
            'econom': {'ar_reverse': 1.0, 'cr': 0.5, 'constant': 1.0},
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_spb.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
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

    @mockserver.json_handler('/dispatch-airport/info/needs/v1')
    def _mock_dispatch_airport(request):
        zone = request.args['zone']

        assert zone in ['svo', 'dme', 'spb']

        return mockserver.make_response(
            json.dumps(
                {
                    'svo_airport_queue_id': {
                        'zone': 'svo',
                        'airport': 'SVO',
                        'class_demand': {
                            'cargo': {'count': 2, 'expected_wait_time': 60},
                            'comfort': {'count': 4, 'expected_wait_time': 120},
                            'econom': {'count': 7, 'expected_wait_time': 300},
                        },
                    },
                    'dme_airport_queue_id': {
                        'zone': 'dme',
                        'airport': 'DME',
                        'class_demand': {},
                    },
                    'led_airport_queue_id': {
                        'zone': 'spb',
                        'airport': 'LED',
                        'class_demand': {
                            'econom': {'count': 3, 'expected_wait_time': 30},
                        },
                    },
                },
            ),
            status=200,
        )

    @mockserver.json_handler(
        '/reposition-api/v1/service/airport_queue/get_drivers_en_route',
    )
    def _mock_driver_en_route(request):
        assert request.args['airport_queue_id'] in [
            'svo_airport_queue_id',
            'dme_airport_queue_id',
            'led_airport_queue_id',
        ]

        return mockserver.make_response(
            json.dumps({'cargo': 2, 'comfort': 1, 'econom': 4}), status=200,
        )

    await taxi_reposition_relocator.invalidate_caches()

    response = await taxi_reposition_relocator.put(
        'v2/call/get_airport_demand/' + NIRVANA_CALL_INSTANCE_ID,
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

    expected = load_json('results.json')
    for request in expected['data']:
        for _, value in request['destinations_demands'].items():
            value.sort()

    actual = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in actual['data']:
        for _, value in request['destinations_demands'].items():
            value.sort()
        assert 'request_info' in request
        del request['request_info']['request_id']

    assert expected == actual


@pytest.mark.filldb()
@pytest.mark.config(
    REPOSITION_RELOCATOR_AIRPORT_QUEUE_DEMAND_FORMULA_CONFIG={
        '__default__': {
            '__default__': {'ar_reverse': 1.0, 'cr': 1.0, 'constant': 0.0},
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_spb.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_empty_demand(
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

    @mockserver.json_handler('/dispatch-airport/info/needs/v1')
    def _mock_dispatch_airport(request):
        zone = request.args['zone']

        assert zone in ['svo', 'dme', 'spb']

        return mockserver.make_response(
            json.dumps(
                {
                    'svo_airport_queue_id': {
                        'zone': 'svo',
                        'airport': 'SVO',
                        'class_demand': {
                            'econom': {'count': 1, 'expected_wait_time': 300},
                        },
                    },
                },
            ),
            status=200,
        )

    @mockserver.json_handler(
        '/reposition-api/v1/service/airport_queue/get_drivers_en_route',
    )
    def _mock_driver_en_route(request):
        assert request.args['airport_queue_id'] in ['svo_airport_queue_id']

        return mockserver.make_response(json.dumps({'econom': 1}), status=200)

    await taxi_reposition_relocator.invalidate_caches()

    response = await taxi_reposition_relocator.put(
        'v2/call/get_airport_demand/' + NIRVANA_CALL_INSTANCE_ID,
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

    actual = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    assert actual == {
        'data': [],
        'meta': {'created_at': '2018-11-26T08:00:00+00:00'},
    }


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
        'v2/call/get_airport_demand/' + NIRVANA_CALL_INSTANCE_ID,
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
            'message': 'Operation search/get_airport_demand runtime failure',
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
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_put_dispatch_airport_error(
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

    @mockserver.json_handler('/dispatch-airport/info/needs/v1')
    def _mock_dispatch_airport(request):
        return mockserver.make_response('', 500)

    response = await taxi_reposition_relocator.put(
        'v2/call/get_airport_demand/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    # TODO(sandyre): fixed texts for reposition request errors
    assert response.status_code == 200

    patched_response = response.json()
    patched_response['executionState']['details'] = ''

    assert patched_response == {
        'executionState': {
            'details': '',
            'message': 'Operation search/get_airport_demand runtime failure',
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

    assert _mock_dispatch_airport.times_called == 3


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
        'v2/call/get_airport_demand/' + NIRVANA_CALL_INSTANCE_ID,
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
