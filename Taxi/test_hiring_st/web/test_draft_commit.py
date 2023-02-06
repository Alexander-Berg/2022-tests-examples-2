import uuid


async def test_commit(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_draft,
        commit_draft,
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

    ticket = await commit_draft(draft['ticket_id'])
    assert ticket['ticket_id'] == draft['ticket_id']
    assert ticket['revision'] == 1


async def test_not_found(web_app_client):
    data = {'ticket_id': uuid.uuid4().hex}

    response = await web_app_client.post('/v1/tickets/commit', json=data)
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'DRAFT_NOT_FOUND'
