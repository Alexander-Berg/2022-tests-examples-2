import pytest

from clowny_roles.crontasks import sync_roles

CUBE_NAME = 'IdmAddNodesForService'


@pytest.mark.roles_features_on('idm_add_nodes_for_new_service')
async def test_cube(load_yaml, mock_idm_batch, web_context, call_cube):
    _batch_handler = mock_idm_batch()

    await sync_roles.SyncRolesTask(web_context).process()
    response = await call_cube(CUBE_NAME, {'clown_service_id': 1})
    assert response == {'status': 'success'}

    requests = []
    while _batch_handler.has_calls:
        requests.append(_batch_handler.next_call())
    assert len(requests) == 1
    assert requests[0]['request'].json == load_yaml('idm_request.yaml')


@pytest.mark.roles_features_on('idm_add_nodes_for_new_service')
async def test_cube_with_fails(mock_idm_batch, web_context, call_cube):
    idm_responses_by_id = {
        (
            'namespace+taxi+namespace_role+project_roles+project+'
            'prj=1+project_role+service_roles+service+srv=1-'
            'srv=1-'
            'None'
        ): {
            'body': {'message': 'Узел уже есть на этом уровне дерева'},
            'status_code': 400,
        },  # error but ok
        (
            'namespace+taxi+namespace_role+project_roles+project+'
            'prj=1+project_role+service_roles+service+srv=1+'
            'service_role+subsystem_internal+service_subsystem_internal+'
            'test_admin-'
            'test_admin-'
            'internal'
        ): {
            'message': 'some internal error',
            'status_code': 500,
        },  # retryable error
    }
    _batch_handler = mock_idm_batch(idm_responses_by_id)

    await sync_roles.SyncRolesTask(web_context).process()
    response = await call_cube(CUBE_NAME, {'clown_service_id': 1})
    assert response == {'status': 'success'}

    requests = []
    while _batch_handler.has_calls:
        requests.append(_batch_handler.next_call())
    assert len(requests) == 2
    assert [len(x['request'].json) for x in requests] == [6, 1]
    assert not idm_responses_by_id
