# pylint: disable=import-only-modules
import json

import pytest

from .utils import format_execution_timestamp

NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


@pytest.mark.filldb()
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

    @mockserver.json_handler('/nirvana/api/public/v1/getBlockParameters')
    def mock_nirvana_block_parameters(request):
        return load_json('response_params.json')

    @mockserver.json_handler('/nirvana/api/public/v1/getBlockMetaData')
    def mock_nirvana_block_metadata(request):
        return load_json('response_metadata.json')

    response = await taxi_reposition_relocator.put(
        'v2/call/log_operations_params/' + NIRVANA_CALL_INSTANCE_ID,
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

    assert mock_nirvana_block_parameters.times_called == 1
    assert mock_nirvana_block_metadata.times_called == 1


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
        'v2/call/log_operations_params/' + NIRVANA_CALL_INSTANCE_ID,
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
        'v2/call/log_operations_params/' + NIRVANA_CALL_INSTANCE_ID,
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
