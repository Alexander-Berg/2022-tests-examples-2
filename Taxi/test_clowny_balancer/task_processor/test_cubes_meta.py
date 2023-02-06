import pytest

from testsuite.utils import matching


@pytest.mark.parametrize(
    'cube_name, input_data, payload',
    [
        (
            'MetaCubeRemoveNannyService',
            {
                'service_id': 1,
                'nanny_sas': 'some_namespace',
                'nanny_vla': 'some_namespace',
                'nanny_man': '',
            },
            {'job_ids': [1, 1]},
        ),
        (
            'MetaCubeRemoveNannyService',
            {
                'nanny_sas': 'some_namespace',
                'nanny_vla': 'some_namespace',
                'nanny_man': '',
            },
            {'job_ids': [1, 1]},
        ),
        ('MetaCubeWaitForJobsCommon', {'job_ids': [1]}, None),
        ('MetaCubeWaitForJobCommon', {'job_id': 1}, None),
        (
            'MetaStartAllocatingExternalL3Addresses',
            {
                'abc_service_slug': 'abc',
                'l3mgr_service_id': '123',
                'fqdn': 'fqdn.net',
                'author': 'd1mbas',
            },
            {'job_id': 1},
        ),
        (
            'MetaStartChangeQuotaAwacsForBalancers',
            {
                'namespace_ids': ['ns1', 'ns2'],
                'user': 'karachevda',
                'new_quota_abc': 'abc-id',
            },
            {'job_ids': [1, 1]},
        ),
        (
            'MetaStartChangeQuotaAwacsNanny',
            {
                'nanny_services': ['service-man', 'service-vla'],
                'user': 'karachevda',
                'new_quota_abc': 'abc-id',
            },
            {'job_ids': [1, 1]},
        ),
        (
            'MetaStartBalancerEnsureDoublePods',
            {
                'namespace_id': 'ns1',
                'sas_pods': ['pod-1'],
                'vla_pods': ['pod-2'],
                'man_pods': [],
                'nanny_services': ['rtc_balancer_sas', 'rtc_balancer_vla'],
            },
            {'job_ids': [1, 1]},
        ),
        (
            'MetaStartEntryPointEnableSsl',
            {
                'entry_point_id': 1,
                'protocol': 'http',
                'awacs_domain_id': 'service_stable',
                'awacs_namespace_id': 'custom-stable',
                'author': 'deoevgen',
                'st_ticket': 'COOLTICKET-1',
            },
            {'job_id': -1},
        ),
        (
            'MetaStartEntryPointEnableSsl',
            {
                'entry_point_id': 1,
                'protocol': 'https',
                'awacs_domain_id': 'service_stable',
                'awacs_namespace_id': 'custom-stable',
                'author': 'deoevgen',
                'st_ticket': 'COOLTICKET-1',
            },
            {'job_id': 1},
        ),
    ],
)
async def test_cubes(
        mock_task_processor,
        mock_task_processor_start_job,
        call_cube,
        cube_name,
        input_data,
        payload,
):
    mock_task_processor_start_job()

    @mock_task_processor('/v1/jobs/')
    async def _jobs_retrieve_handler(request):
        jobs = [
            {
                'job_info': {
                    'id': 1,
                    'job_vars': {},
                    'name': 'aaa',
                    'recipe_id': 1,
                    'status': 'success',
                    'created_at': 1234,
                },
                'tasks': [],
            },
        ]
        return {'jobs': jobs}

    @mock_task_processor('/v1/jobs/retrieve/')
    async def _job_retrieve_handler(request):
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

    response = await call_cube(cube_name, input_data)
    expected = {'status': 'success'}
    if payload is not None:
        expected['payload'] = payload
    assert response == expected


@pytest.mark.parametrize(
    'cube_name, input_data, job, result_job_id',
    [
        (
            'MetaCubeApplyL7MonitoringSettings',
            {'service_id': 1, 'env': 'stable', 'fqdn': 'some.net'},
            {
                'change_doc_id': 'ApplyL7MonitoringSettings-some.net-stable',
                'idempotency_token': matching.any_string,
                'provider_name': 'clowny-balancer',
                'recipe_name': 'ApplyL7MonitoringSettings',
                'job_vars': {
                    'env': 'stable',
                    'fqdn': 'some.net',
                    'service_id': 1,
                },
            },
            1,
        ),
        (
            'MetaCubeDomainCreate',
            {'entry_point_id': 2, 'skip_domain_usage': True},
            None,
            -1,
        ),
        (
            'MetaCubeDomainCreate',
            {'entry_point_id': 3},
            {
                'change_doc_id': 'DomainCreate-ns1-domain-id.net',
                'idempotency_token': matching.any_string,
                'recipe_name': 'DomainCreate',
                'provider_name': 'clowny-balancer',
                'job_vars': {
                    'awacs_namespace_id': 'ns1',
                    'entry_point_id': 3,
                    'domain_id': 'domain-id.net',
                    'origin_fqdn': '',
                },
            },
            1,
        ),
        (
            'MetaStartBalancerEnsureHttpsEnabled',
            {'awacs_namespace_id': 'ns1'},
            {
                'change_doc_id': 'BalancerEnsureHttpsEnabled-ns1',
                'idempotency_token': matching.any_string,
                'recipe_name': 'BalancerEnsureHttpsEnabled',
                'provider_name': 'clowny-balancer',
                'job_vars': {'awacs_namespace_id': 'ns1'},
            },
            1,
        ),
        (
            'MetaStartBalancerReallocateAllPods',
            {'awacs_namespace_id': 'ns1'},
            {
                'change_doc_id': 'BalancerReallocateAllPods-ns1',
                'idempotency_token': matching.any_string,
                'recipe_name': 'BalancerReallocateAllPods',
                'provider_name': 'clowny-balancer',
                'job_vars': {'awacs_namespace_id': 'ns1'},
            },
            1,
        ),
        (
            'MetaStartChangeL7PodsOneNannyService',
            {'nanny_name': 'ns1', 'env': 'stable', 'fqdn': 'some.fqdn.net'},
            {
                'change_doc_id': 'ChangeL7PodsOneNannyService-ns1',
                'idempotency_token': 'ChangeL7PodsOneNannyService-ns1_0',
                'recipe_name': 'ChangeL7PodsOneNannyService',
                'provider_name': 'clowny-balancer',
                'job_vars': {
                    'comment': 'Update pods parameters for L7-balancer',
                    'nanny_name': 'ns1',
                    'env': 'stable',
                    'fqdn': 'some.fqdn.net',
                    'network_capacity': 'REQUIRE_10G',
                },
            },
            1,
        ),
        (
            'MetaStartChangeL7PodsOneNannyService',
            {'nanny_name': '', 'env': 'stable', 'fqdn': 'some.fqdn.net'},
            None,
            -1,
        ),
        (
            'MetaStartChangeL7PodsOneNannyService',
            {
                'nanny_name': '',
                'env': 'stable',
                'fqdn': 'some.fqdn.net',
                'st_ticket': None,
            },
            None,
            -1,
        ),
    ],
)
async def test_job_creation_cubes(
        mock_task_processor,
        call_cube,
        cube_name,
        input_data,
        job,
        result_job_id,
):
    @mock_task_processor('/v1/jobs/start/')
    def _start_job_handler(request):
        assert request.json == job
        return {'job_id': 1}

    response = await call_cube(cube_name, input_data)
    assert response == {
        'status': 'success',
        'payload': {'job_id': result_job_id},
    }
    if job is None:
        assert _start_job_handler.times_called == 0
