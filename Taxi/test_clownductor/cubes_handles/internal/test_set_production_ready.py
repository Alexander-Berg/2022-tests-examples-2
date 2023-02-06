import pytest


@pytest.mark.usefixtures('mocks_for_service_creation')
async def test_set_production_ready(
        call_cube_handle, add_service, web_context,
):
    await add_service('taxi-devops', 'clownductor')
    service = await web_context.service_manager.services.get_by_id(1)
    assert not service['production_ready']
    data_request = {
        'input_data': {'service_id': 1},
        'job_id': 1,
        'retries': 0,
        'status': 'in_progress',
        'task_id': 1,
    }
    content_expected = {'status': 'success'}
    await call_cube_handle(
        'ServiceSetProductionReady',
        {'data_request': data_request, 'content_expected': content_expected},
    )
    service = await web_context.service_manager.services.get_by_id(1)
    assert service['production_ready']
