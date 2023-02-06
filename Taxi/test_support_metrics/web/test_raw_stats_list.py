import pytest


@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_response'],
    [
        (
            {
                'names': 'sip_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-02T21:00:00Z',
            },
            200,
            [
                {
                    'action': 'sip_call',
                    'count': 1,
                    'line': 'first_line',
                    'login': 'superuser',
                },
            ],
        ),
        (
            {
                'names': 'sip_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-03T00:00:00+0300',
            },
            200,
            [
                {
                    'action': 'sip_call',
                    'count': 1,
                    'line': 'first_line',
                    'login': 'superuser',
                },
            ],
        ),
        (
            {
                'names': 'sip_success_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-04T00:00:00+0300',
                'logins': 'superuser|user',
            },
            200,
            [
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'first_line',
                    'login': 'superuser',
                },
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'first_line',
                    'login': 'user',
                },
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'second_line',
                    'login': 'user',
                },
            ],
        ),
        (
            {
                'names': 'sip_success_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-04T00:00:00+0300',
                'logins': 'superuser',
            },
            200,
            [
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'first_line',
                    'login': 'superuser',
                },
            ],
        ),
        (
            {
                'names': 'sip_success_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-04T00:00:00+0300',
                'line': 'second_line',
            },
            200,
            [
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'second_line',
                    'login': 'user',
                },
            ],
        ),
        (
            {
                'names': 'sip_calls_calculator|sip_success_calls_calculator',
                'stat_interval': '1day',
                'created_ts': '2019-07-04T00:00:00+0300',
                'logins': 'superuser',
            },
            200,
            [
                {
                    'action': 'sip_call',
                    'count': 1,
                    'line': 'first_line',
                    'login': 'superuser',
                },
                {
                    'action': 'success_call',
                    'count': 1,
                    'avg_duration': 60,
                    'line': 'first_line',
                    'login': 'superuser',
                },
            ],
        ),
        (
            {
                'names': 'backlog_average_by_line_and_status',
                'stat_interval': '1day',
                'created_ts': '2019-07-04T00:00:00+0300',
            },
            200,
            [
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 5, 'reopen': 2},
                    'projects': ['taxi'],
                    'line': 'first',
                },
            ],
        ),
        (
            {
                'names': 'backlog_average_by_line_and_status',
                'stat_interval': '1min',
                'created_ts': '2019-07-04T00:00:00+0300',
            },
            200,
            [
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 7, 'reopen': 3.5},
                    'projects': ['taxi', 'eats'],
                    'line': 'first',
                },
            ],
        ),
        (
            {
                'names': 'backlog_average_by_line_and_status',
                'stat_interval': '1min',
                'created_ts': '2019-08-04T00:00:00+0300',
            },
            200,
            [],
        ),
    ],
)
async def test_chatterbox_raw_stats(
        web_app_client, params, expected_status, expected_response,
):
    response = await web_app_client.get(
        '/v1/chatterbox/raw_stats/list', params=params,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    data = sorted(data, key=lambda x: (x['line'], x.get('login'), x['action']))
    assert data == expected_response


@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_response'],
    [
        (
            {
                'names': 'backlog_average_by_line_and_status',
                'stat_interval': '1min',
            },
            200,
            [
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 10.0, 'reopen': 10.0},
                    'line': 'newest',
                    'projects': ['taxi'],
                },
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 15.0, 'reopen': 10.0},
                    'line': 'newest_2',
                    'projects': ['taxi'],
                },
            ],
        ),
    ],
)
async def test_stats_without_created_ts(
        web_app_client, params, expected_status, expected_response,
):
    response = await web_app_client.get(
        '/v1/chatterbox/raw_stats/list', params=params,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    data = sorted(data, key=lambda x: (x['line'], x['average_counts']))
    assert data == expected_response


@pytest.mark.config(SUPPORT_METRICS_RAW_STAT_GROUP_BY_FIELD_DELAY=3)
@pytest.mark.now('2019-07-05 21:05:00.00000')
@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_response'],
    [
        (
            {
                'names': 'backlog_average_by_line_and_status',
                'stat_interval': '1min',
                'field_group_by': 'line',
            },
            200,
            [
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 100.0, 'reopen': 100.0},
                    'line': 'latecomer',
                    'projects': ['taxi'],
                },
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 10.0, 'reopen': 10.0},
                    'line': 'newest',
                    'projects': ['taxi'],
                },
                {
                    'action': 'chatterbox_line_backlog',
                    'average_counts': {'new': 15.0, 'reopen': 10.0},
                    'line': 'newest_2',
                    'projects': ['taxi'],
                },
            ],
        ),
    ],
)
async def test_grouped_raw_stat(
        web_app_client, params, expected_status, expected_response,
):
    response = await web_app_client.get(
        '/v1/chatterbox/raw_stats/list', params=params,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    data = sorted(data, key=lambda x: (x['line'], x['average_counts']))
    assert data == expected_response
