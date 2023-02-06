import pytest

from crons.lib import thresholds


@pytest.mark.parametrize(
    'params,expected_code,expected_data',
    [
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            200,
            {
                'is_enabled': True,
                'name': 'logs_errors_filters-crontasks-juggler_synchronizer',
                'monitoring_status': thresholds.CheckStatus.WARN.value,
                'dev_team': 'platform',
                'warn_threshold': 2,
                'crit_threshold': 4,
                'service': 'logs_errors_filters',
            },
        ),
        (
            {'name': 'logs_warnings_filters-crontasks-juggler_synchronizer'},
            200,
            {
                'is_enabled': True,
                'name': 'logs_warnings_filters-crontasks-juggler_synchronizer',
                'monitoring_status': thresholds.CheckStatus.CRIT.value,
                'dev_team': 'platform',
                'warn_threshold': 2,
                'crit_threshold': 4,
                'warn_time_threshold': '15m20s',
                'crit_time_threshold': '1h30m',
                'service': 'logs_warnings_filters',
            },
        ),
        (
            {'name': 'taxi_corp-stuff-send_csv_order_report'},
            200,
            {
                'is_enabled': True,
                'monitoring_status': thresholds.CheckStatus.SUCCESS.value,
                'name': 'taxi_corp-stuff-send_csv_order_report',
                'service': 'taxi_corp',
            },
        ),
        (
            {'name': 'unknown_task'},
            404,
            {
                'code': 'TASK_IS_NOT_FOUND',
                'message': 'task "unknown_task" is not found',
            },
        ),
    ],
)
async def test_tasks_get(web_app_client, params, expected_code, expected_data):
    response = await web_app_client.get('/v1/tasks/', params=params)
    assert response.status == expected_code
    data = await response.json()
    assert data == expected_data
