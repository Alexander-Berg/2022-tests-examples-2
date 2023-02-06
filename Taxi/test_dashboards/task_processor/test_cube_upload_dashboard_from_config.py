import pytest


DIFF_PROPOSAL = {
    'base': 'master',
    'changes': [
        {
            'data': (
                'clownductor_config: taxi-devops:clownductor:stable\n\n'
                'http_hosts:\n  - clownductor.taxi.yandex.net\n'
                'layout:\n  - system\n  - rps_share\n  - http\n'
            ),
            'filepath': 'grafana/nanny_taxi-devops_clownductor_stable.yaml',
            'state': 'created_or_updated',
        },
    ],
    'comment': 'Update dashboard configs',
    'repo': 'infra-cfg-graphs',
    'title': 'feat clownductor: update dashboard configs in stable',
    'user': 'taxi',
}


@pytest.fixture(name='call_cube_client')
def _call_cube_client(web_app_client):
    return web_app_client


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
@pytest.mark.config(
    DASHBOARDS_FEATURES={
        '__default__': {
            'upload_dashboard_from_config': True,
            'upload_dashboard_from_config_dry_run': True,
        },
    },
)
@pytest.mark.usefixtures(
    'arc_infra_graphs_mock',
    'git_infra_graphs_mock',
    'disable_multiprocessing_pool',
)
async def test_cube_upload_dashboard_from_config(
        call_cube, generate_dashboard_mock, includes_dir_call_path,
):
    response = await call_cube(
        'UploadDashboardFromConfig',
        {
            'diff_proposal': DIFF_PROPOSAL,
            'project_name': 'taxi-devops',
            'service_name': 'clownductor',
        },
    )
    assert response['status'] == 'success'
    calls = generate_dashboard_mock.calls
    assert len(calls) == 1
    assert calls[0] == {
        'config_path': 'grafana/nanny_taxi-devops_clownductor_stable.yaml',
        'force': False,
        'includes_dir': includes_dir_call_path,
        'print_dashboard': False,
        'strict_mode': True,
        'title': None,
        'upload': False,
        'user_config': {
            'clownductor_config': 'taxi-devops:clownductor:stable',
            'http_hosts': ['clownductor.taxi.yandex.net'],
            'layout': ['system', 'rps_share', 'http'],
        },
    }
