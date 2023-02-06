# pylint: disable=unused-variable
import pytest


@pytest.mark.parametrize(
    'cube_name',
    [
        'MetaCubeRemoveNannyBranches',
        'MetaCubeWaitForJob',
        'MetaCubeWaitForJobs',
        'MetaCubeCreateNannyService',
        'MetaCubeCreateDBService',
        'MetaCubeCreateDBBranches',
        'MetaCubeCreateFullDatabase',
        'MetaCubeDeployPlaceholders',
        'MetaCubeWaitForJobsCommon',
        'MetaCubeWaitForJobCommon',
        'MetaCubeWaitForAllJobs',
        'MetaCubeWaitForJobCompletion',
        'MetaCubeStartIdmProcessorForNewService',
        'MetaStartUpdateEntryPointSet',
        'MetaCubeStartChangeServiceInfoSystem',
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_meta_cubes.sql'])
async def test_task_processor_meta_cubes(
        mockserver,
        web_app_client,
        cube_name,
        load_json,
        patch,
        add_service,
        add_branch,
        login_mockserver,
        staff_mockserver,
        puncher_mockserver,
        mock_clowny_balancer,
        task_processor,
        mock_task_processor,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': 'robot-taxi-clown'}

    @patch('clownductor.internal.presets.presets.random_region')
    def random_region(context, count=1, project=None):
        return ['vla', 'man', 'sas'][0:count]

    login_mockserver()
    staff_mockserver()
    puncher_mockserver()
    service = await add_service('taxi', 'admin-data')
    await add_branch(
        {
            'service_id': service['id'],
            'env': 'stable',
            'direct_link': 'some-service-link',
            'name': 'stable',
        },
    )

    @mock_clowny_balancer('/v1/entry-points/list/')
    def _entry_points_list(request):
        if request.query.get('greater_than_id') == '1':
            return {'entry_points': []}
        if request.json['branch_ids'] != [1]:
            return {'entry_points': []}
        return {
            'entry_points': [
                {
                    'id': 1,
                    'namespace_id': 1,
                    'upstream_ids': [1],
                    'awacs_namespace': 'ns1',
                    'can_share_namespace': False,
                    'is_external': False,
                    'protocol': 'http',
                    'fqdn': 'test.fqdn',
                    'env': 'stable',
                    'created_at': '2021-01-13T00:00:00',
                    'updated_at': '2021-01-13T00:00:00',
                },
            ],
            'max_id': 1,
        }

    @mock_clowny_balancer('/v1/entry-points/delete/')
    async def _entry_point_delete(request):
        ep_id = request.json['id']
        if ep_id == 1:
            job = await task_processor.start_job(
                'EntryPointDelete', {}, '', '',
            )
            return {'job_id': job.id}
        return mockserver.make_response(status=404)

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _balancer_get_service(request):
        service_id = request.query['service_id']
        if service_id == '1':
            return {
                'namespaces': [
                    {
                        'id': 1,
                        'awacs_namespace': 'awacs-ns',
                        'env': 'stable',
                        'abc_quota_source': 'abc',
                        'is_external': False,
                        'is_shared': False,
                        'entry_points': [],
                    },
                ],
            }
        return mockserver.make_response(
            json={
                'code': 'NOT_FOUND',
                'message': f'balancer for service {service_id} not found',
            },
            status=404,
        )

    @mock_task_processor('/v1/jobs/retrieve/')
    def _jobs_retrieve(request):
        if request.json['job_id'] == 1:
            return {
                'job_info': {
                    'id': 1,
                    'job_vars': {},
                    'name': 'aaa',
                    'recipe_id': 1,
                    'status': 'success',
                    'created_at': 1234,
                },
                'tasks': [],
            }
        return mockserver.make_response(status=404)

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        if cube_name in ['AbcCubeChangeOwner']:
            service = await add_service('taxi', 'some_service')
            data_request['input_data']['service_id'] = service['id']

        if cube_name in ['MetaCubeCreateDBBranches']:
            db_type = data_request['input_data']['db_type']
            service = await add_service('taxi', f'some_service_{db_type}')
            data_request['input_data']['service_id'] = service['id']

        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']


@pytest.mark.pgsql('clownductor', files=['test_meta_cubes.sql'])
async def test_create_env_nanny_branches(
        call_cube_handle, load_json, patch, assert_meta_jobs, get_branch,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @patch('clownductor.internal.presets.presets.random_region')
    def random_region(context, count=1, project=None):
        return ['vla', 'man', 'sas'][0:count]

    cube_name = 'MetaCreateEnvNannyBranches'
    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        await call_cube_handle(cube_name, json_data)
        await assert_meta_jobs(json_data)
        await _check_branches(json_data, get_branch)


@pytest.mark.parametrize(
    ['filename'],
    (
        pytest.param(
            'MetaDeployEnvNannyPlaceholders.json', id='unstable_branch',
        ),
        pytest.param(
            'MetaDeployEnvNannyPlaceholders_tank.json', id='tank_branch',
        ),
    ),
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'task_processor_enabled': False,
        'nanny_add_image_and_sandbox_to_tank_branches': True,
    },
)
@pytest.mark.pgsql('clownductor', files=['test_meta_cubes.sql'])
async def test_deploy_env_nanny_placeholders(
        load_json, patch, assert_meta_jobs, call_cube_handle, filename,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    cube_name = 'MetaDeployEnvNannyPlaceholders'
    json_datas = load_json(filename)
    for json_data in json_datas:
        await call_cube_handle(cube_name, json_data)
        await assert_meta_jobs(json_data)


async def _check_branches(json_data, get_branch):
    for branch_expected in json_data['branches_expected']:
        branch = await get_branch(branch_expected['id'])
        assert len(branch) == 1
        fields = ['env', 'id', 'service_id', 'name']
        assert {field: branch[0][field] for field in fields} == branch_expected


@pytest.mark.parametrize(
    'new_regions_flow',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.features_off('service_creation_available_regions'),
            ],
            id='old_regions_flow',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.features_on('service_creation_available_regions'),
            ],
            id='new_regions_flow',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_full_nanny_branches(
        load_json,
        call_cube_handle,
        assert_meta_jobs,
        patch,
        mock_random_regions,
        new_regions_flow,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @patch('random.choice')
    def _random_choice(regions):
        return regions[0]

    if new_regions_flow:
        file_name = 'CreateFullNannyBranchesNewRegions.json'
    else:
        file_name = 'CreateFullNannyBranches.json'
    json_data = load_json(file_name)

    cube_name = 'MetaCreateFullNannyBranches'
    await call_cube_handle(cube_name, json_data)
    await assert_meta_jobs(json_data)
    assert len(_random_choice.calls) == 1
    assert len(create_comment.calls) == 1
    assert len(mock_random_regions.calls) == 3


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_meta_env_create_unstable_balancers(
        load_json,
        call_cube_handle,
        assert_meta_jobs,
        patch,
        mock_clowny_balancer,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _service_get(request):
        return {
            'namespaces': [
                {
                    'id': 1,
                    'awacs_namespace': 'service_awacs_namespace',
                    'env': 'testing',
                    'abc_quota_source': 'abc_quota_source',
                    'is_external': False,
                    'is_shared': False,
                    'entry_points': [
                        {
                            'id': 1,
                            'protocol': 'http',
                            'dns_name': 'service_dns',
                            'is_external': False,
                            'upstreams': [],
                            'env': 'testing',
                        },
                    ],
                },
            ],
        }

    @mock_clowny_balancer('/v1/entry-points/create/')
    def _entry_points_create(request):
        return {'job_id': 1}

    file_name = 'MetaEnvCreateBalancers.json'
    json_data = load_json(file_name)

    cube_name = 'MetaEnvCreateBalancers'
    await call_cube_handle(cube_name, json_data)
    await assert_meta_jobs(json_data)

    assert len(create_comment.calls) == 1
    assert _service_get.times_called == 1
    assert _entry_points_create.times_called == 1


@pytest.mark.pgsql('clownductor', files=['test_create_tank_branch.sql'])
async def test_meta_create_tank_branch(
        load_json, call_cube_handle, assert_meta_jobs,
):

    file_name = 'MetaCreateTankBranch.json'
    json_data = load_json(file_name)

    cube_name = 'MetaCreateTankBranch'
    for case in json_data:
        await call_cube_handle(cube_name, case)
        await assert_meta_jobs(case)


@pytest.mark.pgsql('clownductor', files=['test_meta_cubes.sql'])
async def test_meta_load_host(
        load_json,
        call_cube_handle,
        assert_meta_jobs,
        task_processor,
        mock_internal_tp,
):

    file_name = 'MetaLoadHost.json'
    json_data = load_json(file_name)

    cube_name = 'MetaLoadHost'
    for case in json_data:
        await call_cube_handle(cube_name, case)
        await assert_meta_jobs(case)


@pytest.mark.pgsql('clownductor', files=['test_delete_ep.sql'])
async def test_meta_env_delete_entrypoint(
        load_json,
        call_cube_handle,
        assert_meta_jobs,
        patch,
        mock_clowny_balancer,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @mock_clowny_balancer('/v1/entry-points/delete/')
    def _entry_points_create(request):
        return {'job_id': 1}

    @mock_clowny_balancer('/v1/entry-points/list/')
    def _entrypoints_list(request):
        greater_than_id = request.query.get('greater_than_id')
        body = request.json
        branch_ids = body.get('branch_ids', [])
        if greater_than_id == '10' or 2 in branch_ids:
            return {'entry_points': []}
        if branch_ids == [3]:
            return {
                'entry_points': [
                    {
                        'awacs_namespace': 'ns1',
                        'can_share_namespace': False,
                        'created_at': '2021-01-13T00:00:00',
                        'env': 'stable',
                        'fqdn': 'fqdn.net',
                        'id': 2,
                        'is_external': False,
                        'namespace_id': 1,
                        'protocol': 'https',
                        'updated_at': '2021-01-13T00:00:00',
                        'upstream_ids': [1, 2],
                    },
                ],
                'max_id': 10,
            }
        return {
            'entry_points': [
                {
                    'awacs_namespace': 'ns1',
                    'can_share_namespace': False,
                    'created_at': '2021-01-13T00:00:00',
                    'env': 'unstable',
                    'fqdn': 'fqdn.net',
                    'id': 1,
                    'is_external': False,
                    'namespace_id': 1,
                    'protocol': 'https',
                    'updated_at': '2021-01-13T00:00:00',
                    'upstream_ids': [1, 2],
                },
            ],
            'max_id': 10,
        }

    cube_name = 'MetaEnvDeleteEntrypoint'
    json_data = load_json(f'{cube_name}.json')
    for case in json_data:
        await call_cube_handle(cube_name, case)
        await assert_meta_jobs(case)

    assert len(create_comment.calls) == 1
    assert _entrypoints_list.times_called == 5
    assert _entry_points_create.times_called == 1
