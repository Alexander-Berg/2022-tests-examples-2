import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize(
    'file_name',
    [
        pytest.param(
            'reallocate_one_nanny_service', id='ReallocateOneNannyService',
        ),
        pytest.param(
            'resize_instances_one_nanny_service',
            id='ResizeInstancesOneNannyService',
        ),
    ],
)
@pytest.mark.features_on('change_resources_by_name_new_flow')
async def test_change_resources_by_name(
        call_cube_handle, load_json, file_name, task_processor,
):
    cube_data = load_json(f'{file_name}.json')
    input_data = cube_data['data_request']['input_data']
    task_processor.load_recipe(
        {
            'name': 'ReallocateOneNannyService',
            'provider_name': 'clownductor',
            'job_vars': [
                'nanny_name',
                'changes',
                'project_name',
                'service_name',
                'environment',
            ],
            'stages': [],
        },
    )
    expected_reallocate_job_vars = {
        field: input_data[field]
        for field in [
            'nanny_name',
            'changes',
            'project_name',
            'service_name',
            'environment',
            'branch_id',
            'service_id',
        ]
    }
    expected_reallocate_job_vars['pods_count'] = 3
    task_processor.load_recipe(
        {
            'name': 'ResizeInstancesOneNannyService',
            'provider_name': 'clownductor',
            'job_vars': [
                'man_pod_ids',
                'sas_pod_ids',
                'vla_pod_ids',
                'man_region',
                'vla_region',
                'sas_region',
                'man_instances',
                'sas_instances',
                'vla_instances',
                'yp_quota_abc',
                'nanny_name',
                'regions',
                'comment',
                'pod_naming_mode',
                'use_append_pods',
                'service_id',
                'branch_ids',
                'pod_ids_by_region',
                'instances_by_region',
                'environment',
            ],
            'stages': [],
        },
    )

    await call_cube_handle('MetaCubeStartJobChangeResourcesByName', cube_data)
    job_vars = task_processor.job(1).job_vars
    if input_data['job_name'] == 'ReallocateOneNannyService':
        assert job_vars == expected_reallocate_job_vars
    else:
        instances_by_region = input_data['instances_by_region']
        pod_ids_by_region = input_data['pod_ids_by_region']
        assert job_vars == {
            'branch_ids': [1],
            'comment': 'Automate change environment',
            'instances_by_region': instances_by_region,
            'man_instances': instances_by_region['man'],
            'man_pod_ids': pod_ids_by_region['man'],
            'man_region': 'man',
            'nanny_name': 'test_nanny_service',
            'pod_ids_by_region': pod_ids_by_region,
            'pod_naming_mode': 'ENUMERATE',
            'project_name': 'test_project',
            'regions': [],
            'sas_instances': instances_by_region['sas'],
            'sas_pod_ids': pod_ids_by_region['sas'],
            'sas_region': 'sas',
            'service_id': 1,
            'service_name': 'test_service',
            'use_append_pods': True,
            'vla_instances': instances_by_region['vla'],
            'vla_pod_ids': pod_ids_by_region.get('vla'),
            'vla_region': 'vla',
            'yp_quota_abc': 'abc_service',
            'environment': 'testing',
        }
