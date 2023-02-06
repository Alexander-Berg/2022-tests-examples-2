import pytest


@pytest.fixture(name='recipe_mocks')
def _recipe_mocks(mockserver):
    @mockserver.json_handler('/client-awacs/api/ListL3Balancers/')
    def _l3_balancers_list_mock(_):
        return {
            'l3_balancers': [
                {'meta': {'id': 'abc'}, 'spec': {'l3mgr_service_id': '123'}},
            ],
        }

    @mockserver.json_handler('/l3mgr/service/123')
    def _l3mgr_service_mock(_):
        return {'config': {'vs_id': ['1', '2']}}

    @mockserver.json_handler(
        r'/l3mgr/service/123/vs/(?P<vs_id>\d+)/rsstate', regex=True,
    )
    def _l3mgr_rsstate_mock(_, vs_id):
        return {
            'objects': [
                {'state': 'ACTIVE', 'rs': {'fqdn': 'pod-1.sas.blah'}},
                {'state': 'ACTIVE', 'rs': {'fqdn': 'pod-2.sas.blah'}},
            ],
        }


@pytest.fixture(name='clown_cube_caller')
def _clown_cube_caller(mockserver):

    _pods = {
        'pod-1': {
            'pod_info': {
                'cpu': 2000,
                'mem': 2048,
                'network': '_SOME_',
                'logs_quota': 50,
                'root_fs_quota_mb': 10,
                'root_bandwidth_guarantee_mb_per_sec': 0,
                'root_bandwidth_limit_mb_per_sec': 0,
                'root_storage_class': 'hdd',
                'work_dir_quota': 20,
                'persistent_volumes': [],
                'sysctl': 123,
            },
        },
    }
    _snapshots = {'snapshot-1': {'pods': ['pod-1'], 'status': 'active'}}

    async def _do_it(cube, stage, request_data):
        input_data = request_data['input_data']
        response = {'status': 'success'}
        if cube.name == 'NannyGetPods':
            response.update(
                payload={
                    'pod_ids': list(_pods.keys()),
                    'region': 'sas',
                    'real_nanny_name': input_data['nanny_name'],
                },
            )
        if cube.name == 'NannyGetPodsInfo':
            response.update(
                payload={
                    'pod_info': _pods[input_data['pod_ids'][0]]['pod_info'],
                },
            )
        if cube.name == 'NannyAllocateAdditionalPods':
            _pods['pod-2'] = _pods['pod-1']['pod_info'].copy()
            response.update(payload={'new_pod_ids': ['pod-2']})
        if cube.name == 'NannyCubeAddPodsToDeploy':
            _snapshots['snapshot-2'] = {
                'pods': sorted(_pods.keys()),
                'status': 'ready',
            }
            response.update(payload={'snapshot_id': 'snapshot-2'})
        if cube.name == 'NannyCubeDeploySnapshot':
            _snapshots['snapshot-1']['status'] = 'ready'
            _snapshots['snapshot-2']['status'] = 'active'
        if cube.name == 'NannyCubeWaitForDeploy':
            if _snapshots[input_data['snapshot_id']]['status'] != 'active':
                response['status'] = 'in_progress'
            else:
                response.update(
                    payload={'active_snapshot_id': input_data['snapshot_id']},
                )
        if cube.name == 'NannyGetNewestPod':
            response.update(payload={'newest_pod_id': 'pod-2', 'region': ''})
        if cube.name == 'NannyPrepareAllocationRequest':
            response.update(
                payload={
                    'original_allocation_request': {},
                    'prepared_allocation_request': {},
                },
            )
        if cube.name == 'ClownNannyReallocatePods':
            response.update(payload={'reallocation_id': 'reallocation_id'})

        return mockserver.make_response(json=response)

    return _do_it


@pytest.mark.usefixtures('recipe_mocks', 'clown_cube_caller')
async def test_recipe(load_yaml, task_processor, run_job_common):
    recipe = task_processor.load_recipe(
        load_yaml('BalancerEnsureDoublePods.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'balancer_nanny_service': (
                'rtc_balancer_clowny-balancer_taxi_yandex_net_sas'
            ),
            'awacs_namespace': 'clowny-balancer.taxi.yandex.net',
        },
        initiator='clowny-balancer',
    )
    await run_job_common(job, sleep_is_expected=True)

    assert job.job_vars == {
        'awacs_namespace': 'clowny-balancer.taxi.yandex.net',
        'balancer_nanny_service': (
            'rtc_balancer_clowny-balancer_taxi_yandex_net_sas'
        ),
        'existing_pod_ids': ['pod-1', 'pod-2'],
        'l3mgr_service_id': '123',
        'new_pod_ids': ['pod-2'],
        'newest_pod_id': 'pod-2',
        'old_pod_info': {
            'cpu': 2000,
            'logs_quota': 50,
            'mem': 2048,
            'network': '_SOME_',
            'persistent_volumes': [],
            'root_bandwidth_guarantee_mb_per_sec': 0,
            'root_bandwidth_limit_mb_per_sec': 0,
            'root_fs_quota_mb': 10,
            'root_storage_class': 'hdd',
            'sysctl': 123,
            'work_dir_quota': 20,
        },
        'pod_ids': ['pod-1'],
        'prepared_allocation_request': {},
        'reallocation_id': 'reallocation_id',
        'region': 'sas',
        'snapshot_id': 'snapshot-2',
    }
