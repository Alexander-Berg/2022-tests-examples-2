import pytest

ROLES_CUBE_NAMES = [
    'InternalAddNodesForService',
    'IdmAddNodesForService',
    'IdmRequestRolesForNewService',
]


@pytest.fixture(name='external_call_cube')
def _external_call_cube(mockserver):
    async def do_it(stage, cube, request_data):

        assert cube.name in ROLES_CUBE_NAMES
        response_data = {'status': 'success'}
        return mockserver.make_response(json=response_data)

    return do_it


@pytest.fixture(name='add_clowny_roles_cubes')
def _add_clowny_roles_cubes(task_processor):
    def _wrapper():
        roles_provider = task_processor.provider('clowny-roles')
        for cube_name in ROLES_CUBE_NAMES:
            task_processor.add_cube(
                cube_name,
                needed_parameters=['service_id'],
                optional_parameters=[],
                output_parameters=[],
                check_input_mappings=True,
                check_output_mappings=True,
                provider=roles_provider,
            )

    return _wrapper


# this test is just to check
# if old clown cubes are good enough for external TP
@pytest.mark.features_on(
    'permissions_cube_give_role_for_service',
    'permissions_cube_add_node_for_service',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_recipe(
        mockserver,
        load_yaml,
        task_processor,
        add_clowny_roles_cubes,
        mock_idm,
        run_job_common,
):
    add_clowny_roles_cubes()

    @mock_idm('/api/v1/batch/')
    def _idm_batch_handler(_):
        return {'responses': []}

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

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ProcessIdmForNewService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'service_id': 1}, initiator='testsuite',
    )
    await run_job_common(job)
