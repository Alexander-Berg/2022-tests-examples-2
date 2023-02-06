import pytest

from . import constants


@pytest.mark.features_on('auto_discover_scope', 'check_scope_by_clown')
@pytest.mark.usefixtures('patch_conductor_session')
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
@pytest.mark.parametrize('method', ['POST', 'PUT'])
@pytest.mark.parametrize(
    [
        'headers',
        'json',
        'expected_status',
        'expected_json',
        'is_external_request',
    ],
    [
        (
            {'X-YaTaxi-Api-Key': 'foo'},
            {},
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
            True,
        ),
        (
            {
                'X-YaTaxi-Api-Key': 'strongbox_api_token',
                'X-Idempotency- Token': 'idempotency_token_2',
            },
            {
                'env': 'unstable',
                'type': 'mongodb',
                'scope': {'project_name': 'taxi'},
                'data': constants.MONDO_DATA,
            },
            200,
            {
                'name': 'MONGODB_TAXI_STRONGBOX',
                'yav_secret_uuid': 'secret_uuid_1',
                'yav_version_uuid': 'version_uuid_1',
            },
            True,
        ),
        (
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'env': 'testing',
                'type': 'mongodb',
                'data': constants.MONDO_DATA,
            },
            409,
            {
                'code': 'SECRET_IS_ALREADY_REGISTERED',
                'message': (
                    'secret with name MONGODB_TAXI_STRONGBOX '
                    'for env \'testing\' is already registered'
                ),
            },
            True,
        ),
        (
            # data without 'project' field
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'env': 'testing',
                'type': 'mongodb',
                'data': {
                    'provider_name': 'strongbox',
                    'user': 'test_user',
                    'password': '12345',
                    'host': 'test_host',
                    'port': 'test_port',
                    'db_name': 'test-db',
                },
            },
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Data has bad format: \'project\' is a required property'
                ),
            },
            True,
        ),
        (
            {
                'X-YaTaxi-Api-Key': 'strongbox_api_token',
                'X-Idempotency-Token': 'idempotency_token_1',
            },
            {
                'env': 'testing',
                'type': 'mongodb',
                'data': constants.MONDO_DATA,
            },
            200,
            {
                'name': 'MONGODB_TAXI_STRONGBOX',
                'yav_secret_uuid': 'YAV_UUID_2',
                'yav_version_uuid': 'VERSION_UUID_2',
            },
            False,
        ),
    ],
)
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    STRONGBOX_PROJECT_YAV_ROLES={'enabled': False},
                ),
            ],
            id='roles_off',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    STRONGBOX_PROJECT_YAV_ROLES={
                        'enabled': True,
                        'projects_roles': {
                            '__default__': {
                                'owner_abc_id': 4012,
                                'reader_abc_ids': [],
                            },
                            'taxi': {
                                'owner_abc_id': 3012,
                                'reader_abc_ids': [1234],
                            },
                        },
                    },
                ),
            ],
            id='roles_on',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_add_secret(
        taxi_strongbox_web,
        web_context,
        clowny_roles_grants,
        vault_mockserver,
        headers,
        json,
        expected_status,
        expected_json,
        is_external_request,
        method,
        add_secret,
        added_roles_from_secdist,
):
    vault_session = vault_mockserver(constants.VAULT_VERSIONS)
    response = await add_secret(method, headers, json)
    if method == 'PUT' and expected_status == 409:
        assert response.status == 200
        expected_json = None
    else:
        assert response.status == expected_status
    if expected_json is not None:
        assert expected_json == await response.json()
    if (
            response.status == 200
            and expected_status != 409
            and is_external_request
    ):
        assert vault_session.is_secret_created
        assert vault_session.is_version_created
        assert vault_session.is_role_added
        config = web_context.config
        roles_on = config.STRONGBOX_PROJECT_YAV_ROLES['enabled']
        added_roles = added_roles_from_secdist
        if roles_on and json.get('scope', {}).get('project_name') == 'taxi':
            added_roles = [
                {'abc_id': 1234, 'role': 'READER'},
                {'abc_id': 3012, 'role': 'OWNER'},
            ]
        assert vault_session.added_roles == added_roles
