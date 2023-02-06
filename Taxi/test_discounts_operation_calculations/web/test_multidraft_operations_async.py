import http

import pytest


@pytest.mark.parametrize(
    'task_id, expected_status, expected_content',
    (
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d73',
            http.HTTPStatus.OK,
            {'status': 'COMPLETED', 'updated_at': '2020-02-03 10:00:00'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d76',
            http.HTTPStatus.OK,
            {'status': 'FAILED', 'updated_at': '2020-02-03 10:00:00'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d83',
            http.HTTPStatus.OK,
            {'status': 'COMPLETED', 'updated_at': '2020-02-03 10:00:00'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d96',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'BadRequest::TaskNotFound',
                'message': 'status for task a8d1e267b27949558980b157ac8e8d96 not found',  # noqa: E501
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_multidraft_tasks.sql'],
)
async def test_get_multidraft_task_status(
        web_app_client, task_id, expected_status, expected_content,
):
    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/status/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content


@pytest.mark.parametrize(
    'task_id, expected_status, expected_content',
    (
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d73',
            http.HTTPStatus.OK,
            {'multidraft': 'test_url/multidraft/42/?multi=true'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d74',
            http.HTTPStatus.CONFLICT,
            {
                'code': 'Conflict::TaskNotCompleted',
                'message': (
                    'Task status_info: id: a8d1e267b27949558980b157ac8e8d74, '
                    'status: CREATED, updated_at: 2020-02-03 10:00:00'
                ),
            },
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d75',
            http.HTTPStatus.CONFLICT,
            {
                'code': 'Conflict::TaskNotCompleted',
                'message': (
                    'Task status_info: id: a8d1e267b27949558980b157ac8e8d75, '
                    'status: RUNNING, updated_at: 2020-02-03 10:00:00'
                ),
            },
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d76',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest::EmptyDiscountsToCreate',
                'message': 'No discounts to create!',
            },
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d77',
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'RuntimeError::UnknownError', 'message': 'unknown error'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d83',
            http.HTTPStatus.OK,
            {'multidraft': 'test_url/multidraft/42/?multi=true'},
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d84',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest::NoDiscountsToStop',
                'message': 'No discounts to stop!',
            },
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8d96',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'BadRequest::TaskNotFound',
                'message': 'status for task a8d1e267b27949558980b157ac8e8d96 not found',  # noqa: E501
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_multidraft_tasks.sql'],
)
async def test_get_multidraft_task_result(
        web_app_client, task_id, expected_status, expected_content,
):
    response = await web_app_client.get(
        f'/v1/multidraft/tasks/{task_id}/result/',
    )

    assert response.status == expected_status
    assert await response.json() == expected_content
