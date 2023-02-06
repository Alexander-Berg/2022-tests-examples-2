# pylint: disable=invalid-name,too-many-locals

import uuid

import pytest


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_oplog_slow(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog_slow,
        move_to_slow,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    ticket = await create_ticket(data3)

    for i in range(1, 4):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    data5 = load_json('ticket_closed.json')
    data5['ticket_id'] = ticket['ticket_id']
    await update_ticket(data5)

    assert await move_to_slow(), 'Записи перемещены в архив'

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog_slow(data6)

    assert len(oplog1['log']) == 3, 'Первая часть лога получена'

    assert oplog1['log'][0]['ticket_id'] == ticket['ticket_id']
    assert oplog1['log'][0]['revision'] == 1

    assert oplog1['log'][1]['ticket_id'] == ticket['ticket_id']
    assert oplog1['log'][1]['revision'] == 2

    assert oplog1['log'][2]['ticket_id'] == ticket['ticket_id']
    assert oplog1['log'][2]['revision'] == 3

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog_slow(data7)

    assert len(oplog2['log']) == 2, 'Вторая часть лога получена'

    assert oplog2['log'][0]['ticket_id'] == ticket['ticket_id']
    assert oplog2['log'][0]['revision'] == 4

    assert oplog2['log'][1]['ticket_id'] == ticket['ticket_id']
    assert oplog2['log'][1]['revision'] == 5

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog_slow(data8)

    assert not oplog3['log'], 'Больше записей нет'


async def test_oplog_slow_empty_db(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog_slow,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog_slow(data6)

    assert not oplog1['log'], 'Данных нет'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog_slow(data7)

    assert not oplog2['log'], 'Данных нет'


async def test_oplog_slow_with_field_duplicates_part(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    await create_ticket(data3)

    data4 = load_json('oplog_with_field_duplicates_part.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/oplog-slow', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


async def test_oplog_slow_unknown_part(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    await create_ticket(data3)

    data4 = load_json('oplog_with_field_unknown_part.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/oplog-slow', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 1
