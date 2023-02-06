import datetime as dt

import pytest

NOW = dt.datetime(2021, 9, 20, 0, 19, tzinfo=dt.timezone.utc)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_response_data'],
    [
        pytest.param(
            {},
            200,
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'login': '',
                        'status': 'offered',
                        'waiting_time': 180,
                        'updated_ts': '2021-09-20T20:00:13+03:00',
                    },
                    {
                        'id': 'task_2',
                        'login': 'support_1',
                        'status': 'accepted',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-20T20:00:49+03:00',
                    },
                    {
                        'id': 'task_3',
                        'login': '',
                        'status': 'new',
                        'waiting_time': 420,
                        'updated_ts': '2021-09-20T20:01:15+03:00',
                    },
                    {
                        'id': 'task_4',
                        'login': 'support_2',
                        'status': 'in_progress',
                        'waiting_time': 300,
                        'updated_ts': '2021-09-20T20:01:54+03:00',
                    },
                    {
                        'id': 'task_5',
                        'login': '',
                        'status': 'reopened',
                        'waiting_time': 300,
                        'updated_ts': '2021-09-20T20:02:24+03:00',
                    },
                    {
                        'id': 'task_6',
                        'login': '',
                        'status': 'forwarded',
                        'waiting_time': 720,
                        'updated_ts': '2021-09-20T20:03:00+03:00',
                    },
                ],
            },
            marks=[
                pytest.mark.pgsql(
                    'support_metrics', files=['pg_support_metrics_1.sql'],
                ),
            ],
        ),
        pytest.param(
            {'statuses': ['accepted', 'in_progress'], 'lines': ['first']},
            200,
            {
                'tasks': [
                    {
                        'id': 'task_2',
                        'login': 'support_1',
                        'status': 'accepted',
                        'waiting_time': 60.0,
                        'updated_ts': '2021-09-20T20:00:49+03:00',
                    },
                ],
            },
            marks=[
                pytest.mark.pgsql(
                    'support_metrics', files=['pg_support_metrics_1.sql'],
                ),
            ],
        ),
        pytest.param(
            {'lower_limit': 60, 'upper_limit': 180},
            200,
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'login': '',
                        'status': 'offered',
                        'waiting_time': 180.0,
                        'updated_ts': '2021-09-20T20:00:13+03:00',
                    },
                    {
                        'id': 'task_2',
                        'login': 'support_1',
                        'status': 'accepted',
                        'waiting_time': 60.0,
                        'updated_ts': '2021-09-20T20:00:49+03:00',
                    },
                ],
            },
            marks=[
                pytest.mark.pgsql(
                    'support_metrics', files=['pg_support_metrics_1.sql'],
                ),
            ],
        ),
        pytest.param(
            {'lines': ['third']},
            200,
            {'tasks': []},
            marks=[
                pytest.mark.pgsql(
                    'support_metrics', files=['pg_support_metrics_1.sql'],
                ),
            ],
        ),
        pytest.param(
            {},
            200,
            {'tasks': []},
            marks=[
                pytest.mark.pgsql(
                    'support_metrics', files=['pg_support_metrics_2.sql'],
                ),
            ],
        ),
    ],
)
async def test_chatterbox_waiting_tasks(
        web_app_client, params, expected_status, expected_response_data,
):
    params_to_send = {}
    for key, value in params.items():
        if isinstance(value, list):
            value = '|'.join(value)
        params_to_send[key] = value
    response = await web_app_client.get(
        '/v1/chatterbox/non-aggregated-stat/waiting-tasks',
        params=params_to_send,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    assert data == expected_response_data
