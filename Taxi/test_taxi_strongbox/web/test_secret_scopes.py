import pytest


def _secret_headers(login):
    headers = {'X-YaTaxi-Api-Key': 'strongbox_api_token'}
    if login:
        headers['X-Yandex-Login'] = login
    return headers


def _add_secret_body(scope, env):
    body = {
        'type': 'mongodb',
        'data': {
            'project': 'taxi',
            'provider_name': 'strongbox',
            'user': 'test_user',
            'password': '12345',
            'host': 'test_host',
            'port': 'test_port',
            'db_name': 'test-db',
        },
    }
    if scope:
        body['scope'] = scope
    if env:
        body['env'] = env
    return body


def _case(
        env,
        scope,
        login,
        expected_call,
        expected_status,
        use_clowny_roles: bool = False,
):
    return pytest.param(
        env,
        scope,
        login,
        expected_call,
        expected_status,
        use_clowny_roles,
        marks=[
            (
                pytest.mark.roles_features_on
                if use_clowny_roles
                else pytest.mark.roles_features_off
            )('strongbox_scopes_resolver'),
        ],
    )


@pytest.mark.features_on('auto_discover_scope', 'check_scope_by_clown')
@pytest.mark.parametrize('method', ['POST', 'PUT'])
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.config(
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
)
@pytest.mark.parametrize(
    [
        'env',
        'scope',
        'login',
        'expected_call',
        'expected_status',
        'use_clowny_roles',
    ],
    [
        _case(
            'unstable',
            {'project_name': 'taxi'},
            'meow',
            {
                'scope': {'type': 'project', 'project_name': 'taxi'},
                'logins': ['meow'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
        ),
        _case(
            'unstable',
            {'project_name': 'taxi'},
            'meow',
            {
                'scope': {'type': 'project', 'project_name': 'taxi'},
                'logins': ['meow'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
            use_clowny_roles=True,
        ),
        _case(
            'unstable',
            {},
            'login',
            {
                'scope': {'type': 'super'},
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
        ),
        _case(
            'unstable',
            None,
            'login',
            {
                'scope': {'type': 'super'},
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
        ),
        _case(
            'production',
            None,
            'login',
            {
                'scope': {'type': 'super'},
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                ],
                'limit': 1,
            },
            200,
        ),
        _case('production', None, None, None, 200),
        _case(
            'unstable',
            {'service_name': 'test', 'project_name': 'taxi'},
            'login',
            {
                'scope': {
                    'project_name': 'taxi',
                    'service_name': 'test',
                    'type': 'service',
                },
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
        ),
        _case(
            'unstable',
            {'service_name': 'test', 'project_name': 'taxi'},
            'login',
            {
                'scope': {
                    'project_name': 'taxi',
                    'service_name': 'test',
                    'type': 'service',
                },
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'nanny_admin_testing',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                    'strongbox_secrets_testing',
                ],
                'limit': 1,
            },
            200,
            use_clowny_roles=True,
        ),
        _case(
            'production',
            {'service_name': 'service', 'project_name': 'taxi'},
            'only-create',
            {
                'scope': {
                    'project_name': 'taxi',
                    'service_name': 'service',
                    'type': 'service',
                },
                'logins': ['only-create'],
                'roles': [
                    'nanny_admin_prod',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                ],
                'limit': 1,
            },
            200,
        ),
        _case(
            'production',
            {'service_name': 'service', 'project_name': 'taxi'},
            'only-create',
            {
                'scope': {
                    'project_name': 'taxi',
                    'service_name': 'service',
                    'type': 'service',
                },
                'logins': ['only-create'],
                'roles': [
                    'nanny_admin_prod',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                ],
                'limit': 1,
            },
            200,
            use_clowny_roles=True,
        ),
        _case(
            'production',
            None,
            'login',
            {
                'scope': {'type': 'super'},
                'logins': ['login'],
                'roles': [
                    'nanny_admin_prod',
                    'strongbox_secrets_creation',
                    'strongbox_secrets_prod',
                ],
                'limit': 1,
            },
            403,
        ),
    ],
)
async def test_add_secret_auth_scope(
        taxi_strongbox_web,
        clowny_roles_grants,
        vault_mockserver,
        method,
        clown_roles_mock,
        env,
        scope,
        login,
        expected_call,
        expected_status,
        add_secret,
        use_clowny_roles,
):
    clowny_roles_grants.add_creator('meow', {'id': 'taxi', 'type': 'project'})
    clowny_roles_grants.add_creator('login', {'id': 'taxi', 'type': 'project'})
    clowny_roles_grants.add_creator(
        'only-create', {'id': 'taxi', 'type': 'project'},
    )
    vault_mockserver()

    if expected_status == 403:
        handler = clown_roles_mock([])
    else:
        handler = clown_roles_mock()

    body = _add_secret_body(scope, env)
    headers = _secret_headers(login)
    response = await add_secret(method, headers, body)
    content = await response.json()
    assert response.status == expected_status, content
    if expected_status == 403:
        assert content == {
            'code': 'SCOPE_NOT_AUTHORIZED',
            'message': (
                f'Scope can not be authorized for {login} in {env}. '
                f'For more information, please follow the link: '
                f'https://wiki.yandex-team.ru/taxi/backend/architecture/'
                f'strongbox/#sozdanieiredaktirovaniesekretov'
            ),
        }
    if expected_call and not use_clowny_roles:
        assert handler.times_called == 1
        call = handler.next_call()['request']
        assert call.json == expected_call
    else:
        assert not handler.times_called


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[pytest.mark.roles_features_on('strongbox_scopes_resolver')],
            id='clowny-roles usage on',
        ),
        pytest.param(
            marks=[
                pytest.mark.roles_features_off('strongbox_scopes_resolver'),
            ],
            id='clowny-roles usage off',
        ),
    ],
)
@pytest.mark.features_on('auto_discover_scope', 'check_scope_by_clown')
@pytest.mark.parametrize('method', ['POST', 'PUT'])
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.config(
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'use_db_synced_values': True,
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
)
@pytest.mark.parametrize(
    ['env', 'scope', 'login', 'expected_status'],
    [
        ('unstable', {'project_name': 'taxi'}, 'some-mate', 200),
        ('production', {'project_name': 'taxi'}, 'some-mate', 403),
        (
            'production',
            {'service_name': 'service', 'project_name': 'taxi'},
            'only-create',
            200,
        ),
    ],
)
async def test_add_secret_auth_scope_db(
        taxi_strongbox_web,
        clowny_roles_grants,
        vault_mockserver,
        method,
        env,
        scope,
        login,
        expected_status,
        add_secret,
):
    vault_mockserver()
    body = _add_secret_body(scope, env)
    headers = _secret_headers(login)
    response = await add_secret(method, headers, body)
    content = await response.json()
    assert response.status == expected_status, content
    if expected_status == 403:
        assert content == {
            'code': 'SCOPE_NOT_AUTHORIZED',
            'message': (
                f'Scope can not be authorized for {login} in {env}. '
                f'For more information, please follow the link: '
                f'https://wiki.yandex-team.ru/taxi/backend/architecture/'
                f'strongbox/#sozdanieiredaktirovaniesekretov'
            ),
        }


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[pytest.mark.roles_features_on('strongbox_scopes_resolver')],
            id='clowny-roles usage on',
        ),
        pytest.param(
            marks=[
                pytest.mark.roles_features_off('strongbox_scopes_resolver'),
            ],
            id='clowny-roles usage off',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.config(
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'use_db_synced_values': True,
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
)
@pytest.mark.parametrize(
    ['login', 'expected_status'],
    [('some-mate', 200), ('some-mate-4', 403), ('only-create', 403)],
)
async def test_edit_secret_auth_scope_db(
        patch,
        web_app_client,
        clowny_roles_grants,
        vault_versions_mock,
        login,
        expected_status,
        edit_secret,
):
    body = {
        'key': 'SEARCHABLE_SECRET',
        'env': 'unstable',
        'data': {
            'project': 'taxi',
            'provider_name': 'service',
            'shards': [],
            'sentinels': [],
            'password': '123',
        },
    }
    vault_versions_mock('YAV_UUID_2')
    headers = _secret_headers(login)
    response = await edit_secret(headers, body)
    content = await response.json()
    assert response.status == expected_status, content
    if expected_status == 403:
        assert content == {
            'code': 'SCOPE_NOT_AUTHORIZED',
            'message': (
                f'Scope can not be authorized for {login} in unstable. '
                f'For more information, please follow the link: '
                f'https://wiki.yandex-team.ru/taxi/backend/architecture/'
                f'strongbox/#sozdanieiredaktirovaniesekretov'
            ),
        }
