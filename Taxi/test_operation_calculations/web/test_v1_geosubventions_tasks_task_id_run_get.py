import http

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '5f9b08b19da21d52ed964473',
            http.HTTPStatus.OK,
            {'task_id': '5f9b08b19da21d52ed964473'},
        ),
        pytest.param(
            '5f9b08b19da21d53ed964474',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': 'task for task 5f9b08b19da21d53ed964474 not found',
            },
        ),
        pytest.param(
            '5f9b08b19da21d53ed964473',
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'Task 5f9b08b19da21d53ed964473 is already started',
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_run(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{operation_id}/run/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
