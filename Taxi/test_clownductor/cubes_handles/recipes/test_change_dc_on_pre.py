import pytest


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    def make_pod(pod_id: str, state: str = 'ACTIVE'):
        return {
            'status': {
                'agent': {'iss': {'currentStates': [{'currentState': state}]}},
            },
            'meta': {'creationTime': '1628931000883990', 'id': pod_id},
        }

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        cluster = data['cluster']
        nanny_name = data['serviceId']
        assert cluster in ['MAN', 'VLA', 'SAS', 'MYT', 'IVA']

        if nanny_name in ['test_service_pre_stable']:
            if cluster == 'MAN':
                return {'total': 1, 'pods': [make_pod('pod-service-1')]}

        if nanny_name in ['test_service_stable']:
            if cluster == 'MAN':
                return {
                    'total': 2,
                    'pods': [
                        make_pod('pod-service-2'),
                        make_pod('pod-service-3'),
                    ],
                }

            return {
                'total': 4,
                'pods': [
                    make_pod('pod-service-4'),
                    make_pod('pod-service-5'),
                    make_pod('pod-service-6'),
                    make_pod('pod-service-7', state='PREPARED'),
                ],
            }
        return {'total': 0, 'pods': []}

    return _handler


EXPECTED_VARS = {
    'service_id': 1,
    'pre_move_region': 'MAN',
    'use_active': True,
    'job_name': 'ResizeInstancesOneNannyService',
    'changes': {},
    'project_id': 1,
    'project_name': 'taxi',
    'service_name': 'test_service',
    'abc_service': 'abc_service',
    'yp_quota_abc': 'taxiquotaypdefault',
    'stable_env': 'stable',
    'pre_env': 'prestable',
    'pre_nanny_name': 'test_service_pre_stable',
    'pre_branch_id': 3,
    'pre_new_active_regions': ['sas'],
    'stable_nanny_name': 'test_service_stable',
    'stable_branch_id': 2,
    'stable_new_active_regions': ['man', 'sas', 'vla'],
    'stable_instances_by_region': {'man': 3, 'vla': 3, 'sas': 2},
    'pre_instances_by_region': {'sas': 1},
    'pre_pod_ids_by_region': {
        'iva': [],
        'man': ['pod-service-1'],
        'myt': [],
        'sas': [],
        'vla': [],
    },
    'stable_pod_ids_by_region': {
        'iva': [],
        'man': ['pod-service-2', 'pod-service-3'],
        'myt': [],
        'sas': ['pod-service-4', 'pod-service-5', 'pod-service-6'],
        'vla': ['pod-service-4', 'pod-service-5', 'pod-service-6'],
    },
}


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize('service_have_balancers', [True, False])
@pytest.mark.features_on('change_resources_by_name_new_flow')
async def test_test_change_dc_on_pre(
        load_yaml,
        load_json,
        mockserver,
        task_processor,
        run_job_with_meta,
        nanny_mockserver,
        nanny_yp_mockserver,
        add_external_cubes,
        patch,
        mock_clowny_balancer,
        nanny_yp_list_pods,
        service_have_balancers,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_pre_stable/runtime_attrs/',
    )
    def handler_pre(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs_pre.json')
        if request.method == 'PUT':
            return load_json('nanny_service_runtime_attrs_response_pre.json')
        return None

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_stable/runtime_attrs/',
    )
    def handler(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs.json')
        if request.method == 'PUT':
            return load_json('nanny_service_runtime_attrs_response.json')
        return None

    nanny_yp_mock = nanny_yp_mockserver()
    add_external_cubes()

    @patch(
        'clownductor.internal.tasks.cubes.internal.info.'
        'PrepareInfoToChangeDc.shuffle_regions',
    )
    def _shuffle_regions(regions):
        regions.sort()
        return regions

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _balancer_get_service(request):
        service_id = request.query['service_id']
        if service_have_balancers:
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

    task_processor.load_recipe(
        load_yaml('recipes/ResizeInstancesOneNannyService.yaml')['data'],
    )
    job = await task_processor.start_job(
        name='ChangeDcOnPrestable',
        job_vars={
            'service_id': 1,
            'pre_move_region': 'MAN',
            'use_active': True,
            'job_name': 'ResizeInstancesOneNannyService',
            'changes': {},
            'project_id': 1,
            'project_name': 'taxi',
            'pre_env': 'prestable',
            'stable_env': 'stable',
        },
        initiator='deoevgen',
        idempotency_token='ChangeDcOnPrestable_1_1',
    )
    await run_job_with_meta(job)
    job.job_vars.pop('pre_job_id')
    job.job_vars.pop('pre_comment')
    if not service_have_balancers:
        assert not job.job_vars.get('sync_slb_job_id')
    else:
        assert job.job_vars['sync_slb_job_id']
    job.job_vars.pop('sync_slb_job_id')
    job.job_vars.pop('sync_stable_slb_job_id')
    job.job_vars.pop('job_id')
    job.job_vars.pop('comment')
    assert job.job_vars == EXPECTED_VARS
    assert handler_pre.times_called == 4
    assert handler.times_called == 4
    assert nanny_yp_mock.times_called == 25

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ChangeDcOnPrestable.yaml')['data'],
    )
    test_job = await recipe.start_job(
        job_vars={
            'service_id': 1,
            'pre_move_region': 'MAN',
            'pre_env': 'prestable',
            'stable_env': 'stable',
            'use_active': True,
            'job_name': 'ResizeInstancesOneNannyService',
            'changes': {},
            'project_id': 1,
            'project_name': 'taxi',
        },
        initiator='deoevgen',
    )
    await run_job_with_meta(test_job)
    test_job.job_vars.pop('pre_job_id')
    test_job.job_vars.pop('pre_comment')
    if not service_have_balancers:
        assert not test_job.job_vars.get('sync_slb_job_id')
    else:
        assert test_job.job_vars['sync_slb_job_id']
    test_job.job_vars.pop('sync_slb_job_id')
    test_job.job_vars.pop('sync_stable_slb_job_id')
    test_job.job_vars.pop('job_id')
    test_job.job_vars.pop('comment')
    assert test_job.job_vars == EXPECTED_VARS
