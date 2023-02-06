# pylint: disable=invalid-name

import uuid


async def test_ticket_find(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        find_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft_scout_old.json')
    data3['queue_id'] = queue['queue_id']
    await create_ticket(data3)

    data4 = load_json('draft_scout_young.json')
    data4['queue_id'] = queue['queue_id']
    await create_ticket(data4)

    data5 = load_json('draft_scout_middle.json')
    data5['queue_id'] = queue['queue_id']
    saved = await create_ticket(data5)

    data6 = load_json('ticket_find.json')
    data6['queue_id'] = queue['queue_id']
    tickets = await find_ticket(data6)
    assert len(tickets) == 1, 'Условия сработали'
    assert tickets[0]['ticket_id'] == saved['ticket_id']


async def test_ticket_find_not_found(
        load_json, create_workflow, create_queue, find_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('ticket_find.json')
    data3['queue_id'] = queue['queue_id']
    tickets = await find_ticket(data3)
    assert not tickets, 'Тикетов не найдено'


async def test_ticket_find_part(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        find_ticket,
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

    data6 = load_json('ticket_find_part.json')
    data6['queue_id'] = queue['queue_id']
    tickets = await find_ticket(data6)
    assert len(tickets[0]['fields']) == 2, 'Возвратили только указанные поля'
    assert filter(lambda x: x['field'] == 'scout_id', tickets[0]['fields'])
    assert filter(lambda x: x['field'] == 'weight', tickets[0]['fields'])


async def test_ticket_find_limit(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        find_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft_scout_middle.json')
    data3['queue_id'] = queue['queue_id']
    await create_ticket(data3)

    data4 = load_json('draft_scout_middle.json')
    data4['queue_id'] = queue['queue_id']
    await create_ticket(data4)

    data5 = load_json('draft_scout_middle.json')
    data5['queue_id'] = queue['queue_id']
    await create_ticket(data5)

    data6 = load_json('ticket_find_limit.json')
    data6['queue_id'] = queue['queue_id']
    tickets = await find_ticket(data6)
    assert len(tickets) == 2, 'Лимит сработал'


async def test_ticket_find_with_field_duplicates_part(
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

    data4 = load_json('ticket_find_with_field_duplicates_part.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/tickets/find', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


async def test_ticket_find_unknown_query(
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

    data4 = load_json('ticket_find_with_field_unknown_query.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/tickets/find', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FILTER_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 0


async def test_ticket_find_unknown_part(
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

    data4 = load_json('ticket_find_with_field_unknown_part.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/tickets/find', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 1


async def test_ticket_find_binary_query(
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

    data4 = load_json('ticket_find_with_field_binary_query.json')
    data4['queue_id'] = queue['queue_id']
    response = await web_app_client.post('/v1/tickets/find', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FILTER_BINARY'
    assert content['details']['errors'][0]['index'] == 1
