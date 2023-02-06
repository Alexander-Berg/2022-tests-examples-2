import pytest


@pytest.fixture(name='init_data', autouse=True)
async def _init_data(add_service, add_branch, mocks_for_service_creation):
    await add_service('taxi-devops', 'clownductor')
    await add_branch(
        {
            'service_id': 1,
            'name': 'stable',
            'direct_link': 'taxi_clownductor_stable',
            'env': 'stable',
        },
    )


@pytest.fixture(name='test_dashboards_cube')
def _test_dashboards_cube(
        call_cube_handle, mock_dashboards_context, dashboards_mockserver,
):
    async def run_test(expected):
        input_data = {'branch_id': 1, 'needs_balancers': True}
        await call_cube_handle(
            'DashboardsUploadGraphs',
            {
                'data_request': {
                    'job_id': 1,
                    'retries': 0,
                    'status': 'in_progress',
                    'task_id': 1,
                    'input_data': input_data,
                },
                'content_expected': {'status': 'success'},
            },
        )
        configs = list(mock_dashboards_context.configs)
        assert len(configs) == 1
        key, config = configs[0]
        assert key == ('taxi-devops', 'clownductor', 'stable', 'nanny')
        assert config.serialize() == expected

    return run_test


@pytest.mark.features_on('use_dashboards_upload_graphs')
async def test_dashboards_upload_graphs(test_dashboards_cube):
    await test_dashboards_cube(
        {
            'hostnames': ['clownductor.taxi.pytest'],
            'layouts': [
                {'name': 'system'},
                {'name': 'rps_share'},
                {'name': 'http'},
            ],
        },
    )


@pytest.mark.features_on('use_dashboards_upload_graphs')
async def test_dashboards_upload_uservices_graphs(
        test_dashboards_cube, set_service_general_params, make_empty_config,
):
    param_config = make_empty_config()
    param_config.service_info.general.set('service_type', 'uservices')
    await set_service_general_params(1, param_config)
    await test_dashboards_cube(
        {
            'hostnames': ['clownductor.taxi.pytest'],
            'layouts': [
                {'name': 'system'},
                {'name': 'rps_share'},
                {'name': 'http'},
                {
                    'name': 'userver_common',
                    'parameters': {'uservice_name': 'clownductor'},
                },
            ],
        },
    )
