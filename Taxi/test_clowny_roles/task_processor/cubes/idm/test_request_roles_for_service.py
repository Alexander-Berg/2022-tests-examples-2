import pytest

CUBE_NAME = 'IdmRequestRolesForNewService'


@pytest.fixture(name='common_mocks')
async def _common_mocks(mockserver, add_subsystem, add_role):
    internal_subsystem_id = await add_subsystem('internal')
    await add_role(
        'nanny_admin_testing', 'srv-1-slug', 'service', internal_subsystem_id,
    )
    await add_role(
        'strongbox_secrets_creation',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )
    await add_role(
        'mdb_cluster_ro_access',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )
    await add_role(
        'deploy_approve_programmer',
        'srv-1-slug',
        'service',
        internal_subsystem_id,
    )

    @mockserver.json_handler('/client-staff/v3/persons')
    def _persons_handler(request):
        if request.query.get('_one') == '1':
            return {
                'department_group': {'department': {'url': 'department_url'}},
            }
        return {
            'result': [
                {
                    'chief': {'login': 'chief-1'},
                    'login': request.query['login'],
                },
            ],
        }

    @mockserver.json_handler('/client-staff/v3/groups')
    def _groups_handler(_):
        return {'result': [{'id': 1}]}


@pytest.mark.roles_features_on('idm_request_roles_for_new_service')
@pytest.mark.usefixtures('common_mocks')
async def test_cube(load_yaml, mock_idm_batch, web_context, call_cube):
    _batch_handler = mock_idm_batch()

    response = await call_cube(CUBE_NAME, {'clown_service_id': 1})
    assert response == {'status': 'success'}

    requests = []
    while _batch_handler.has_calls:
        requests.append(_batch_handler.next_call())
    assert len(requests) == 1
    assert requests[0]['request'].json == load_yaml('idm_request.yaml')


@pytest.mark.roles_features_on('idm_request_roles_for_new_service')
@pytest.mark.usefixtures('common_mocks')
async def test_cube_with_fails(
        mock_idm_batch, web_context, add_subsystem, add_role, call_cube,
):
    idm_responses_by_id = {
        (
            'taxi+project_roles+prj=1+'
            'service_roles+srv=1+'
            'subsystem_internal+deploy_approve_programmer-'
            'None-'
            'chief=1'
        ): {
            'body': {
                'message': (
                    '...'
                    'в системе "Платформа Клоундуктор" в состоянии "Выдана"'
                    '...'
                ),
            },
            'status_code': 400,
        },
        (
            'taxi+project_roles+prj=1+'
            'service_roles+srv=1+'
            'subsystem_internal+mdb_cluster_ro_access-'
            '1-'
            'None'
        ): {'body': {'message': 'internal error'}, 'status_code': 500},
    }
    _batch_handler = mock_idm_batch(idm_responses_by_id)

    response = await call_cube(CUBE_NAME, {'clown_service_id': 1})
    assert response == {'status': 'success'}

    requests = []
    while _batch_handler.has_calls:
        requests.append(_batch_handler.next_call())
    assert len(requests) == 2
    assert [len(x['request'].json) for x in requests] == [4, 1]
    assert not idm_responses_by_id
