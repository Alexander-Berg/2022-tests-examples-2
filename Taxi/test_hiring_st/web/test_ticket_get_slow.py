# pylint: disable=invalid-name

import uuid

import pytest


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_get(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_ticket_cold,
        move_to_slow,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    hot = await create_ticket(load_json('draft.json'))
    hot = await update_ticket(
        load_json('ticket_closed.json'), ticket_id=hot['ticket_id'],
    )

    assert await move_to_slow(), 'Записи перемещены в архив'

    cold = await get_ticket_cold(ticket_id=hot['ticket_id'])
    assert cold['ticket_id'] == hot['ticket_id']
    assert cold['revision'] == hot['revision']


async def test_not_found(web_app_client, get_ticket):
    response = await web_app_client.post(
        '/v1/tickets/get-ticket-slow', json={'ticket_id': uuid.uuid4().hex},
    )
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_NOT_FOUND'


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_query_with_field_duplicates(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        move_to_slow,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    hot = await create_ticket(load_json('draft.json'))
    hot = await update_ticket(
        load_json('ticket_closed.json'), ticket_id=hot['ticket_id'],
    )

    assert await move_to_slow(), 'Записи перемещены в архив'

    data = load_json('ticket_query_with_field_duplicates.json')
    data['ticket_id'] = hot['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/get-ticket-slow', json=data,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_ticket_query_with_field_unknown(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        move_to_slow,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    hot = await create_ticket(load_json('draft.json'))
    hot = await update_ticket(
        load_json('ticket_closed.json'), ticket_id=hot['ticket_id'],
    )

    assert await move_to_slow(), 'Записи перемещены в архив'

    data = load_json('ticket_query_with_field_unknown.json')
    data['ticket_id'] = hot['ticket_id']
    response = await web_app_client.post(
        '/v1/tickets/get-ticket-slow', json=data,
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'TICKET_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 2


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_ticket_query_part(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        move_to_slow,
        get_ticket_cold,
):
    await create_workflow(load_json('workflow.json'))
    await create_queue(load_json('queue.json'))

    hot = await create_ticket(load_json('draft.json'))
    hot = await update_ticket(
        load_json('ticket_closed.json'), ticket_id=hot['ticket_id'],
    )

    assert await move_to_slow(), 'Записи перемещены в архив'

    ticket = await get_ticket_cold(
        load_json('ticket_query_part.json'), ticket_id=hot['ticket_id'],
    )

    assert len(ticket['fields']) == 2
    assert filter(lambda x: x['field'] == 'scout_id', ticket['fields'])
    assert filter(lambda x: x['field'] == 'weight', ticket['fields'])
