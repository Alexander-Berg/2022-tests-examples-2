import pytest


@pytest.mark.parametrize(
    'params,expected_code,expected_data',
    [
        (
            {'name': 'logs_errors_filters'},
            200,
            {
                'crit_threshold': 5,
                'dev_team': 'platform',
                'name': 'logs_errors_filters',
                'warn_threshold': 2,
                'last_launches_count': 6,
                'warn_time_threshold': '0s',
                'crit_time_threshold': '0s',
            },
        ),
        (
            {'name': 'logs_warnings_filters'},
            200,
            {
                'crit_threshold': 5,
                'dev_team': 'platform',
                'name': 'logs_warnings_filters',
                'warn_threshold': 2,
                'last_launches_count': 6,
                'warn_time_threshold': '10m45s',
                'crit_time_threshold': '1h30m20s',
            },
        ),
        (
            {'name': 'unknown_service'},
            404,
            {
                'code': 'SERVICE_IS_NOT_FOUND',
                'message': 'service "unknown_service" is not found',
            },
        ),
    ],
)
async def test_services_get(
        web_app_client, params, expected_code, expected_data,
):
    response = await web_app_client.get('/v1/services/', params=params)
    assert response.status == expected_code
    data = await response.json()
    assert data == expected_data
