# pylint: disable=redefined-outer-name, invalid-name

import pytest


async def test_create(
        load_json,
        create_workflow,
        request_queue,
        get_operation,
        get_queue,
        save_queues,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    pending = await request_queue(data2)

    await save_queues()

    done = await get_operation({'operation_id': pending['operation_id']})
    assert done['operation_id'] == pending['operation_id']
    assert done['status'] == 'done'
    assert done['details']['code'] == 'QUEUE_SAVED'

    queue = await get_queue({'queue_id': data2['queue_id']})
    assert queue['queue_id'] == data2['queue_id']
    assert queue['workflow_id'] == workflow['workflow_id']
    assert queue['revision'] == 1


async def test_update_description(
        load_json,
        create_workflow,
        request_queue,
        get_operation,
        get_queue,
        save_queues,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    operation1 = await request_queue(data2, description='Новая очередь')

    data3 = load_json('queue.json')
    operation2 = await request_queue(data3, description='Обновленная очередь')

    await save_queues()

    done = await get_operation({'operation_id': operation1['operation_id']})
    assert done['status'] == 'done'
    assert done['details']['code'] == 'QUEUE_SAVED'
    done2 = await get_operation({'operation_id': operation2['operation_id']})
    assert done2['status'] == 'done'
    assert done2['details']['code'] == 'QUEUE_SAVED'

    queue2 = await get_queue({'queue_id': data2['queue_id']})
    assert queue2['queue_id'] == data2['queue_id']
    assert queue2['workflow_id'] == workflow['workflow_id']
    assert queue2['description'] == 'Обновленная очередь'
    assert queue2['revision'] == 2


async def test_update_workflow(
        load_json,
        create_workflow,
        request_queue,
        get_operation,
        get_queue,
        save_queues,
):
    workflow1 = await create_workflow(load_json('workflow.json'))
    workflow2 = await create_workflow(load_json('workflow_v2.json'))
    assert workflow2['workflow_id'] != workflow1['workflow_id'], 'Точно разные'

    data1 = load_json('queue.json')
    data1['workflow_id'] = workflow1['workflow_id']
    operation1 = await request_queue(data1)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow2['workflow_id']
    operation2 = await request_queue(data2)

    await save_queues()

    done = await get_operation({'operation_id': operation1['operation_id']})
    assert done['status'] == 'done'
    assert done['details']['code'] == 'QUEUE_SAVED'
    done2 = await get_operation({'operation_id': operation2['operation_id']})
    assert done2['status'] == 'done'
    assert done2['details']['code'] == 'QUEUE_SAVED'

    queue = await get_queue({'queue_id': data2['queue_id']})
    assert (
        queue['workflow_id'] == workflow2['workflow_id']
    ), 'Новый рабочий процесс установлен'
    assert queue['revision'] == 2, 'Ревизия установлена верно'


async def test_update_workflow_status_fail_hot(
        load_json,
        create_workflow,
        create_queue,
        request_queue,
        get_operation,
        get_queue,
        create_ticket,
        update_ticket,
        save_queues,
):
    """
    Проверяем что операция фейлится если тикет из горячего хранилища
    находится в статусе которого нет в новом рабочем процессе.
    """

    workflow_less_statuses = await create_workflow(load_json('workflow.json'))
    workflow_more_statuses = await create_workflow(
        load_json('workflow_v2.json'),
    )
    assert (
        workflow_less_statuses['workflow_id']
        != workflow_more_statuses['workflow_id']
    ), 'Точно разные'

    queue = await create_queue(
        load_json('queue.json'),
        workflow_id=workflow_more_statuses['workflow_id'],
    )

    ticket = await create_ticket(load_json('draft.json'))
    ticket = await update_ticket(
        load_json('ticket_set_status_process.json'),
        ticket_id=ticket['ticket_id'],
    )

    operation = await request_queue(
        load_json('queue.json'),
        workflow_id=workflow_less_statuses['workflow_id'],
    )

    assert await save_queues(), 'Операция сохранения выполнена'

    failed = await get_operation({'operation_id': operation['operation_id']})
    assert failed['status'] == 'failed'
    assert failed['details']['code'] == 'TICKET_STATUS_ERROR'

    queue = await get_queue({'queue_id': queue['queue_id']})
    assert (
        queue['workflow_id'] == workflow_more_statuses['workflow_id']
    ), 'Рабочий процесс не изменился'

    assert queue['revision'] == 1, 'Ревизия установлена верно'


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_update_workflow_status_fail_cold(
        load_json,
        create_workflow,
        create_queue,
        request_queue,
        get_operation,
        get_queue,
        create_ticket,
        update_ticket,
        save_queues,
        move_to_slow,
):
    """
    Проверяем что операция фейлится если тикет из холодного хранилища
    находится в статусе которого нет в новом рабочем процессе.
    """

    workflow_orig = await create_workflow(load_json('workflow.json'))
    workflow_changed = await create_workflow(load_json('workflow_v3.json'))
    assert (
        workflow_orig['workflow_id'] != workflow_changed['workflow_id']
    ), 'Точно разные'

    queue = await create_queue(
        load_json('queue.json'), workflow_id=workflow_orig['workflow_id'],
    )

    ticket = await create_ticket(load_json('draft.json'))
    ticket = await update_ticket(
        load_json('ticket_set_status_closed.json'),
        ticket_id=ticket['ticket_id'],
    )

    assert await move_to_slow(), 'Записи перемещены в архив'

    operation = await request_queue(
        load_json('queue.json'), workflow_id=workflow_changed['workflow_id'],
    )

    assert await save_queues(), 'Операция сохранения выполнена'

    failed = await get_operation({'operation_id': operation['operation_id']})
    assert failed['status'] == 'failed'
    assert failed['details']['code'] == 'TICKET_STATUS_ERROR'

    queue = await get_queue({'queue_id': queue['queue_id']})
    assert (
        queue['workflow_id'] == workflow_orig['workflow_id']
    ), 'Рабочий процесс не изменился'

    assert queue['revision'] == 1, 'Ревизия установлена верно'
