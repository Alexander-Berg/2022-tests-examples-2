async def test_v1_operations_operation_statuses_get(web_app_client):
    response = await web_app_client.get('/v1/operations/statuses/')
    assert response.status == 200, await response.json()
    assert await response.json() == {
        'items': ['CREATED', 'STARTED', 'FINISHED', 'FAILED', 'DRAFT_CREATED'],
    }
