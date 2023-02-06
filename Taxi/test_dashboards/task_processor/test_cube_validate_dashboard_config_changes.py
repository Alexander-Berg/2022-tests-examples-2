import pytest


CONFIG_MARK = pytest.mark.config(
    DASHBOARDS_GRAFANA_ACTIVE_LAYOUTS={
        'http': {'is_active': True},
        'http_basic': {'is_active': True},
        'rps_share': {'is_active': True},
        'include': {'is_active': True},
        'system': {'is_active': True},
        'stq': {'is_active': False},
    },
)


@CONFIG_MARK
@pytest.mark.parametrize(
    'diff_proposal_filename, expected_status',
    [
        pytest.param('diff_proposal.json', 'success', id='success'),
        pytest.param('invalid_diff_proposal.json', 'failed', id='failed'),
    ],
)
async def test_cube_validate_dashboard_config_changes(
        call_cube, load_json, diff_proposal_filename, expected_status,
):
    diff_proposal = load_json(diff_proposal_filename)
    response = await call_cube(
        'ValidateDashboardConfigChanges', {'diff_proposal': diff_proposal},
    )
    assert response['status'] == expected_status


@pytest.fixture(name='get_diff_proposal')
def _get_diff_proposal(load_json):
    def _wrapper(change_layouts=None):
        diff_proposal = load_json('diff_proposal.json')
        if change_layouts:
            changes = diff_proposal['changes']
            data_raw = changes[-1]['data']
            to_replace = 'layout:\n  - system\n  - rps_share\n  - http'
            changes[-1]['data'] = data_raw.replace(to_replace, change_layouts)
        return diff_proposal

    return _wrapper


@CONFIG_MARK
@pytest.mark.parametrize(
    'change_layouts',
    [
        pytest.param(None, id='default_config'),
        pytest.param('layout:\n  - system', id='just_system'),
        pytest.param(
            'layout:\n  - system:\n      collapsed: true',
            id='system_collapsed',
        ),
    ],
)
async def test_validate_config_ok(
        call_cube, get_diff_proposal, change_layouts,
):
    diff_proposal = get_diff_proposal(change_layouts=change_layouts)
    response = await call_cube(
        'ValidateDashboardConfigChanges', {'diff_proposal': diff_proposal},
    )
    assert response['status'] == 'success', response


@CONFIG_MARK
@pytest.mark.parametrize(
    'change_layouts',
    [
        pytest.param('layout:\n  - not_exists', id='not_exists'),
        pytest.param(
            'layout:\n  - system:\n      bad_param: true', id='bad_param',
        ),
        pytest.param('layout:\n  - stq', id='not_active'),
    ],
)
async def test_validate_config_bad(
        call_cube, get_diff_proposal, change_layouts,
):
    diff_proposal = get_diff_proposal(change_layouts=change_layouts)
    response = await call_cube(
        'ValidateDashboardConfigChanges', {'diff_proposal': diff_proposal},
    )
    assert response['status'] == 'failed', response
