import pytest

from . import constants
from . import helpers


@pytest.mark.parametrize(
    [
        'conductor_response',
        'params',
        'headers',
        'expected_status',
        'expected_json',
    ],
    [
        (
            # Invalid token
            'test_group_1\ntest_group_2',
            {'timestamp': 100},
            helpers.make_headers('bad_token'),
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
        ),
        (
            # Token of another group
            'test_group_1\ntest_group_2',
            {'timestamp': 100},
            helpers.make_headers('token_3'),
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
        ),
        (
            # Group without templates
            'test_group_1\ntest_group_2',
            {'timestamp': 100},
            helpers.make_headers('token_1'),
            200,
            {
                'timestamp': 150,
                'files': [
                    {
                        'data': 'really common audit secret',
                        'path': '/etc/yandex/taxi-audit/secrets.json',
                        'ownership': {},
                    },
                ],
            },
        ),
        (
            # Template without secrets
            'test_group_3\ntest_group_4',
            {'timestamp': 100},
            helpers.make_headers('token_3'),
            200,
            {
                'files': [
                    {
                        'data': 'mongo_settings',
                        'path': '/etc/yandex/taxi-secdist/taxi.json',
                        'ownership': {},
                    },
                    {
                        'data': 'really common audit secret',
                        'path': '/etc/yandex/taxi-audit/secrets.json',
                        'ownership': {},
                    },
                    {
                        'data': 'elastic credentials',
                        'path': '/etc/yandex/taxi-pilorama/secrets.json',
                        'ownership': {'user': 'pilorama', 'group': 'pilorama'},
                    },
                ],
                'timestamp': 150,
            },
        ),
        (
            'test_group_5',
            {'timestamp': 100},
            helpers.make_headers('token_5'),
            200,
            {
                'files': [
                    {
                        'data': constants.EXPECTED,
                        'path': '/etc/yandex/taxi-secdist/taxi.json',
                        'ownership': {},
                    },
                    {
                        'data': 'really common audit secret',
                        'path': '/etc/yandex/taxi-audit/secrets.json',
                        'ownership': {},
                    },
                ],
                'timestamp': 250,
            },
        ),
        (
            # Not Modified
            'test_group_5',
            {'timestamp': 300},
            helpers.make_headers('token_5'),
            304,
            None,
        ),
        (
            # templates.updated is greater than 300
            'test_group_10',
            {'timestamp': 300},
            helpers.make_headers('token_10'),
            200,
            {
                'files': [
                    {
                        'data': constants.EXPECTED,
                        'path': '/etc/yandex/taxi-secdist/taxi.json',
                        'ownership': {},
                    },
                    {
                        'data': 'really common audit secret',
                        'path': '/etc/yandex/taxi-audit/secrets.json',
                        'ownership': {},
                    },
                ],
                'timestamp': 350,
            },
        ),
        (
            # VaultSession raises error
            'test_group_7',
            {'timestamp': 100},
            helpers.make_headers('token_7'),
            500,
            {
                'code': 'RENDER_ERROR',
                'message': (
                    'some variables ({\'TEST_2\'}) have no value to ' 'render'
                ),
            },
        ),
        (
            # Bad template
            'test_group_8',
            {'timestamp': 100},
            helpers.make_headers('token_8'),
            500,
            {
                'code': 'RENDER_ERROR',
                'message': (
                    'unable to parse template secdist/test_service_4: '
                    'expected token \':\', got \'}\''
                ),
            },
        ),
        (
            # Wrong env (testing)
            'test_group_9',
            {'timestamp': 100},
            helpers.make_headers('token_9'),
            500,
            {
                'code': 'RENDER_ERROR',
                'message': (
                    'some variables ({\'TEST_1\'}) have no value to ' 'render'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_get_secrets_list(
        web_app_client,
        patch_conductor_session,
        vault_mockserver,
        conductor_response,
        params,
        headers,
        expected_status,
        expected_json,
        patched_logs,
        patch_get_host_name,
):
    patch_conductor_session(conductor_response)
    vault_mockserver(constants.VAULT_VERSIONS)
    response = await web_app_client.get(
        '/v1/secrets/list/', params=params, headers=headers,
    )
    assert response.status == expected_status
    if expected_json is not None:
        assert expected_json == await response.json()

    assert patched_logs
    for log_message in patched_logs:
        assert 'London' not in log_message
        assert 'uri=/v1/secrets/list/?timestamp=' in log_message
