import http

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '5f9b08b19da21d52ed964473',
            http.HTTPStatus.OK,
            {
                'updated': '1999-01-08 04:05:06',
                'status': 'COMPLETED',
                'stage': ['some_stage'],
                'message': 'some_message',
                'task_id': '5f9b08b19da21d52ed964473',
                'errors': {'some_key': 'some_value'},
            },
        ),
        pytest.param(
            '5f5a4979798bb8702eefddc2',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': (
                    'status for task 5f5a4979798bb8702eefddc2 not found'
                ),
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_status_get(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{operation_id}/status/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
