# pylint: disable=invalid-name

import uuid


async def test_update(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data6 = load_json('ticket_update.json')
    data6['ticket_id'] = old['ticket_id']
    new = await update_ticket(data6)

    assert new['ticket_id'] == old['ticket_id']
    assert new['status'] == 'closed'

    scout_id = list(filter(lambda x: x['field'] == 'scout_id', new['fields']))[
        0
    ]
    assert scout_id['revision'] == 1, 'Ревизия не менялась'
    assert scout_id['created_ts'], 'Время создания сохранено'
    assert scout_id['updated_ts'], 'Время обновления сохранено'

    age = list(filter(lambda x: x['field'] == 'age', new['fields']))[0]
    assert age['value'] == '55', 'Значение обновлено'
    assert age['revision'] == 2, 'Ревизия инкрементирована'
    assert age['created_ts'], 'Время создания сохранено'
    assert age['updated_ts'], 'Время обновления установлено'

    weight = list(filter(lambda x: x['field'] == 'weight', new['fields']))[0]
    assert weight['value'] == '99.0', 'Значение обновлено'
    assert weight['revision'] == 2, 'Ревизия инкрементирована'
    assert weight['created_ts'], 'Время создания сохранено'
    assert weight['updated_ts'], 'Время обновления установлено'

    avatar = list(filter(lambda x: x['field'] == 'avatar', new['fields']))
    assert not avatar, 'Значение удалено'


async def test_ticket_not_found(
        web_app_client, load_json, create_workflow, create_queue,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    await create_queue(data2)

    data4 = load_json('ticket_not_found.json')
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data4,
    )
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_NOT_FOUND'


async def test_ticket_update_required(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data4 = load_json('ticket_update_required.json')
    data4['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data4,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'UPDATE_FIELDS_REQUIRED'


async def test_field_not_found_in_set(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('field_not_found_in_set.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 0
    assert content['details']['errors'][1]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][1]['index'] == 2


async def test_field_not_found_in_unset(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('field_not_found_in_unset.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'


async def test_field_deprecated_in_set(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue_field_deprecated.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data5 = load_json('draft_without_depticated_field.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('field_depricated_in_set.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_DEPRECATED'
    assert content['details']['errors'][0]['index'] == 0


async def test_field_deprecated_in_unset(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue_field_deprecated.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data5 = load_json('draft_without_depticated_field.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data6 = load_json('field_depricated_in_unset.json')
    data6['ticket_id'] = old['ticket_id']
    await update_ticket(data6)


async def test_field_duplicate_in_set(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('field_duplicate_in_set.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2
    assert content['details']['errors'][1]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][1]['index'] == 4


async def test_field_duplicate_in_unset(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('field_duplicate_in_unset.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 1


async def test_field_not_integer(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('ticket_field_not_integer.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_INTEGER'
    assert content['details']['errors'][0]['index'] == 0


async def test_field_not_float(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('ticket_field_not_float.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FLOAT'
    assert content['details']['errors'][0]['index'] == 0


async def test_ticket_update_status_no_way(
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

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('ticket_update_status_no_way.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'STATUS_TRANSITION_ERROR'


async def test_ticket_update_status_bad_way(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    data = load_json('workflow_more_statuses.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data5 = load_json('draft.json')
    data5['queue_id'] = queue['queue_id']
    old = await create_ticket(data5)

    data3 = load_json('ticket_update_status_bad_way.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'STATUS_TRANSITION_ERROR'


async def test_ticket_update_status_not_found(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))
    old = await create_ticket(load_json('draft.json'))

    data3 = load_json('ticket_update_status_not_found.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'STATUS_NOT_FOUND'


async def test_ticket_update_resolution_not_found(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))
    old = await create_ticket(load_json('draft.json'))

    data3 = load_json('ticket_update_resolution_not_found.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_NOT_FOUND'


async def test_ticket_update_resolution_required(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))
    old = await create_ticket(load_json('draft.json'))

    data3 = load_json('ticket_update_resolution_required.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_REQUIRED'


async def test_ticket_update_resolution_not_required(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    await create_workflow(load_json('workflow_without_resolutions.json'))
    await create_queue(load_json('queue.json'))
    old = await create_ticket(load_json('draft.json'))

    data3 = load_json('ticket_update.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'RESOLUTION_NOT_REQUIRED'


async def test_ticket_update_resolution_not_terminal(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
):
    await create_workflow(load_json('workflow_more_statuses.json'))
    await create_queue(load_json('queue.json'))
    old = await create_ticket(load_json('draft.json'))

    data3 = load_json('ticket_update_resolution_not_terminal.json')
    data3['ticket_id'] = old['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/update-ticket', json=data3,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code']
        == 'RESOLUTION_NOT_AT_TERMINATE'
    )
