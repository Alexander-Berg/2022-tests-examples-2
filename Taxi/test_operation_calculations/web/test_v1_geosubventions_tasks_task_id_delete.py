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
                'message': (
                    'anything for task 5f9b08b19da21d53ed964474 not found'
                ),
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_delete(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
):
    response = await web_app_client.delete(
        f'/v1/geosubventions/tasks/{operation_id}/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
