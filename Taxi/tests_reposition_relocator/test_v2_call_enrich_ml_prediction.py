# pylint: disable=import-only-modules
import copy
import json

import pytest

from .utils import format_execution_timestamp


NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    REPOSITION_RELOCATOR_UMLAAS_ASYNC_REQUESTS={
        'max_bulk_size': 1,
        'max_parallel_requests': 100,
    },
)
@pytest.mark.parametrize('negative_prediction', [False, True])
@pytest.mark.parametrize('use_umlaas_pricing', [False, True])
async def test_put(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        negative_prediction,
        use_umlaas_pricing,
        experiments3,
):
    @mockserver.json_handler(
        '/umlaas-pricing/umlaas-pricing/v1/surge-statistics',
    )
    def mock_umlaas_pricing(request):
        assert use_umlaas_pricing

        req = json.loads(request.get_data())
        assert req['request_source'] is not None
        assert req['user_id'] is not None
        assert req['point_a'] is not None
        assert req['tariff_zone'] is not None
        assert req['by_category']

        result = {'by_category': {}}
        prediction = 0.33333333
        if negative_prediction:
            prediction = prediction - 1
        for category in req['by_category']:
            result['by_category'][category] = {
                'results': [{'name': 'pins', 'value': prediction}],
            }
        return mockserver.make_response(json.dumps(result))

    @mockserver.json_handler('/umlaas/umlaas/v1/surge-statistics')
    def mock_umlaas(request):
        assert not use_umlaas_pricing

        req = json.loads(request.get_data())
        assert req['request_source'] is not None
        assert req['user_id'] is not None
        assert req['point_a'] is not None
        assert req['tariff_zone'] is not None
        assert req['by_category']

        result = {'by_category': {}}
        prediction = 0.33333333
        if negative_prediction:
            prediction = prediction - 1
        for category in req['by_category']:
            result['by_category'][category] = {
                'results': [{'name': 'pins', 'value': prediction}],
            }
        return mockserver.make_response(json.dumps(result))

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

    if use_umlaas_pricing:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_surge_statistic_enabled_exp3_config.json',
            ),
        )
    else:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_surge_statistic_disabled_exp3_config.json',
            ),
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/enrich_ml_prediction/' + NIRVANA_CALL_INSTANCE_ID,
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

    if use_umlaas_pricing:
        assert mock_umlaas_pricing.times_called == 4
    else:
        assert mock_umlaas.times_called == 4

    expected_results = load_json(
        'results_{}.json'.format(
            'negative' if negative_prediction else 'positive',
        ),
    )
    expected_results['data'][0]['destinations_demands']['1'].sort()

    results = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    results['data'][0]['destinations_demands']['1'].sort()

    assert results == expected_results


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    REPOSITION_RELOCATOR_UMLAAS_ASYNC_REQUESTS={
        'max_bulk_size': 1,
        'max_parallel_requests': 100,
    },
    REPOSITION_RELOCATOR_PARALLEL_REQUEST_PROCESSING_COUNT=6,
)
@pytest.mark.parametrize('negative_prediction', [False, True])
async def test_put_multiple(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        negative_prediction,
):
    @mockserver.json_handler('/umlaas/umlaas/v1/surge-statistics')
    def mock_surge_statistics(request):
        req = json.loads(request.get_data())
        assert req['request_source'] is not None
        assert req['user_id'] is not None
        assert req['point_a'] is not None
        assert req['tariff_zone'] is not None
        assert req['by_category']

        result = {'by_category': {}}
        prediction = 0.33333333
        if negative_prediction:
            prediction = prediction - 1
        for category in req['by_category']:
            result['by_category'][category] = {
                'results': [{'name': 'pins', 'value': prediction}],
            }
        return mockserver.make_response(json.dumps(result))

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
        'v2/call/enrich_ml_prediction/' + NIRVANA_CALL_INSTANCE_ID,
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

    assert mock_surge_statistics.times_called == 4 * request_cnt

    expected_results = load_json(
        'results_{}.json'.format(
            'negative' if negative_prediction else 'positive',
        ),
    )
    expected_results['data'][0]['destinations_demands']['1'].sort()
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
        results['data'][i]['destinations_demands']['1'].sort()

    assert results == expected_results


@pytest.mark.filldb()
@pytest.mark.parametrize('missing_type', ['inputs', 'outputs'])
@pytest.mark.now('2018-11-26T08:00:00+0000')
@pytest.mark.config(
    REPOSITION_RELOCATOR_UMLAAS_ASYNC_REQUESTS={
        'max_bulk_size': 1,
        'max_parallel_requests': 1,
    },
)
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
        'v2/call/enrich_ml_prediction/' + NIRVANA_CALL_INSTANCE_ID,
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
            'message': 'Operation enrich/enrich_ml_prediction runtime failure',
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
        'v2/call/enrich_ml_prediction/' + NIRVANA_CALL_INSTANCE_ID,
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
        'v2/call/enrich_ml_prediction/' + NIRVANA_CALL_INSTANCE_ID,
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
