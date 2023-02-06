import pytest

from testsuite.utils import matching


@pytest.mark.usefixtures('mock_clownductor_handlers')
@pytest.mark.parametrize('use_draft', [True, False])
@pytest.mark.parametrize(
    'entry_point_id, expected_code, expected_result',
    [
        (
            123,
            404,
            {'code': 'NOT_FOUND', 'message': 'Entry point 123 not found'},
        ),
        (1, 200, {'job_id': 1}),
    ],
)
async def test_delete(
        mock_task_processor,
        taxi_clowny_balancer_web,
        use_draft,
        entry_point_id,
        expected_code,
        expected_result,
):
    @mock_task_processor('/v1/jobs/start/')
    def _handler(request):
        assert request.json == {
            'change_doc_id': 'RemoveEntryPointWrapper-1',
            'idempotency_token': matching.any_string,
            'job_vars': {'entry_point_id': 1},
            'provider_name': 'clowny-balancer',
            'recipe_name': 'RemoveEntryPointWrapper',
        }
        return {'job_id': 1}

    if not use_draft:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/delete/', json={'id': entry_point_id},
        )
        result = await response.json()
        assert response.status == expected_code, result
        assert result == expected_result
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/delete/check/', json={'id': entry_point_id},
    )
    result = await response.json()
    assert response.status == expected_code, result
    if expected_result != 200:
        return
    assert result['tickets']
    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/delete/apply/', json=result['data'],
    )
    assert response.status == expected_code, result
    if expected_result is not None:
        assert result == expected_result
