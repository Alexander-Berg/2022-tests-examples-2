import uuid


async def test_get(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        get_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    saved = await create_ticket(data3)

    ticket = await get_ticket({'ticket_id': saved['ticket_id']})
    assert ticket['ticket_id'] == saved['ticket_id']
    assert ticket['revision'] == saved['revision']


async def test_not_found(web_app_client, get_ticket):
    response = await web_app_client.post(
        '/v1/tickets/get-ticket', json={'ticket_id': uuid.uuid4().hex},
    )
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_NOT_FOUND'


async def test_query_with_field_duplicates(  # pylint: disable=invalid-name
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        get_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    saved = await create_ticket(data3)

    data4 = load_json('ticket_query_with_field_duplicates.json')
    data4['ticket_id'] = saved['ticket_id']
    response = await web_app_client.post('/v1/tickets/get-ticket', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


async def test_ticket_query_with_field_unknown(  # pylint: disable=invalid-name
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        get_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    saved = await create_ticket(data3)

    data4 = load_json('ticket_query_with_field_unknown.json')
    data4['ticket_id'] = saved['ticket_id']
    response = await web_app_client.post('/v1/tickets/get-ticket', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 2


async def test_ticket_query_part(  # pylint: disable=invalid-name
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        get_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    saved = await create_ticket(data3)

    data4 = load_json('ticket_query_part.json')
    data4['ticket_id'] = saved['ticket_id']
    ticket = await get_ticket(data4)

    assert len(ticket['fields']) == 2
    assert filter(lambda x: x['field'] == 'scout_id', ticket['fields'])
    assert filter(lambda x: x['field'] == 'weight', ticket['fields'])
