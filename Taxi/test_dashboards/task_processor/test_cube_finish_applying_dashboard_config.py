import pytest


DASHBOARD_NAME_MOCK = 'nanny_taxi_test-service_stable'

FETCH_ALL_CONFIGS_QUERY = f"""
SELECT id, status, finish_apply_time
FROM dashboards.configs
WHERE dashboard_name = '{DASHBOARD_NAME_MOCK}'
  AND NOT is_deleted
"""


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='only_applying_configs',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_nanny_service.sql',
                        'add_applying_config_with_uniq_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            id='applied_and_applying_configs',
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
    ],
)
async def test_cube_finish_applying_dashboard_config(call_cube, web_context):
    response = await call_cube(
        'FinishApplyingDashboardConfig',
        {'dashboard_name': DASHBOARD_NAME_MOCK},
    )

    assert response == {'status': 'success'}
    rows = await web_context.pg.primary.fetch(FETCH_ALL_CONFIGS_QUERY)
    assert len(rows) == 1
    applied_config = rows.pop()
    assert applied_config['status'] == 'applied'
    assert applied_config['finish_apply_time']
