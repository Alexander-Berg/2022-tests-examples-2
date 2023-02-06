# pylint: disable=protected-access
# pylint: disable=unused-variable
import datetime
import json

import pytest

from taxi.util import dates
from taxi.util import permissions


@pytest.mark.parametrize(
    'path,storage,expected',
    [
        (
            'drivers.0.driver_id',
            {'drivers': [{'driver_id': '123'}, {'driver_id': '345'}]},
            '123',
        ),
        (
            'drivers.10.driver_id',
            {'drivers': [{'driver_id': '123'}, {'driver_id': '345'}]},
            None,
        ),
        (
            'driver.driver_id',
            {'driver': {'driver_id': '123', 'phone': '+79998431233'}},
            '123',
        ),
        ('phone', {'driver_licence': 'XXXXXX'}, None),
        (
            'drivers.driver_id',
            {'drivers': [{'driver_id': '123'}, {'driver_id': '345'}]},
            None,
        ),
        ('drivers.driver_id', {'drivers': None}, None),
    ],
)
async def test_get_object_id_from_storage(path, storage, expected):
    assert permissions.get_value_from_storage(path, storage) == expected


@pytest.mark.parametrize(
    'url,data,response,method,expected_audit,headers',
    [
        (
            '/service_with_object_id/user/b698a54d38884/retrieve/',
            {'tplatform_namespace': 'taxi'},
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'get_user_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'user/b698a54d38884/retrieve/',
                    },
                    'data': {'tplatform_namespace': 'taxi'},
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0, 0),
                'object_id': 'b698a54d38884',
                'system_name': 'tariff-editor',
                'tplatform_namespace': 'taxi',
            },
            {},
        ),
        (
            '/service_with_object_id/gps-storage/get/?driver_id=743357cdf01a3',
            {},
            b'ok',
            'GET',
            {
                'login': 'superuser',
                'action': 'get_driver_geotrack',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'gps-storage/get/',
                        'params': {'driver_id': '743357cdf01a3'},
                    },
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0, 0),
                'object_id': '743357cdf01a3',
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/user/search/',
            {'phone': '+79646350521'},
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'search_by_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'user/search/',
                    },
                    'data': {'phone': '+79646350521'},
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'object_id': '+79646350521',
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/gps-storage/get/',
            None,
            b'ok',
            'GET',
            {
                'login': 'superuser',
                'action': 'get_driver_geotrack',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'gps-storage/get/',
                    },
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/user/search/',
            {'field': '+79646350521'},
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'search_by_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'user/search/',
                    },
                    'data': {'field': '+79646350521'},
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/order/search/',
            {'field': '+79646350521'},
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'search_by_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'order/search/',
                    },
                    'data': {'field': '+79646350521'},
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/driver/search/',
            {'field': '+79646350521'},
            b'ok',
            'POST',
            None,
            {},
        ),
        (
            '/service_with_object_id/approvals/path/',
            {
                'request_id': '123123',
                'run_manually': False,
                'data': {'innerdata': {'entities': [{'id': '2e1fde655d773'}]}},
                'service_name': 'random_service',
                'api_path': 'random_path',
                'mode': 'push',
            },
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'approve_something',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'approvals/path/',
                    },
                    'data': {
                        'request_id': '123123',
                        'run_manually': False,
                        'data': {
                            'innerdata': {
                                'entities': [{'id': '2e1fde655d773'}],
                            },
                        },
                        'service_name': 'random_service',
                        'api_path': 'random_path',
                        'mode': 'push',
                    },
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'object_id': '2e1fde655d773',
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/create/something/',
            {},
            b'\xe1n',  # non utf-8
            'POST',
            {
                'login': 'superuser',
                'action': 'create_something',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'create/something/',
                    },
                    'data': {},
                    'response': 'b\'\\xe1n\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/create/something/',
            {},
            bytes(
                json.dumps({'innerdata': {'creature_id': '6e2519fc4916e'}}),
                'utf-8',
            ),
            'POST',
            {
                'login': 'superuser',
                'action': 'create_something',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'create/something/',
                    },
                    'data': {},
                    'response': {
                        'innerdata': {'creature_id': '6e2519fc4916e'},
                    },
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'object_id': '6e2519fc4916e',
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/user/search/',
            b'\xe1n',
            b'\xe1n',
            'POST',
            {
                'login': 'superuser',
                'action': 'search_by_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'user/search/',
                    },
                    'data': 'b\'\\xe1n\'',
                    'response': 'b\'\\xe1n\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/get-config/GREAT_CONFIG_NAME/',
            None,
            b'ok',
            'GET',
            {
                'login': 'superuser',
                'action': 'search_by_pd',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'get-config/GREAT_CONFIG_NAME/',
                    },
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'object_id': 'GREAT_CONFIG_NAME',
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_exclude_audit/fields_exclude/',
            {
                'important_data': {'request_key': '123123'},
                'object_id_path': 'object_id_value',
            },
            bytes(
                json.dumps(
                    {
                        'response_key': 'some_key',
                        'another_key': 123,
                        'summary': {'current': {}, 'new': {'test': 'cool'}},
                    },
                ),
                'utf-8',
            ),
            'POST',
            {
                'login': 'superuser',
                'action': 'some_action_id',
                'arguments': {
                    'request': {
                        'service': 'service_with_exclude_audit',
                        'endpoint': 'fields_exclude/',
                    },
                    'data': {
                        'important_data': {
                            'request_key': (
                                'Field is hidden because' ' of security reason'
                            ),
                        },
                        'object_id_path': 'object_id_value',
                    },
                    'response': {
                        'response_key': (
                            'Field is hidden because of security reason'
                        ),
                        'another_key': 123,
                        'summary': {'current': {}, 'new': {'test': 'cool'}},
                    },
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_exclude_audit/full_exclude/',
            {
                'important_data': {'request_key': '123123'},
                'object_id_path': 'object_id_value',
            },
            bytes(
                json.dumps({'response_key': 'some_key', 'another_key': 123}),
                'utf-8',
            ),
            'POST',
            {
                'login': 'superuser',
                'action': 'some_action_id',
                'arguments': {
                    'request': {
                        'service': 'service_with_exclude_audit',
                        'endpoint': 'full_exclude/',
                    },
                    'data': (
                        'Request body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                    'response': (
                        'Response body logging disabled by configuring'
                        ' in yaml schema'
                    ),
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0),
                'system_name': 'tariff-editor',
            },
            {},
        ),
        (
            '/service_with_object_id/upload/file/',
            {},
            b'ok',
            'POST',
            {
                'login': 'superuser',
                'action': 'upload_file',
                'arguments': {
                    'request': {
                        'service': 'service_with_object_id',
                        'endpoint': 'upload/file/',
                    },
                    'data': {},
                    'response': 'b\'ok\'',
                },
                'timestamp': datetime.datetime(2008, 8, 8, 12, 0, 0),
                'object_id': 'important_file.txt',
                'system_name': 'tariff-editor',
            },
            {'X-File-Name': 'important_file.txt'},
        ),
    ],
)
@pytest.mark.now('2008-08-08T12:00:00')
async def test_service_with_no_response(
        url,
        data,
        response,
        method,
        expected_audit,
        headers,
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        patch_audit_log,
):
    @patch_aiohttp_session('http://unstable-service.yandex.net')
    def patch_request(method, url, **kwargs):
        return response_mock(read=response)

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/drafts/create/',
    )
    def _patch_approvals(*args, **kwargs):
        return response_mock(read=response)

    if data is None:
        response = await taxi_api_admin_client.request(method, url)
    else:
        data = json.dumps(data) if isinstance(data, dict) else data
        response = await taxi_api_admin_client.request(
            method, url, data=data, headers=headers,
        )
    assert response.status == 200
    audit_action_request = patch_audit_log.only_one_request()
    if audit_action_request:
        expected_timestamp = expected_audit.pop('timestamp')
        request_timestamp_raw = audit_action_request.pop('timestamp')
        parsed = dates.parse_timestring(request_timestamp_raw, timezone='UTC')
        assert parsed == expected_timestamp
        assert audit_action_request == expected_audit


