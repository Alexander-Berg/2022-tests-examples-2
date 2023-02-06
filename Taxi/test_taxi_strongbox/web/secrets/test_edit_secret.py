import pytest


def _assert_edit_secret_call(mock, data):
    if not data:
        assert not mock.has_calls
        return
    assert mock.times_called == 1
    call = mock.next_call()
    assert call['request'].json.keys() == {'value'}
    values = call['request'].json['value']
    data = data.copy()
    for value in values:
        key = value['key']
        assert key in data, key
        assert value['value'] == data.pop(key), key
    assert not data


@pytest.mark.features_on('auto_discover_scope', 'check_scope_by_clown')
@pytest.mark.parametrize(
    'use_clowny_roles',
    [
        pytest.param(
            True,
            marks=[pytest.mark.roles_features_on('strongbox_scopes_resolver')],
            id='clowny-roles usage on',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.roles_features_off('strongbox_scopes_resolver'),
            ],
            id='clowny-roles usage off',
        ),
    ],
)
@pytest.mark.parametrize(
    ['body', 'expected_status', 'expected_content', 'roles_times_called'],
    [
        (
            {
                'key': 'TEST_2',
                'env': 'unstable',
                'scope': {'project_name': 'meow', 'service_name': 'service'},
                'data': {
                    'project': 'taxi',
                    'provider_name': 'service',
                    'user': 'test',
                    'host': 'test',
                    'port': '5432',
                    'db_name': 'test',
                    'password': 'test',
                },
            },
            200,
            {
                'secret': {
                    'env': 'unstable',
                    'key': 'TEST_2',
                    'scope': {
                        'project_name': 'meow',
                        'service_name': 'service',
                    },
                    'type': 'mongodb',
                    'yav_secret_uuid': 'YAV_UUID_2',
                    'yav_version_uuid': 'version_uuid_1',
                },
            },
            2,
        ),
        (
            {
                'key': 'TEST_2',
                'env': 'unstable',
                'scope': {'project_name': 'meow', 'service_name': 'service'},
            },
            200,
            {
                'secret': {
                    'env': 'unstable',
                    'key': 'TEST_2',
                    'scope': {
                        'project_name': 'meow',
                        'service_name': 'service',
                    },
                    'type': 'mongodb',
                    'yav_secret_uuid': 'YAV_UUID_2',
                    'yav_version_uuid': 'VERSION_UUID_2',
                },
            },
            2,
        ),
        (
            {
                'key': 'TEST_2',
                'env': 'unstable',
                'data': {
                    'project': 'taxi',
                    'provider_name': 'service',
                    'user': 'test',
                    'host': 'test',
                    'port': '5432',
                    'db_name': 'test',
                    'password': 'test',
                },
            },
            200,
            {
                'secret': {
                    'env': 'unstable',
                    'key': 'TEST_2',
                    'scope': {'project_name': 'meow'},
                    'type': 'mongodb',
                    'yav_secret_uuid': 'YAV_UUID_2',
                    'yav_version_uuid': 'version_uuid_1',
                },
            },
            1,
        ),
        (
            {
                'key': 'TEST_NOT_FOUND',
                'env': 'unstable',
                'scope': {'project_name': 'meow'},
            },
            404,
            {
                'code': 'SECRET_NOT_FOUND',
                'message': 'Secret TEST_NOT_FOUND not found in unstable',
            },
            1,
        ),
        (
            {
                'key': 'TEST_2',
                'env': 'unstable',
                'scope': {'service_name': '123'},
            },
            400,
            {
                'code': 'BAD_SCOPE',
                'message': 'Service name must be defined with project name',
            },
            0,
        ),
        (
            {'key': 'TEST_2', 'env': 'unstable'},
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': 'No parameter to edit was passed',
            },
            0,
        ),
        (
            {'key': 'TEST_2', 'env': 'unstable', 'data': {}},
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Data has bad format: \'project\' is a required property'
                ),
            },
            1,
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
async def test_edit_secret(
        web_app_client,
        clowny_roles_grants,
        vault_versions_mock,
        body,
        expected_status,
        expected_content,
        clown_roles_mock,
        roles_times_called,
        use_clowny_roles,
):
    clowny_roles_grants.add_prod_editor(
        'login', {'type': 'project', 'id': 'meow'},
    )
    clowny_roles_grants.add_creator('login', {'type': 'project', 'id': 'meow'})
    mock = vault_versions_mock('YAV_UUID_2')
    handler = clown_roles_mock()
    response = await web_app_client.post(
        '/v1/secrets/edit/',
        headers={
            'X-YaTaxi-Api-Key': 'strongbox_api_token',
            'X-Yandex-Login': 'login',
        },
        json=body,
    )
    _assert_edit_secret_call(mock, body.get('data'))
    content = await response.json()
    assert response.status == expected_status, content
    if expected_status == 200:
        assert content['secret'].pop('updated')
    assert content == expected_content
    assert handler.times_called == (
        roles_times_called if not use_clowny_roles else 0
    )
