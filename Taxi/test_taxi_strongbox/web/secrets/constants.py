from taxi_strongbox.components import secret_processor as sp
from taxi_strongbox.components.sessions import exceptions


CLOWNDUCTOR_RESPONSE = [
    {
        'id': 123,
        'branch_id': 1,
        'name': 'test_host',
        'datacenter': 'man',
        'dom0_name': None,
        'dom0_updated_at': 0,
        'branch_name': 'unstable',
        'service_name': 'some-service',
        'service_id': 8,
        'project_name': 'taxi',
        'project_id': 11,
    },
]

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

EXPECTED = (
    '"test_provider": {\n  "uri": "mongodb://user:@host:port/db_name"\n}'
)

MONDO_DATA = {
    'project': 'taxi',
    'provider_name': 'strongbox',
    'user': 'test_user',
    'password': '12345',
    'host': 'test_host',
    'port': 'test_port',
    'db_name': 'test-db',
}

VAULT_VERSIONS = {
    'VERSION_UUID_1': {
        'value': [
            {'key': 'project', 'value': 'test_project'},
            {'key': 'provider_name', 'value': 'test_provider'},
            {'key': 'user', 'value': 'user'},
            {'key': 'host', 'value': 'host'},
            {'key': 'port', 'value': 'port'},
            {'key': 'db_name', 'value': 'db_name'},
        ],
    },
    'VERSION_UUID_2': exceptions.SessionError(),
}
for version_uuid, token in TOKENS_BY_VERSION_UUID.items():
    VAULT_VERSIONS[version_uuid] = {
        'value': [{'key': sp.AUTH_SECRET_VALUE_KEY, 'value': token}],
    }
