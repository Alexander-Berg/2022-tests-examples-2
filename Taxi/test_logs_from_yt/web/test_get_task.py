import pytest


@pytest.mark.parametrize(
    ['params', 'expected_status', 'expected_json'],
    [
        (
            {'task_id': 'task_1'},
            200,
            {
                'task_id': 'task_1',
                'status': 'queued',
                'author': 'nevladov',
                'created_at': '2019-06-19T22:00:00+03:00',
                'request': {
                    'filters': [
                        {
                            'key': 'meta_user_id',
                            'value': 'test_user_id',
                            'service_names': ['protocol'],
                        },
                    ],
                    'start_time': '2019-06-08T22:30:00+03:00',
                    'end_time': '2019-06-09T01:30:00+03:00',
                },
                'message': '',
            },
        ),
        (
            {'task_id': 'task_2'},
            404,
            {
                'code': 'TASK_IS_NOT_FOUND',
                'message': 'task "task_2" is not found',
            },
        ),
    ],
)
async def test_get_task(
        web_app_client, params, expected_status, expected_json,
):
    response = await web_app_client.get(
        '/v1/tasks/', headers={'X-YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == expected_status
    if expected_json is not None:
        assert expected_json == await response.json()
