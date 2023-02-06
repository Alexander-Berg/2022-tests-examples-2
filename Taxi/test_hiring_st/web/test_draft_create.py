import uuid


async def test_creation(
        web_app_client, load_json, create_workflow, create_queue, create_draft,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    draft = await create_draft(data3)

    assert draft['queue_id'] == queue['queue_id']
    assert draft['revision'] == 1
    assert draft['status'] == 'open', 'Установлен начальный статус'


async def test_queue_not_found(web_app_client, load_json):
    data = load_json('draft.json')
    data['queue_id'] = uuid.uuid4().hex
    response = await web_app_client.post('/v1/tickets/create-draft', json=data)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'QUEUE_NOT_FOUND'


async def test_field_not_found(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    data3['set'][0]['field'] = 'UNKNOWN'
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'


async def test_field_deprecated(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue_field_deprecated.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_DEPRECATED'
    assert content['details']['errors'][0]['index'] == 0


async def test_field_duplicate(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    data3['set'] = [
        {'field': 'scout_id', 'value': '100'},
        {'field': 'scout_id', 'value': '102'},
    ]
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 1


async def test_field_not_integer(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft_field_not_integer.json')
    data3['queue_id'] = queue['queue_id']
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_INTEGER'
    assert content['details']['errors'][0]['index'] == 0


async def test_field_not_float(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft_field_not_float.json')
    data3['queue_id'] = queue['queue_id']
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FLOAT'
    assert content['details']['errors'][0]['index'] == 0


async def test_resolution_not_found(
        web_app_client, load_json, create_workflow, create_queue,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    data3 = load_json('draft_resolution_not_found.json')
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_NOT_FOUND'


async def test_resolution_required(
        web_app_client, load_json, create_workflow, create_queue,
):
    await create_workflow(load_json('workflow_single_status.json'))
    await create_queue(load_json('queue.json'))

    data3 = load_json('draft.json')
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_REQUIRED'


async def test_resolution_not_required(
        web_app_client, load_json, create_workflow, create_queue,
):
    await create_workflow(
        load_json('workflow_single_status_without_resolution.json'),
    )
    await create_queue(load_json('queue.json'))

    data3 = load_json('draft_resolution_not_required.json')
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_NOT_REQUIRED'


async def test_resolution_not_terminal(
        web_app_client, load_json, create_workflow, create_queue,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    data3 = load_json('draft_resolution_not_terminal.json')
    response = await web_app_client.post(
        '/v1/tickets/create-draft', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code']
        == 'RESOLUTION_NOT_AT_TERMINATE'
    )
