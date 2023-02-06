import pytest


@pytest.mark.parametrize(
    'payload, status, input_data, awacs_namespace',
    [
        pytest.param(
            {
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
            },
            'success',
            {
                'service_id': 1,
                'branch_id': 1,
                'service_name': 'test_service',
                'project_name': 'test_project',
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 5,
                'environment': 'testing',
            },
            'test-fqdn-with-safe-l3',
            marks=pytest.mark.features_off(
                'enable_custom_reallocation_params',
            ),
            id='service_with_disable_feature',
        ),
        pytest.param(
            {
                'degrade_params': {
                    'maxUnavailablePods': 20,
                    'minUpdateDelaySeconds': 300,
                },
            },
            'success',
            {
                'service_id': 1,
                'branch_id': 1,
                'service_name': 'test_service',
                'project_name': 'test_project',
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 100,
                'environment': 'testing',
            },
            'test-fqdn-with-safe-l3',
            marks=pytest.mark.features_on('enable_custom_reallocation_params'),
            id='service_with_enable_feature',
        ),
        pytest.param(
            {
                'degrade_params': {
                    'maxUnavailablePods': 45,
                    'minUpdateDelaySeconds': 350,
                },
            },
            'success',
            {
                'service_id': 1,
                'branch_id': 1,
                'service_name': 'test_service',
                'project_name': 'test_project',
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 100,
                'environment': 'testing',
            },
            'test-fqdn-with-safe-l3',
            marks=pytest.mark.features_on(
                'enable_custom_reallocation_params',
                'enable_yaml_reallocation_params',
            ),
            id='service_with_enable_all_features',
        ),
        pytest.param(
            {
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
            },
            'success',
            {
                'service_id': 1,
                'branch_id': 2,
                'service_name': 'test_service',
                'project_name': 'test_project',
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 100,
                'environment': 'stable',
            },
            'test-fqdn-with-safe-l3',
            marks=pytest.mark.features_on(
                'enable_custom_reallocation_params',
                'enable_yaml_reallocation_params',
            ),
            id='service_without_l7_balancers',
        ),
        pytest.param(
            {
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
            },
            'success',
            {
                'service_id': 1,
                'branch_id': 1,
                'service_name': 'test_service',
                'project_name': 'test_project',
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 100,
                'environment': 'testing',
            },
            'test-fqdn',
            marks=pytest.mark.features_on(
                'enable_custom_reallocation_params',
                'enable_yaml_reallocation_params',
            ),
            id='service_with_bad_l3_balancer',
        ),
        pytest.param(
            {},
            'success',
            {
                'service_id': 1,
                'degrade_params': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
                'pods_count': 100,
                'environment': 'testing',
            },
            'test-fqdn',
            marks=pytest.mark.features_on('enable_custom_reallocation_params'),
            id='not_all_clown_parameters_in_input',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_cube_nanny_prepare_degrade_params(
        call_cube_handle,
        payload,
        status,
        input_data,
        mock_clowny_balancer,
        awacs_mockserver,
        awacs_namespace,
):
    awacs_mockserver()

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _service_get(request):
        return {
            'namespaces': [
                {
                    'id': 1,
                    'awacs_namespace': awacs_namespace,
                    'env': 'testing',
                    'abc_quota_source': 'abc_quota_source',
                    'is_external': False,
                    'is_shared': False,
                    'entry_points': [],
                },
            ],
        }

    await call_cube_handle(
        'NannyPrepareDegradeParams',
        {
            'content_expected': {'payload': payload, 'status': status},
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
