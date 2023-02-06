import pytest


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
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                    {
                        'id': 'task_2',
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                    {
                        'id': 'task_3',
                        'login': 'support_1',
                        'waiting_time': 120,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                ],
            },
        ),
        pytest.param(
            {'lines': ['first', 'second']},
            200,
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                    {
                        'id': 'task_2',
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                ],
            },
        ),
        pytest.param(
            {'lower_limit': 50, 'upper_limit': 100},
            200,
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                    {
                        'id': 'task_2',
                        'login': 'superuser',
                        'waiting_time': 60,
                        'updated_ts': '2021-07-20T02:13:21+03:00',
                    },
                ],
            },
        ),
        pytest.param({'lines': 'not_exist'}, 200, {'tasks': []}),
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
        '/v1/chatterbox/non-aggregated-stat/offered-tasks',
        params=params_to_send,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    data = await response.json()
    assert data == expected_response_data
