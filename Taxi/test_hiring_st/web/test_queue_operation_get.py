import uuid


async def test_get(
        web_app_client,
        load_json,
        create_workflow,
        request_queue,
        get_operation,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    operation = await request_queue(data2)

    data3 = {'operation_id': operation['operation_id']}
    operation2 = await get_operation(data3)

    assert operation2['status'] == 'pending'


async def test_not_found(web_app_client):
    data = {'operation_id': uuid.uuid4().hex}
    response = await web_app_client.get('/v1/queue/operations', params=data)
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'OPERATION_NOT_FOUND'
