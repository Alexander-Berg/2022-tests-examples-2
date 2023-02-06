# pylint: disable=redefined-outer-name
import uuid

import pytest


@pytest.mark.config(HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0)
async def test_move_to_cold(
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
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

    for i in range(1, 3):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    data5 = load_json('ticket_closed.json')
    data5['ticket_id'] = ticket['ticket_id']
    await update_ticket(data5)

    assert await move_to_slow(), 'Записи перемещены в архив'

    response = await web_app_client.post(
        '/v1/tickets/get-ticket', json={'ticket_id': ticket['ticket_id']},
    )
    assert response.status == 404, await response.text()
