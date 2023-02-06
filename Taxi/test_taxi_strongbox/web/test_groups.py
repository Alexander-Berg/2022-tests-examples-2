# pylint: disable=inconsistent-return-statements,unused-variable
# pylint: disable=redefined-outer-name
import pytest

from taxi_strongbox.components.sessions import conductor_session as cs


@pytest.fixture
def patch_conductor_session(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(cs.ConductorSession.base_url, 'GET')
    def request(method, url, *args, **kwargs):
        if 'groups/taxi:' in url:
            return response_mock()
        return response_mock(status=404)


@pytest.mark.usefixtures('patch_conductor_session')
@pytest.mark.parametrize(
    ['headers', 'json', 'group_source', 'expected_status', 'expected_json'],
    [
        (
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'name': 'taxi:imports2:unstable',
                'env': 'unstable',
                'service_name': 'strongbox',
            },
            None,
            200,
            {
                'yav_secret_uuid': 'secret_uuid_1',
                'yav_version_uuid': 'version_uuid_1',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'name': 'taxi:clowny-smth:unstable',
                'env': 'unstable',
                'service_name': 'clowny-smth',
            },
            'clownductor',
            200,
            {
                'yav_secret_uuid': 'secret_uuid_1',
                'yav_version_uuid': 'version_uuid_1',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'foo'},
            {
                'name': 'taxi:imports:unstable',
                'env': 'unstable',
                'service_name': 'strongbox',
            },
            None,
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
        ),
        (
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'name': 'taxi-error:imports:unstable',
                'env': 'unstable',
                'service_name': 'strongbox',
            },
            None,
            400,
            {
                'code': 'CONDUCTOR_GROUP_IS_NOT_FOUND',
                'message': (
                    'group taxi-error:imports:unstable '
                    'is not found in Conductor'
                ),
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'strongbox_api_token'},
            {
                'name': 'taxi:imports:unstable',
                'env': 'unstable',
                'service_name': 'strongbox',
            },
            None,
            409,
            {
                'code': 'GROUP_IS_ALREADY_REGISTERED',
                'message': 'group taxi:imports:unstable is already registered',
            },
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
                            'some-project': {
                                'owner_abc_id': 1012,
                                'reader_abc_ids': [1112],
                            },
                        },
                    },
                ),
            ],
            id='roles_on',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_groups.sql'])
async def test_add_group(
        web_app_client,
        vault_mockserver,
        headers,
        json,
        expected_status,
        expected_json,
        added_roles_from_secdist,
        group_source,
        patch_clownductor_session,
):
    params = {}
    vault_session = vault_mockserver()
    if group_source:
        params['group_source'] = group_source
    patch_clownductor_session([{'id': 111, 'name': 'unstable'}])
    response = await web_app_client.post(
        '/v1/groups/', headers=headers, json=json, params=params,
    )
    content = await response.json()
    assert response.status == expected_status, content
    if expected_json is not None:
        assert expected_json == content
    if response.status == 200:
        assert vault_session.is_secret_created
        assert vault_session.is_version_created
        assert vault_session.is_role_added
        config = web_app_client.app['context'].config
        roles_on = config.STRONGBOX_PROJECT_YAV_ROLES['enabled']
        added_roles = added_roles_from_secdist
        if roles_on:
            added_roles = [{'abc_id': 4012, 'role': 'OWNER'}]
        assert vault_session.added_roles == added_roles


@pytest.mark.parametrize(
    ['name', 'expected_status', 'expected_json'],
    [
        (
            'taxi:imports:unstable',
            200,
            {
                'yav_secret_uuid': 'auth_secret_uuid_1',
                'yav_version_uuid': 'auth_version_uuid_1',
                'env': 'unstable',
                'service_name': 'imports',
            },
        ),
        (
            'taxi_unknown',
            404,
            {
                'code': 'GROUP_IS_NOT_FOUND',
                'message': 'group taxi_unknown is not found',
            },
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_groups.sql'])
async def test_get_group(
        web_app_client,
        patch_conductor_session,
        name,
        expected_status,
        expected_json,
):
    response = await web_app_client.get(f'/v1/groups/', params={'name': name})
    assert response.status == expected_status
    if expected_json is not None:
        assert expected_json == await response.json()


@pytest.mark.pgsql('strongbox', files=['test_groups.sql'])
async def test_rename_group(
        web_app_client, vault_mockserver, patch_clownductor_session,
):
    clown_patch = patch_clownductor_session([{'id': 111, 'name': 'unstable'}])
    old_name = 'taxi:strongbox:unstable'
    new_name = 'taxi-infra:strongbox:unstable'
    vault_mockserver()

    response = await web_app_client.post(
        '/v1/groups/',
        params={'group_source': 'clownductor'},
        headers={'X-YaTaxi-Api-Key': 'strongbox_api_token'},
        json={
            'name': old_name,
            'env': 'unstable',
            'service_name': 'strongbox',
        },
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/groups/move/',
        headers={'X-YaTaxi-Api-Key': 'strongbox_api_token'},
        json={'name': old_name, 'new_project': 'taxi-infra'},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/groups/', params={'name': new_name},
    )
    assert response.status == 200
    assert len(clown_patch.calls) == 6
