# from aiohttp import web
import pytest


CALLS_CURSOR_URL = '/v1/calls/history'
CALLCENTER_STATS_DB_TIMEOUTS = {
    'admin_timeouts': {'network_timeout': 1200, 'statement_timeout': 1000},
    'calls_history': {'network_timeout': 1200, 'statement_timeout': 1000},
    'default': {'network_timeout': 1200, 'statement_timeout': 1000},
}


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(
    CALLCENTER_STATS_CALLS_LIST_LIMIT=4,
    CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS,
)
@pytest.mark.pgsql('callcenter_stats', files=['callcenter_calls_history.sql'])
@pytest.mark.parametrize(
    'request_body, expected_status, expected_data',
    (
        ('body_1.json', 200, 'expected_data_1.json'),
        ('body_2.json', 200, 'expected_data_2.json'),
        ('body_3.json', 200, 'expected_data_3.json'),
    ),
)
async def test_calls_cursor(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        CALLS_CURSOR_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    assert response.json() == load_json(expected_data)