async def test_check_platform_audit_action(
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        grands_retrieve_mock,
        patch_audit_log,
):
    @patch_aiohttp_session(
        'http://unstable-service-host.net/v1/namespaces/retrieve/',
    )
    def _patch_namespaces_retrieve_request(*args, **kwargs):
        return response_mock(text='response', read=b'response')

    grands_retrieve_mock(['clowny_role_1'])
    url = '/platform/platform/send_sms/'
    response = await taxi_api_admin_client.request(
        'GET',
        url,
        params={'tplatform_namespace': 'taxi', 'project_name': 'taxi-support'},
        json={'data': 'data'},
    )
    response_body = await response.read()
    assert response.status == 200, response_body
    audit_action_request = patch_audit_log.only_one_request()
    assert audit_action_request.pop('timestamp')
    assert audit_action_request == {
        'action': 'test_action_id',
        'arguments': {
            'data': (
                'Request body logging disabled by configuring in yaml '
                'schema'
            ),
            'request': {
                'endpoint': 'send_sms/',
                'headers': {'X-Arg-Type': None, 'X-File-Name': None},
                'params': {
                    'project_name': 'taxi-support',
                    'tplatform_namespace': 'taxi',
                },
                'service': 'platform',
            },
            'response': 'b\'response\'',
        },
        'login': 'superuser',
        'system_name': 'tplatform',
        'tplatform_namespace': 'taxi',
    }


async def test_namespace_response(
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        patch_audit_log,
):
    @patch_aiohttp_session(
        'http://unstable-service-host.net/order/search', 'POST',
    )
    def _patch_namespaces_retrieve_request(*args, **kwargs):
        response_raw = bytes(
            json.dumps({'some_data': {'tplatform_namespace': 'market'}}),
            'utf-8',
        )
        return response_mock(read=response_raw)

    url = '/service_with_object_id/order/search'
    response = await taxi_api_admin_client.request(
        'POST', url, params={}, json={'data': 'data'},
    )
    response_body = await response.json()
    assert response.status == 200, response_body
    audit_action_request = patch_audit_log.only_one_request()
    assert audit_action_request.pop('timestamp')
    assert audit_action_request == {
        'login': 'superuser',
        'action': 'search_by_pd',
        'arguments': {
            'request': {
                'service': 'service_with_object_id',
                'endpoint': 'order/search',
            },
            'data': {'data': 'data'},
            'response': {'some_data': {'tplatform_namespace': 'market'}},
        },
        'system_name': 'tariff-editor',
        'tplatform_namespace': 'market',
    }
