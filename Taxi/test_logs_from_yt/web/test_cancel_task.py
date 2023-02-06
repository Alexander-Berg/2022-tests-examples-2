import pytest


@pytest.mark.parametrize(
    ['headers', 'params', 'expected_status', 'expected_json'],
    [
        (
            {'X-YaTaxi-Api-Key': 'foo', 'X-Yandex-Login': 'nevladov'},
            {'task_id': 'task_1'},
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {'task_id': 'task_1'},
            200,
            {},
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'homer'},
            {'task_id': 'task_1'},
            400,
            {
                'code': 'CANCEL_BY_NOT_THE_AUTHOR',
                'message': 'you are not the author of the task "task_1"',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {'task_id': 'task_2'},
            404,
            {
                'code': 'TASK_IS_NOT_FOUND',
                'message': 'task "task_2" is not found',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {'task_id': 'task_3'},
            409,
            {
                'code': 'TASK_HAS_TERMINAL_STATUS',
                'message': 'task "task_3" has terminal status',
            },
        ),
    ],
)
async def test_cancel_task(
        web_app_client, headers, params, expected_status, expected_json,
):
    response = await web_app_client.post(
        '/v1/tasks/cancel/', headers=headers, params=params,
    )
    assert response.status == expected_status
    if expected_json is not None:
        assert expected_json == await response.json()
