# pylint: disable=redefined-outer-name, invalid-name

import pytest


@pytest.mark.config(
    HIRING_ST_OPERATION_TIMEOUT=0, HIRING_ST_OPERATION_TIMEOUT_LIMIT=1,
)
async def test_timeout(
        load_json,
        create_workflow,
        request_queue,
        get_operation,
        timeout_operations,
        fake_operations_processing,
):
    await create_workflow(load_json('workflow.json'))

    operation1 = await request_queue(load_json('queue.json'))
    operation2 = await request_queue(load_json('queue.json'))

    processing = await fake_operations_processing()
    assert len(processing) == 2, 'Операции запущены в обработку'

    assert await timeout_operations(), 'Операции сброшены, первая итерация'

    failed = await get_operation({'operation_id': operation1['operation_id']})
    assert failed['status'] == 'failed'
    assert failed['details']['code'] == 'TIMEOUT'

    pending = await get_operation({'operation_id': operation2['operation_id']})
    assert pending['status'] == 'processing'

    assert await timeout_operations(), 'Операции сброшены, вторая итерация'

    failed2 = await get_operation({'operation_id': operation2['operation_id']})
    assert failed2['status'] == 'failed'
    assert failed2['details']['code'] == 'TIMEOUT'
