import http

import pytest


@pytest.mark.parametrize(
    'task_id, expected_status, expected_content',
    (
        pytest.param(
            '7557c62d8cef4d1b8c964280a889a86d',
            http.HTTPStatus.OK,
            {
                'stage': 'stage_01',
                'status': 'COMPLETED',
                'task_id': '7557c62d8cef4d1b8c964280a889a86d',
                'updated_at': '2020-02-02 10:00:00',
            },
        ),
        pytest.param(
            'a8d1e267b27949558980b157ac8e8de7',
            http.HTTPStatus.OK,
            {
                'stage': 'stage_00',
                'status': 'FAILED',
                'task_id': 'a8d1e267b27949558980b157ac8e8de7',
                'message': 'Error: error desription',
                'updated_at': '2020-03-03 14:34:40',
            },
        ),
        pytest.param(
            '5778c8cf87fa4681a56de3081580693a',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': 'status for task 5778c8cf87fa4681a56de3081580693a not found',  # noqa: E501
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_multidraft_task.sql'],
)
async def test_v1_geosubventions_multidraft_task_status(
        web_app_client, task_id, expected_status, expected_content,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/multidraft/tasks/{task_id}/status/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
