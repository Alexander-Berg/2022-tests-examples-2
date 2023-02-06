import pytest


@pytest.mark.parametrize(
    ['body', 'expected_status', 'expected_content'],
    [
        pytest.param(
            {
                'type': 'postgresql',
                'scope': {
                    'service_name': 'test_service',
                    'project_name': 'test_project',
                    'tplatform_namespace': 'namespace',
                },
                'environments': [
                    {
                        'environment': 'production',
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {
                                'key': 'shards',
                                'value': [
                                    {
                                        'user': 'taxi',
                                        'host': 'man.alive.net',
                                        'port': '3456',
                                        'db_name': 'db_name',
                                        'password': '12345',
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'environment': 'testing',
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {
                                'key': 'shards',
                                'value': [
                                    {
                                        'user': 'taxi-ro',
                                        'host': 'man.tst.alive.net',
                                        'port': 'tst12345',
                                        'db_name': 'db_tst_name',
                                        'password': '12345tst',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            {
                'key': 'POSTGRES_TEST_PROJECT_TEST_PROVIDER',
                'type': 'postgresql',
                'environments': [
                    {
                        'environment': 'production',
                        'yav_link': (
                            'https://yav.yandex-team.ru/secret/'
                            'secret_uuid_1/explore/version/version_uuid_1'
                        ),
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {
                                'key': 'shards',
                                'value': [
                                    {
                                        'db_name': 'db_name',
                                        'host': 'man.alive.net',
                                        'port': '3456',
                                        'user': 'taxi',
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'environment': 'testing',
                        'yav_link': (
                            'https://yav.yandex-team.ru/secret/'
                            'secret_uuid_1/explore/version/version_uuid_2'
                        ),
                        'fields': [
                            {'key': 'project', 'value': 'test_project'},
                            {'key': 'provider_name', 'value': 'test_provider'},
                            {
                                'key': 'shards',
                                'value': [
                                    {
                                        'db_name': 'db_tst_name',
                                        'host': 'man.tst.alive.net',
                                        'port': 'tst12345',
                                        'user': 'taxi-ro',
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'scope': {
                    'service_name': 'test_service',
                    'project_name': 'test_project',
                },
                'tvm_access_services': [],
                'use_in_services': [],
            },
        ),
        pytest.param(
            {
                'type': 'not_exists_type',
                'scope': {
                    'service_name': 'test_service',
                    'project_name': 'test_project',
                    'tplatform_namespace': 'namespace',
                },
                'environments': [],
            },
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': 'unknown secret type name: not_exists_type',
            },
        ),
        pytest.param(
            {'type': 'api_token', 'scope': {}, 'environments': []},
            400,
            {'message': 'Secret scope is empty', 'code': 'REQUEST_ERROR'},
        ),
        pytest.param(
            {
                'type': 'api_token',
                'scope': {
                    'service_name': 'test_service',
                    'project_name': 'test_project',
                    'tplatform_namespace': 'namespace',
                },
                'environments': [],
            },
            400,
            {
                'message': 'Cant create empty environments',
                'code': 'REQUEST_ERROR',
            },
        ),
        pytest.param(
            {
                'type': 'api_token',
                'scope': {
                    'service_name': 'test_service',
                    'project_name': 'test_project',
                    'tplatform_namespace': 'namespace',
                },
                'environments': [
                    {
                        'environment': 'production',
                        'fields': [
                            {'key': 'error_key', 'value': 'error_value'},
                        ],
                    },
                ],
            },
            400,
            {
                'message': (
                    'Data has bad format: \'project\' '
                    'is a required property'
                ),
                'code': 'REQUEST_ERROR',
            },
        ),
    ],
)
@pytest.mark.config(
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_v2_create_secret(
        taxi_strongbox_web,
        clowny_roles_grants,
        clown_roles_mock,
        vault_mockserver,
        mockserver,
        body,
        expected_status,
        expected_content,
):
    clowny_roles_grants.add_prod_editor(
        'login', {'type': 'project', 'id': 'meow'},
    )
    clowny_roles_grants.add_creator('login', {'type': 'project', 'id': 'meow'})
    clown_roles_mock()
    vault_session = vault_mockserver()

    response = await taxi_strongbox_web.post(
        '/v2/secret/create/',
        json=body,
        headers={
            'X-Yandex-Login': 'login',
            'X-YaTaxi-Api-Key': 'strongbox_api_token',
            'X-Idempotency-Token': 'strongbox_api_token',
        },
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_content
    if response.status == 200:
        assert vault_session.is_secret_created == 2
        assert vault_session.is_version_created == 2
        assert vault_session.is_role_added == 6
        assert vault_session.is_version_get == 2
        assert vault_session.versions == {
            'version_uuid_1': {
                'value': [
                    {'value': 'test_project', 'key': 'project'},
                    {'value': 'test_provider', 'key': 'provider_name'},
                    {'value': 'db_name', 'key': 'shards.0.db_name'},
                    {'value': 'man.alive.net', 'key': 'shards.0.host'},
                    {'value': '12345', 'key': 'shards.0.password'},
                    {'value': '3456', 'key': 'shards.0.port'},
                    {'value': 'taxi', 'key': 'shards.0.user'},
                ],
            },
            'version_uuid_2': {
                'value': [
                    {'value': 'test_project', 'key': 'project'},
                    {'value': 'test_provider', 'key': 'provider_name'},
                    {'value': 'db_tst_name', 'key': 'shards.0.db_name'},
                    {'value': 'man.tst.alive.net', 'key': 'shards.0.host'},
                    {'value': '12345tst', 'key': 'shards.0.password'},
                    {'value': 'tst12345', 'key': 'shards.0.port'},
                    {'value': 'taxi-ro', 'key': 'shards.0.user'},
                ],
            },
        }
