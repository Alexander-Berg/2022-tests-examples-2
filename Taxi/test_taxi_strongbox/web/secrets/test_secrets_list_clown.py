import pytest

from . import constants
from . import helpers


@pytest.mark.parametrize(
    [
        'clownductor_response',
        'params',
        'headers',
        'expected_status',
        'expected_json',
    ],
    [
        (
            # Clownductor as a group source
            constants.CLOWNDUCTOR_RESPONSE,
            {'timestamp': 100, 'group_source': 'clownductor'},
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
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_get_secrets_list_clown(
        web_app_client,
        patch_clownductor_session,
        vault_mockserver,
        clownductor_response,
        params,
        headers,
        expected_status,
        expected_json,
        patched_logs,
        patch_get_host_name,
):
    patch_clownductor_session(clownductor_response)
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
