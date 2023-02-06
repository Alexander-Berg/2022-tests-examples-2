import uuid

import pytest

from testsuite.utils import matching


@pytest.mark.parametrize(
    'cube_name',
    [
        'InternalCubeUpdateService',
        'InternalCubeUpdateBranch',
        'InternalCubeUpdateDirectLink',
        'InternalCubeInitBalancerAlias',
        'InternalGenerateYavSecret',
        'InternalWaitForService',
        'InternalGetLock',
        'InternalBatchGetLock',
        'InternalReleaseLock',
        'InternalBatchReleaseLock',
        'InternalGenerateArtifactName',
        'InternalGetBranchInformation',
        'InternalGetServiceInformation',
        'ClearJobsIdempotencyTokensByTokens',
        'ClearJobsIdempotencyTokensByIds',
        'InternalCubeSleep',
        'InternalJobGetInformation',
        'InternalJobBranchSetDeleted',
        'InternalJobServiceSetDeleted',
        'InternalServiceYamlToParameters',
        'InternalCubeUpdateServiceConfigs',
    ],
)
@pytest.mark.usefixtures('mock_internal_tp')
async def test_internal_cubes(
        web_app_client,
        web_context,
        cube_name,
        load_json,
        login_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        nanny_mockserver,
        nanny_yp_mockserver,
        yav_mockserver,
        pgsql,
):
    login_mockserver()
    staff_mockserver()
    nanny_yp_mockserver()
    yav_mockserver()

    service = await add_service(
        'taxi', 'some_service', direct_link='test_direct',
    )
    branch_id = await add_nanny_branch(
        service['id'], 'new-branch', direct_link='path',
    )

    await web_context.service_manager.hosts.upsert(
        {
            'name': 'some-host',
            'datacenter': 'some-datacenter',
            'branch_id': branch_id,
        },
    )

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
        if cube_name == 'InternalCubeUpdateServiceConfigs':
            cursor = pgsql['clownductor'].cursor()
            query = (
                'select name, libraries, plugins, is_service_yaml '
                'from clownductor.configs;'
            )
            cursor.execute(query)
            configs_info = [
                {
                    'name': row[0],
                    'libraries': row[1],
                    'plugins': row[2],
                    'is_service_yaml': row[3],
                }
                for row in cursor
            ]
            assert data_request['input_data']['configs_info'] == configs_info


async def test_generate_idempotency_token(call_cube_handle):
    await call_cube_handle(
        'InternalGenerateIdempotencyToken',
        {
            'content_expected': {
                'payload': {'uuid_token': matching.uuid_string},
                'status': 'success',
            },
            'data_request': {
                'input_data': {},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )


async def test_cube_with_external_entities(call_cube_handle, patch_method):
    class BreakRun(Exception):
        pass

    @patch_method(
        'clownductor.internal.tasks.cubes.cubes_internal.'
        'InternalGenerateIdempotencyToken.update_from_handler',
    )
    async def _update_from_handler(self, input_data, external_entities):
        try:
            with self.context.external_entities.external_entity_scope(
                    **external_entities,
            ):
                current_external_entities = (
                    self.context.external_entities.get_external_entities()
                )
                assert current_external_entities == {'service': '1'}
                additional_data = {'other': '222'}
                self.context.external_entities.add_external_entities(
                    **additional_data,
                )
                external_entities = (
                    self.context.external_entities.get_external_entities()
                )
                assert external_entities == {'service': '1', 'other': '222'}
                self.data['payload'] = {'uuid_token': uuid.uuid4().hex}
                self.succeed()
        except BreakRun:
            return

    await call_cube_handle(
        'InternalGenerateIdempotencyToken',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
                'external_entities': {'service': '1'},
            },
        },
    )
