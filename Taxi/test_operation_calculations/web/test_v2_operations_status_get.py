import http

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '61711eb7b7e4790047d4fe50',
            http.HTTPStatus.OK,
            {
                'id': '61711eb7b7e4790047d4fe50',
                'status': 'CREATED',
                'message': '',
                'updated_at': '2020-01-01T15:00:00+03:00',
                'updated_by': 'dpano',
            },
        ),
        pytest.param(
            '61711eb7b7e4790047d4fe53', http.HTTPStatus.NOT_FOUND, {},
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_operations_status.sql'],
)
async def test_v2_operations_operation_params_get(
        web_app_client, operation_id, expected_status, expected_content,
):
    response = await web_app_client.get(
        f'/v2/operations/status/', params={'task_id': operation_id},
    )
    assert response.status == expected_status
    if expected_status == http.HTTPStatus.OK:
        assert await response.json() == expected_content
