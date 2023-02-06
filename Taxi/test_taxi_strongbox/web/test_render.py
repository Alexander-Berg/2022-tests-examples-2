# pylint: disable=inconsistent-return-statements,unused-variable
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import pytest

from taxi_strongbox.components import secret_processor as sp
from taxi_strongbox.components import secret_type as st
from taxi_strongbox.components.sessions import exceptions

EXPECTED_RAW = 'mongo_settings'

EXPECTED_SAFE = (
    '"test_provider": {\n  "uri": "mongodb://user:{}@host:port/db_name"\n}'
)

TOKENS_BY_VERSION_UUID = {
    'auth_version_uuid_1': 'token_1',
    'auth_version_uuid_3': 'token_3',
    'auth_version_uuid_5': 'token_5',
    'auth_version_uuid_6': 'token_6',
    'auth_version_uuid_7': 'token_7',
    'auth_version_uuid_8': 'token_8',
    'auth_version_uuid_9': 'token_9',
    'auth_version_uuid_10': 'token_10',
    'auth_version_uuid_11': 'token_11',
}

VAULT_VERSIONS = {
    'VERSION_UUID_1': {
        'value': [
            {'key': 'project', 'value': 'test_project'},
            {'key': 'provider_name', 'value': 'test_provider'},
            {'key': 'user', 'value': 'user'},
            {'key': 'host', 'value': 'host'},
            {'key': 'port', 'value': 'port'},
            {'key': 'password', 'value': 'real_password'},
            {'key': 'db_name', 'value': 'db_name'},
        ],
    },
    'VERSION_UUID_2': exceptions.SessionError(),
}
for version_uuid, token in TOKENS_BY_VERSION_UUID.items():
    VAULT_VERSIONS[version_uuid] = {
        'value': [{'key': sp.AUTH_SECRET_VALUE_KEY, 'value': token}],
    }


def test_obfuscate():
    assert st._match_path('a.b', 'a.b')
    assert not st._match_path('a.b', 'a.c')
    assert st._match_path('a.3.key', 'a.$.key')
    assert not st._match_path('a.c.key', 'a.$.key')
    assert st._match_path('a.3.key.5.key', 'a.$.key.$.key')
    assert not st._match_path('a.3.key.5.key', 'a.$.key.$.key2')


@pytest.mark.parametrize(
    ['status_code', 'service', 'env', 'expected'],
    [
        (500, 'test_service_2', 'testing', None),
        (200, 'test_service_2', 'unstable', EXPECTED_SAFE),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_secrets_safe_render(
        taxi_strongbox_web,
        status_code,
        service,
        env,
        expected,
        vault_mockserver,
):
    vault_mockserver(VAULT_VERSIONS)
    params = {'service_name': service, 'env': env}
    response = await taxi_strongbox_web.get(
        '/v1/secrets/safe_render/', params=params,
    )
    assert response.status == status_code
    if status_code == 200:
        response_json = await response.json()
        assert expected == response_json['data']


@pytest.mark.parametrize(
    ['status_code', 'secret_key', 'env', 'expected'],
    [
        pytest.param(
            200, 'TEST_1', 'unstable', EXPECTED_SAFE, id='REAL SECRET',
        ),
        pytest.param(
            404,
            'NON_EXISTENT_SECRET',
            'testing',
            None,
            id='NON-EXISTENT SECRET',
        ),
        pytest.param(
            404,
            'TEST_2',
            'unstable',
            None,
            id='BROKEN SECRET EXISTS IN STRONGBOX, BUT NOT IN YAV',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_single_secret_safe_render(
        taxi_strongbox_web,
        status_code,
        secret_key,
        env,
        expected,
        vault_mockserver,
):
    vault_mockserver(VAULT_VERSIONS)
    params = {'secret_name': secret_key, 'env': env}
    response = await taxi_strongbox_web.get(
        '/v1/secrets/single/safe_render/', params=params,
    )
    assert response.status == status_code, await response.json()
    if status_code == 200:
        response_json = await response.json()
        assert expected == response_json['data']
