import pytest

VAULT_VERSIONS = {
    'VERSION_UUID_2': {
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
    'VERSION_UUID_PG_2': {
        'value': [
            {'key': 'project', 'value': 'test_project'},
            {'key': 'provider_name', 'value': 'test_provider'},
            {'key': 'shards.0.password', 'value': '123'},
            {'key': 'shards.0.user', 'value': 'deoevgen'},
            {'key': 'shards.0.host', 'value': 'coll_host'},
            {'key': 'shards.0.port', 'value': '1111'},
            {'key': 'shards.0.db_name', 'value': 'deo_db'},
        ],
    },
}


@pytest.mark.parametrize(
    ['key', 'expected_status', 'expected_response'],
    [
        pytest.param(
            'TEST_2',
            200,
            {
                'key': 'TEST_2',
                'type': 'mongodb',
                'environments': [
                    {
                        'environment': 'unstable',
                        'yav_link': (
                            'https://yav.yandex-team.ru/secret/'
                            'YAV_UUID_2/explore/version/VERSION_UUID_2'
                        ),
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {'key': 'user', 'value': 'user'},
                            {'key': 'host', 'value': 'host'},
                            {'key': 'port', 'value': 'port'},
                            {'key': 'db_name', 'value': 'db_name'},
                        ],
                    },
                ],
                'scope': {'project_name': 'meow'},
                'tvm_access_services': [],
                'use_in_services': [{'name': 'test_service_2'}],
            },
        ),
        pytest.param(
            'POSTGRES_TAXI_STRONGBOX',
            200,
            {
                'key': 'POSTGRES_TAXI_STRONGBOX',
                'type': 'postgresql',
                'environments': [
                    {
                        'environment': 'testing',
                        'yav_link': (
                            'https://yav.yandex-team.ru/secret/'
                            'YAV_UUID_PG_2/explore/version/VERSION_UUID_PG_2'
                        ),
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {
                                'key': 'shards',
                                'value': [
                                    {
                                        'user': 'deoevgen',
                                        'host': 'coll_host',
                                        'port': '1111',
                                        'db_name': 'deo_db',
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'scope': {
                    'project_name': 'project_name',
                    'service_name': 'service_name',
                },
                'tvm_access_services': [],
                'use_in_services': [],
            },
        ),
        pytest.param(
            'NOT_FOUND_KEY',
            404,
            {
                'code': 'SECRET_NOT_FOUND',
                'message': 'Secret: NOT_FOUND_KEY is not found',
            },
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_secret_retrieve(
        taxi_strongbox_web,
        vault_mockserver,
        key,
        expected_status,
        expected_response,
        clowny_roles_grants,
):
    vault_mockserver(VAULT_VERSIONS)
    clowny_roles_grants.add_prod_editor(
        'login', {'type': 'project', 'id': 'meow'},
    )
    clowny_roles_grants.add_creator('login', {'type': 'project', 'id': 'meow'})

    response = await taxi_strongbox_web.post(
        '/v2/secret/retrieve/',
        json={'key': key},
        headers={
            'X-Yandex-Login': 'login',
            'X-YaTaxi-Api-Key': 'strongbox_api_token',
        },
    )
    data = await response.json()
    assert response.status == expected_status, data
    assert data == expected_response
