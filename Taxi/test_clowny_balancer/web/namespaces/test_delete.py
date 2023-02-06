import pytest


@pytest.mark.parametrize(
    'namespace_id, status, expected_response',
    [
        pytest.param(
            1, 200, {'job_id': 1}, id='delete_namespace_n_entry_points',
        ),
        (
            2,
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': 'Not all entry points for namespaces 2 are default',
            },
        ),
        pytest.param(
            3,
            200,
            {'job_id': 1},
            id='delete_only_namespace_no_entry_points_found',
        ),
        (4, 404, {'code': 'NOT_FOUND', 'message': 'Namespace 4 not found'}),
    ],
)
async def test_delete(
        mock_task_processor_start_job,
        taxi_clowny_balancer_web,
        namespace_id,
        status,
        expected_response,
):
    task_processor_mock = mock_task_processor_start_job()
    response = await taxi_clowny_balancer_web.post(
        '/v1/namespaces/delete/', json={'namespace_id': namespace_id},
    )
    assert response.status == status, await response.text()
    assert await response.json() == expected_response
    assert task_processor_mock.times_called == int(status == 200)
