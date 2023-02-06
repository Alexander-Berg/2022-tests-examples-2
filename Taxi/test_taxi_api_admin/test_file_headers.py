# pylint: disable=unused-variable
import pytest

URL = '/service_with_file_headers/v1/experiments/files/'


@pytest.mark.parametrize(
    'headers,expected_audit_log',
    [
        (
            {
                'YaTaxi-Api-Key': 'secret',
                'X-File-Name': 'file_1.txt',
                'X-Arg-Type': 'str',
            },
            {
                'login': 'superuser',
                'action': 'create_log',
                'arguments': {
                    'request': {
                        'service': 'service_with_file_headers',
                        'endpoint': 'v1/experiments/files/',
                        'headers': {
                            'X-File-Name': 'file_1.txt',
                            'X-Arg-Type': 'str',
                        },
                    },
                    'data': (
                        'Request body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                    'response': (
                        'Response body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                },
                'system_name': 'tariff-editor',
            },
        ),
        (
            {},
            {
                'login': 'superuser',
                'action': 'create_log',
                'arguments': {
                    'request': {
                        'service': 'service_with_file_headers',
                        'endpoint': 'v1/experiments/files/',
                        'headers': {'X-File-Name': None, 'X-Arg-Type': None},
                    },
                    'data': (
                        'Request body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                    'response': (
                        'Response body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                },
                'system_name': 'tariff-editor',
            },
        ),
        (
            {
                'YaTaxi-api-Key': 'secret',
                'X-file-Name': 'file_1.txt',
                'x-Arg-Type': 'str',
            },
            {
                'login': 'superuser',
                'action': 'create_log',
                'arguments': {
                    'request': {
                        'service': 'service_with_file_headers',
                        'endpoint': 'v1/experiments/files/',
                        'headers': {
                            'X-File-Name': 'file_1.txt',
                            'X-Arg-Type': 'str',
                        },
                    },
                    'data': (
                        'Request body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                    'response': (
                        'Response body logging disabled by'
                        ' configuring in yaml schema'
                    ),
                },
                'system_name': 'tariff-editor',
            },
        ),
    ],
)
@pytest.mark.now('2008-08-08T12:00:00')
async def test_service_headers_log(
        headers,
        expected_audit_log,
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        patch_audit_log,
):
    @patch_aiohttp_session('http://unstable-service-host.net')
    def patch_req(method, url, **kwargs):
        return response_mock(read=b'ok')

    response = await taxi_api_admin_client.request(
        'POST', URL, data=b'test_file_content', headers=headers,
    )
    assert response.status == 200

    audit_action_request = patch_audit_log.only_one_request()

    assert bool(audit_action_request)
    assert audit_action_request.pop('timestamp')
    assert audit_action_request == expected_audit_log
