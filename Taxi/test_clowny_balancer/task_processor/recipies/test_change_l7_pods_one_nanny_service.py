import pytest


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
            _snapshots['snapshot-1']['pods'] = sorted(_pods.keys())
            response.update(payload={'snapshot_id': 'snapshot-1'})
        if cube.name == 'NannyCubeWaitForDeploy':
            response.update(
                payload={'active_snapshot_id': input_data['snapshot_id']},
            )
        if cube.name == 'NannyGetServicePods':
            response.update(
                payload={
                    'man': [],
                    'vla': [],
                    'sas': ['olololo_sas_pod_id'],
                    'man_region': 'MAN',
                    'vla_region': 'VLA',
                    'sas_region': 'SAS',
                    'pod_ids_by_region': {
                        'man': [],
                        'sas': ['olololo_sas_pod_id'],
                        'vla': [],
                    },
                },
            )
        if cube.name == 'NannyCubeRemovePodsFromDeploy':
            response.update(payload={'snapshot_id': 'snapshot_id_to_delete'})

        return mockserver.make_response(json=response)

    return _do_it


@pytest.mark.usefixtures('clown_cube_caller')
async def test_recipe(load_yaml, task_processor, run_job_common, mockserver):

    recipe = task_processor.load_recipe(
        load_yaml('ChangeL7PodsOneNannyService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'ns1',
            'env': 'stable',
            'fqdn': 'fqdn.net',
            'network_capacity': 'REQUIRE_10G',
            'comment': 'Update pods parameters for L7-balancer',
        },
        initiator='clowny-balancer',
    )
    await run_job_common(job, sleep_is_expected=True)
    assert job.job_vars == {
        'nanny_name': 'ns1',
        'env': 'stable',
        'fqdn': 'fqdn.net',
        'network_capacity': 'REQUIRE_10G',
        'io_info': [
            {'path': '__default__', 'value': 1},
            {'path': '/', 'value': 1},
            {'path': '/awacs', 'value': 1},
            {'path': '/logs', 'value': 1},
        ],
        'region': 'sas',
        'existing_pod_ids': ['pod-1'],
        'real_nanny_name': 'ns1',
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
        'new_pod_ids': ['pod-2'],
        'snapshot_id': 'snapshot-1',
        'comment': 'Update pods parameters for L7-balancer',
        'sas_pods_to_remove': ['olololo_sas_pod_id'],
        'sas_region': 'SAS',
        'snapshot_id_remove_pods': 'snapshot_id_to_delete',
        'vla_pods_to_remove': [],
        'man_pods_to_remove': [],
        'vla_region': 'VLA',
        'man_region': 'MAN',
        'pod_ids_by_region': {
            'man': [],
            'sas': ['olololo_sas_pod_id'],
            'vla': [],
        },
    }
