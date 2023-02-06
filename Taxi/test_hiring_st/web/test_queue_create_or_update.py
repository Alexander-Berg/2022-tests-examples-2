async def test_creation(
        web_app_client, load_json, create_workflow, request_queue,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    operation = await request_queue(data2)

    assert operation['status'] == 'pending'
    assert operation['specification']['queue_id'] == data2['queue_id']
    assert operation['specification']['workflow_id'] == data2['workflow_id']
    assert operation['specification']['description'] == data2['description']


async def test_update(
        web_app_client, load_json, create_workflow, request_queue,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    first = await request_queue(data2)

    data3 = load_json('queue.json')
    data3['workflow_id'] = workflow['workflow_id']
    second = await request_queue(data3)

    assert first['operation_id'] != second['operation_id']


async def test_workflow_not_found(web_app_client, load_json, request_queue):
    data = load_json('queue_unknown_workflow.json')
    response = await web_app_client.post('/v1/queue', json=data)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'QUEUE_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'WORKFLOW_NOT_FOUND'


async def test_field_duplicates(
        web_app_client, load_json, create_workflow, request_queue,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue_with_field_duplicates.json')
    data2['workflow_id'] = workflow['workflow_id']
    response = await web_app_client.post('/v1/queue', json=data2)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'QUEUE_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


async def test_multiply_updates(
        web_app_client,
        load_json,
        create_workflow,
        request_queue,
        create_queue,
):
    data = load_json('workflow.json')
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    exists = await create_queue(data2)

    data3 = load_json('queue_with_multiply_updates.json')
    data3['workflow_id'] = workflow['workflow_id']
    data3['queue_id'] = exists['queue_id']
    response = await web_app_client.post('/v1/queue', json=data3)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'QUEUE_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'TOO_MANY_CHANGES'
    assert content['details']['errors'][0]['field'] == 'description'
    assert content['details']['errors'][1]['code'] == 'TOO_MANY_CHANGES'
    assert content['details']['errors'][1]['field'] == 'fields'


async def test_missed_fields(
        web_app_client,
        load_json,
        create_workflow,
        request_queue,
        create_queue,
):
    await create_workflow(load_json('workflow.json'))

    await create_queue(load_json('queue.json'))

    response = await web_app_client.post(
        '/v1/queue', json=load_json('queue_with_missed_fields.json'),
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'QUEUE_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'MISSED_FIELD'
    assert content['details']['errors'][0]['field'] == 'age'
