import pathlib

import pytest


GRAPHS_REPO_OWNER_MOCK = 'taxi'
GRAPHS_REPO_NAME_MOCK = 'infra-cfg-graphs'


@pytest.fixture(name='call_cube_client')
def _call_cube_client(web_app_client):
    return web_app_client


@pytest.mark.parametrize(
    'dashboard_name, generated_configs_dir, pr_title, changes_count',
    [
        pytest.param(
            'nanny_taxi_test-service_stable',
            'nanny_service_generate_configs',
            'feat test-service: update dashboard configs in stable',
            2,
            id='nanny_service_generate_configs',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_nanny_service.sql',
                        'add_applied_config_with_common_handler.sql',
                        'add_applying_config_with_uniq_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'eda_conductor_taxi_user_api',
            'conductor_service_generate_configs',
            'feat user-api: update dashboard configs in stable',
            2,
            id='conductor_service_generate_configs',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_conductor_service.sql',
                        'add_applying_config_without_handlers.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'nanny_taxi_test-service_stable',
            'service_with_multiple_branches_generate_configs',
            'feat test-service: update dashboard configs in stable, testing',
            3,
            id='service_with_multiple_branches_generate_configs',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_service_branches.sql',
                        'add_applying_config_for_two_branches.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'nanny_taxi_test-service_stable',
            'multiple_services_generate_configs',
            'feat all: update dashboard configs',
            3,
            id='multiple_services_generate_configs',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_multiple_services.sql',
                        'add_applying_config_for_multiple_services.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'nanny_taxi_test-service_stable',
            'service_with_multiple_hostnames',
            'feat test-service: update dashboard configs in stable',
            2,
            id='service_with_multiple_hostnames',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_nanny_service_with_multiple_hostnames.sql',
                        'add_applying_config_with_uniq_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'nanny_taxi_test-service_stable',
            'service_with_no_dorblu',
            'feat test-service: update dashboard configs in stable',
            1,
            id='service_with_no_dorblu',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_nanny_service_no_hostnames.sql',
                        'add_applying_config_with_uniq_handler.sql',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    DASHBOARDS_GRAPHS_REPO_SETTINGS={
        'user': GRAPHS_REPO_OWNER_MOCK,
        'repo': GRAPHS_REPO_NAME_MOCK,
    },
)
async def test_cube_generate_dashboard_config_changes(
        call_cube,
        load,
        dashboard_name,
        generated_configs_dir,
        pr_title,
        changes_count,
):
    response = await call_cube(
        'GenerateDashboardConfigChanges', {'dashboard_name': dashboard_name},
    )
    assert response['status'] == 'success', response.get('payload', '')
    assert response['payload']['diff_proposal']['title'] == pr_title
    assert (
        response['payload']['diff_proposal']['user'] == GRAPHS_REPO_OWNER_MOCK
    )
    assert (
        response['payload']['diff_proposal']['repo'] == GRAPHS_REPO_NAME_MOCK
    )

    for file_change in response['payload']['diff_proposal']['changes']:
        file_path = f'{generated_configs_dir}/{file_change["filepath"]}'
        expected_data = load(file_path)

        assert file_change['data'] == expected_data, file_path

    assert (
        len(response['payload']['diff_proposal']['changes']) == changes_count
    )


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            marks=[pytest.mark.features_on('use_new_grafana_merge')],
            id='new_merge',
        ),
        pytest.param(
            marks=[pytest.mark.features_off('use_new_grafana_merge')],
            id='old_merge',
        ),
    ],
)
@pytest.mark.parametrize(
    'use_arc, includes_dir_call_path',
    [
        pytest.param(
            False,
            '/var/cache/yandex/taxi/infra-cfg-graphs/grafana/includes',
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
            True,
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
    DASHBOARDS_GRAPHS_REPO_SETTINGS={
        'user': GRAPHS_REPO_OWNER_MOCK,
        'repo': GRAPHS_REPO_NAME_MOCK,
    },
)
async def test_generate_changes_with_merge(
        call_cube, load, monkeypatch, use_arc, includes_dir_call_path,
):
    monkeypatch.setattr(
        'dashboards.components.infra_graphs_repo.ArcRepo.ARC_SUBDIR_NAME', '',
    )

    generated_configs_dir = 'service_with_merge'
    monkeypatch.setattr(
        'dashboards.components.infra_graphs_repo.CACHE_REPO_FOLDER',
        pathlib.Path(__file__).parent
        / 'static'
        / 'test_cube_generate_dashboard_config_changes'
        / generated_configs_dir,
    )
    dashboard_name = 'nanny_taxi_test-service_stable'
    response = await call_cube(
        'GenerateDashboardConfigChanges', {'dashboard_name': dashboard_name},
    )
    assert response['status'] == 'success', response.get('payload', '')

    changes = response['payload']['diff_proposal']['changes']
    for file_change in changes:
        file_path = f'{generated_configs_dir}/{file_change["filepath"]}'
        expected_data = load(file_path)

        assert file_change['data'] == expected_data, file_path

    assert len(changes) == 2
