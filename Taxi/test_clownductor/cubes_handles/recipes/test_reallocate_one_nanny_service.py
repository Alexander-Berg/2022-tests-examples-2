import pytest


@pytest.mark.features_on(
    'enable_custom_reallocation_params', 'enable_yaml_reallocation_params',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_reallocate_one_nanny_service_recipe(
        mockserver,
        mock_clowny_balancer,
        load_yaml,
        task_processor,
        run_job_common,
        nanny_mockserver,
        nanny_yp_mockserver,
        nanny_yp_list_pods_groups,
        nanny_yp_pod_reallocation_spec,
        nanny_yp_start_pod_reallocation,
        load_json,
        awacs_mockserver,
        yp_mockserver,
):
    nanny_yp_mock = nanny_yp_mockserver()
    awacs_mockserver()
    yp_mockserver()

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_nanny_service/current_state/',
        prefix=True,
    )
    async def _handler(request):
        return load_json('nanny_service_current_state.json')

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _service_get(request):
        return {
            'namespaces': [
                {
                    'id': 1,
                    'awacs_namespace': 'test-fqdn-with-safe-l3',
                    'env': 'testing',
                    'abc_quota_source': 'abc_quota_source',
                    'is_external': False,
                    'is_shared': False,
                    'entry_points': [],
                },
            ],
        }

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ReallocateOneNannyService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_nanny_service',
            'changes': {
                'mem': 1024,
                'cpu': 3500,
                'root_fs_quota_mb': 4000,
                'work_dir_quota': 10000,
                'root_bandwidth_guarantee_mb_per_sec': 1,
                'root_bandwidth_limit_mb_per_sec': 1,
                'root_storage_class': 'hdd',
                'network_bandwidth_guarantee_mb_per_sec': 10,
            },
            'project_name': 'test_project',
            'service_name': 'test_service',
            'service_id': 1,
            'branch_id': 1,
            'pods_count': 100,
            'environment': 'testing',
        },
        initiator='clownductor',
        idempotency_token='ony_one_job',
    )
    await run_job_common(job)
    assert job.job_vars == load_json('expected_job_vars.json')
    assert nanny_yp_list_pods_groups.times_called == 1
    assert nanny_yp_pod_reallocation_spec.times_called == 1
    assert nanny_yp_start_pod_reallocation.times_called == 1
    assert nanny_yp_mock.times_called == 3
