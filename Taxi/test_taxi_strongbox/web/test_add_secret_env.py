import pytest


@pytest.mark.parametrize(
    ['body', 'expected_status', 'expected_content'],
    [
        pytest.param(
            {
                'key': 'SEARCH_ABLE_SECRET_2',
                'env': 'unstable',
                'data': {
                    'project': 'any_project',
                    'provider_name': 'any_name',
                    'value': '"secret_token"',
                },
            },
            200,
            {
                'secret': {
                    'env': 'unstable',
                    'key': 'SEARCH_ABLE_SECRET_2',
                    'scope': {
                        'project_name': 'taxi-infra',
                        'service_name': 'service-2',
                    },
                    'type': 'api_token',
                    'yav_secret_uuid': 'secret_uuid_1',
                    'yav_version_uuid': 'version_uuid_1',
                },
            },
            id='add new env',
        ),
        pytest.param(
            {
                'key': 'SEARCH_ABLE_SECRET_2',
                'env': 'testing',
                'data': {
                    'project': 'any_project',
                    'provider_name': 'any_name',
                    'value': '"secret_token"',
                },
            },
            409,
            {
                'code': 'SECRET_IS_ALREADY_REGISTERED',
                'message': (
                    'secret with name SEARCH_ABLE_SECRET_2 for '
                    'env \'testing\' is already registered'
                ),
            },
            id='add exist env',
        ),
        pytest.param(
            {
                'key': 'NOT_FOUND_KEY',
                'env': 'testing',
                'data': {
                    'project': 'any_project',
                    'provider_name': 'any_name',
                    'value': '"secret_token"',
                },
            },
            404,
            {
                'code': 'SECRET_NOT_FOUND',
                'message': 'Secret: NOT_FOUND_KEY is not found',
            },
            id='not found secret',
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
async def test_add_secret_env(
        taxi_strongbox_web,
        clowny_roles_grants,
        vault_mockserver,
        clown_roles_mock,
        body,
        expected_status,
        expected_content,
):

    clowny_roles_grants.add_prod_editor(
        'login', {'type': 'project', 'id': 'meow'},
    )
    clowny_roles_grants.add_creator('login', {'type': 'project', 'id': 'meow'})
    clown_roles_mock()
    vault_mockserver()

    response = await taxi_strongbox_web.post(
        '/v1/secrets/env/add/',
        json=body,
        headers={
            'X-Yandex-Login': 'login',
            'X-YaTaxi-Api-Key': 'strongbox_api_token',
        },
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_content
