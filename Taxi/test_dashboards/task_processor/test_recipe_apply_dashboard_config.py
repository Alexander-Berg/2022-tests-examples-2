import pytest

from dashboards.internal.models import configs_upload


DASHBOARD_NAME_MOCK = 'nanny_taxi_test-service_stable'


@pytest.fixture(name='call_cube_client')
def _call_cube_client(web_app_client):
    return web_app_client


@pytest.fixture(name='sleep_callback')
def _sleep_callback(web_context):
    async def _wrapper(task):
        if task.cube.name == 'EnqueueDashboardConfigUpload':
            config_upload_ids = task.payload['config_upload_ids']
            db_manager = configs_upload.ConfigsUploadManager(web_context)
            await db_manager.set_status(
                config_upload_ids, configs_upload.ConfigUploadStatus.APPLIED,
            )

    return _wrapper


@pytest.mark.parametrize(
    'includes_dir_call_path',
    [
        pytest.param(
            '/tmp/infra-cfg-graphs/grafana/includes',
            marks=[
                pytest.mark.config(
                    DASHBOARDS_UPLOAD_CONFIGS_TO_REPO={
                        'github_vendor': {'enabled': True},
                        'arcadia_vendor': {'enabled': False},
                    },
                ),
            ],
            id='use git',
        ),
        pytest.param(
            '/tmp/arc/infra-cfg-graphs/grafana/includes',
            marks=[
                pytest.mark.config(
                    DASHBOARDS_UPLOAD_CONFIGS_TO_REPO={
                        'github_vendor': {'enabled': False},
                        'arcadia_vendor': {'enabled': True},
                    },
                ),
            ],
            id='use arc',
        ),
    ],
)
@pytest.mark.pgsql(
    'dashboards',
    files=[
        'init_nanny_service.sql',
        'add_applied_config_with_common_handler.sql',
        'add_applying_config_with_uniq_handler.sql',
    ],
)
@pytest.mark.config(
    DASHBOARDS_FEATURES={
        '__default__': {
            'upload_dashboard_from_config': False,
            'upload_dashboard_from_config_dry_run': False,
        },
        'taxi-devops': {
            '__default__': {
                'upload_dashboard_from_config': True,
                'upload_dashboard_from_config_dry_run': True,
            },
        },
    },
)
@pytest.mark.usefixtures(
    'arc_infra_graphs_mock',
    'git_infra_graphs_mock',
    'disable_multiprocessing_pool',
)
async def test_recipe(
        load_yaml,
        task_processor,
        run_job_common,
        generate_dashboard_mock,
        sleep_callback,
        includes_dir_call_path,
):
    recipe = task_processor.load_recipe(
        load_yaml('recipes/ApplyDashboardConfig.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'dashboard_name': DASHBOARD_NAME_MOCK},
        initiator='dashboards',
    )
    await run_job_common(job, sleep_callback)

    # too heavy object, tested separately
    job.job_vars.pop('diff_proposal')
    calls = generate_dashboard_mock.calls
    assert len(calls) == 1
    user_config = calls[0].pop('user_config')
    layout = user_config.pop('layout')
    assert len(layout) == 6
    for expected_layout, layout in zip(
            ['system', 'rps_share', 'http', 'fallbacks', 'include', 'stq'],
            layout,
    ):
        if isinstance(layout, str):
            assert expected_layout == layout
        else:
            assert len(layout.keys()) == 1
            assert expected_layout == next(iter(layout.keys()))

    assert user_config == {
        'clownductor_config': 'taxi:test-service:stable',
        'http_hosts': ['test-service.taxi.yandex.net'],
    }

    assert calls[0] == {
        'config_path': 'grafana/nanny_taxi_test-service_stable.yaml',
        'force': False,
        'includes_dir': includes_dir_call_path,
        'print_dashboard': False,
        'strict_mode': True,
        'title': None,
        'upload': False,
    }
    assert job.job_vars == {
        'dashboard_name': DASHBOARD_NAME_MOCK,
        'config_upload_ids': [1, 2],
        'project_name': 'taxi-devops',
        'service_name': 'test-service',
    }
