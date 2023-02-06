# pylint: disable=invalid-name,too-many-locals,too-many-arguments
# pylint: disable=too-many-statements

import uuid

import pytest


async def test_oplog(
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
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

    for i in range(1, 5):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

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
    oplog2 = await get_oplog(data7)

    assert len(oplog2['log']) == 2, 'Вторая часть лога получена'

    assert oplog2['log'][0]['ticket_id'] == ticket['ticket_id']
    assert oplog2['log'][0]['revision'] == 4

    assert oplog2['log'][1]['ticket_id'] == ticket['ticket_id']
    assert oplog2['log'][1]['revision'] == 5

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog(data8)

    assert not oplog3['log'], 'Больше записей нет'


async def test_oplog_holes(
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
        oplog_record_hide,
        oplog_record_show,
        decode_cursor,
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

    for i in range(1, 5):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    assert await oplog_record_hide(revision=3), 'Запись номер 3 скрыта'

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    cursor1 = decode_cursor(oplog1['cursor'])
    assert cursor1.last == 4
    assert len(cursor1.holes) == 1, 'Найдена 1 дырка'
    assert cursor1.holes[0].hole_id == 3

    assert len(oplog1['log']) == 3, 'Первая часть лога получена'

    assert oplog1['log'][0]['revision'] == 1
    assert oplog1['log'][1]['revision'] == 2
    assert oplog1['log'][2]['revision'] == 4, 'Запись сохраненная вне очереди'

    assert await oplog_record_show(revision=3), 'Запись номер 3 показана'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog(data7)

    cursor2 = decode_cursor(oplog2['cursor'])
    assert cursor2.last == 5
    assert not cursor2.holes, 'дырок нет'

    assert len(oplog2['log']) == 2, 'Вторая часть лога получена'

    assert oplog2['log'][0]['revision'] == 3, 'Пропущенная запись'
    assert oplog2['log'][1]['revision'] == 5

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog(data8)

    cursor3 = decode_cursor(oplog3['cursor'])
    assert cursor3.last == 5
    assert not cursor3.holes, 'дырок нет'

    assert not oplog3['log'], 'Больше записей нет'


async def test_oplog_long_holes(
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
        oplog_record_hide,
        oplog_record_show,
        decode_cursor,
):
    """
        Тест дырки которая сохрянается долгое время.
        Ожидается что она будет передаваться в курсоре пока не будет закрыта.
    """
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    ticket = await create_ticket(data3)

    for i in range(1, 8):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    assert await oplog_record_hide(revision=3), 'Запись номер 3 скрыта'

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    cursor1 = decode_cursor(oplog1['cursor'])
    assert cursor1.last == 4
    assert len(cursor1.holes) == 1, 'Найдена 1 дырка'
    assert cursor1.holes[0].hole_id == 3

    assert len(oplog1['log']) == 3, 'Первая часть лога получена'

    assert oplog1['log'][0]['revision'] == 1
    assert oplog1['log'][1]['revision'] == 2
    assert oplog1['log'][2]['revision'] == 4

    assert await oplog_record_hide(revision=6), 'Запись номер 6 скрыта'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog(data7)

    cursor2 = decode_cursor(oplog2['cursor'])
    assert cursor2.last == 8
    assert len(cursor2.holes) == 2, 'Найдено 2 дырки'
    assert cursor2.holes[0].hole_id == 3
    assert cursor2.holes[1].hole_id == 6

    assert len(oplog2['log']) == 3, 'Вторая часть лога получена'

    assert oplog2['log'][0]['revision'] == 5
    assert oplog2['log'][1]['revision'] == 7
    assert oplog2['log'][2]['revision'] == 8

    assert await oplog_record_show(revision=3), 'Запись номер 3 показана'
    assert await oplog_record_show(revision=6), 'Запись номер 6 показана'

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog(data8)

    cursor3 = decode_cursor(oplog3['cursor'])
    assert cursor3.last == 8
    assert not cursor3.holes, 'дырок нет'

    assert len(oplog3['log']) == 2, 'Третья часть лога получена'

    assert oplog3['log'][0]['revision'] == 3
    assert oplog3['log'][1]['revision'] == 6

    data9 = load_json('oplog.json')
    data9['queue_id'] = queue['queue_id']
    data9['cursor'] = oplog3['cursor']
    oplog4 = await get_oplog(data9)

    cursor4 = decode_cursor(oplog4['cursor'])
    assert cursor4.last == 8
    assert not cursor4.holes, 'дырок нет'

    assert not oplog4['log'], 'Больше записей нет'


async def test_oplog_double_holes(
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
        oplog_record_hide,
        oplog_record_show,
        decode_cursor,
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

    for i in range(1, 5):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    assert await oplog_record_hide(revision=3), 'Запись номер 3 скрыта'
    assert await oplog_record_hide(revision=4), 'Запись номер 4 скрыта'

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    cursor1 = decode_cursor(oplog1['cursor'])
    assert cursor1.last == 5
    assert len(cursor1.holes) == 2, 'Найдено 2 дырки'
    assert cursor1.holes[0].hole_id == 3
    assert cursor1.holes[1].hole_id == 4

    assert len(oplog1['log']) == 3, 'Первая часть лога получена'

    assert oplog1['log'][0]['revision'] == 1
    assert oplog1['log'][1]['revision'] == 2
    assert oplog1['log'][2]['revision'] == 5

    assert await oplog_record_show(revision=3), 'Запись номер 3 показана'
    assert await oplog_record_show(revision=4), 'Запись номер 4 показана'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog(data7)

    cursor2 = decode_cursor(oplog2['cursor'])
    assert cursor2.last == 5
    assert not cursor2.holes, 'дырок нет'

    assert len(oplog2['log']) == 2, 'Вторая часть лога получена'

    assert oplog2['log'][0]['revision'] == 3, 'Пропущенная запись'
    assert oplog2['log'][1]['revision'] == 4, 'Пропущенная запись'

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog(data8)

    cursor3 = decode_cursor(oplog3['cursor'])
    assert cursor3.last == 5
    assert not cursor3.holes, 'дырок нет'

    assert not oplog3['log'], 'Больше записей нет'


@pytest.mark.config(HIRING_ST_OPLOG_HOLE_TIMEOUT=0)
async def test_oplog_holes_timeout(
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
        oplog_record_hide,
        decode_cursor,
        web_context,
):
    """
        Пропуски живут в курсоре не вечно, а имеют время жизни. Ведь запись
        может просто упасть и пропуск уже никогда не восстановится.
        Тестируем выброс пропуска из курсора.
    """
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data3 = load_json('draft.json')
    data3['queue_id'] = queue['queue_id']
    ticket = await create_ticket(data3)

    for i in range(1, 5):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    assert await oplog_record_hide(revision=3), 'Запись номер 3 скрыта'

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    cursor1 = decode_cursor(oplog1['cursor'])
    assert cursor1.last == 4
    assert len(cursor1.holes) == 1, 'Найдена 1 дырка'
    assert cursor1.holes[0].hole_id == 3

    assert len(oplog1['log']) == 3, 'Первая часть лога получена'

    assert oplog1['log'][0]['revision'] == 1
    assert oplog1['log'][1]['revision'] == 2
    assert oplog1['log'][2]['revision'] == 4

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog(data7)

    cursor2 = decode_cursor(oplog2['cursor'])
    assert cursor2.last == 5
    assert not cursor2.holes, 'дырок нет'

    assert len(oplog2['log']) == 1, 'Вторая часть лога получена'

    assert oplog2['log'][0]['revision'] == 5

    data8 = load_json('oplog.json')
    data8['queue_id'] = queue['queue_id']
    data8['cursor'] = oplog2['cursor']
    oplog3 = await get_oplog(data8)

    cursor3 = decode_cursor(oplog3['cursor'])
    assert cursor3.last == 5
    assert not cursor3.holes, 'дырок нет'

    assert not oplog3['log'], 'Больше записей нет'


async def test_oplog_empty_db(
        load_json, create_workflow, create_queue, get_oplog,
):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    workflow = await create_workflow(data)

    data2 = load_json('queue.json')
    data2['workflow_id'] = workflow['workflow_id']
    queue = await create_queue(data2)

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    assert not oplog1['log'], 'Данных нет'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']
    oplog2 = await get_oplog(data7)

    assert not oplog2['log'], 'Данных нет'


@pytest.mark.config(
    HIRING_ST_TICKET_MOVE_TO_COLD_TIMEOUT=0,
    HIRING_ST_TICKET_MOVE_TO_COLD_LIMIT=3,
)
async def test_oplog_cursor_too_old(  # pylint: disable=too-many-locals
        web_app_client,
        load_json,
        create_workflow,
        create_queue,
        create_ticket,
        update_ticket,
        get_oplog,
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

    for i in range(1, 5):
        data4 = load_json('ticket_update.json')
        data4['ticket_id'] = ticket['ticket_id']
        data4['set'][0]['value'] = str(i)
        await update_ticket(data4)

    data5 = load_json('ticket_closed.json')
    data5['ticket_id'] = ticket['ticket_id']
    await update_ticket(data5)

    data6 = load_json('oplog.json')
    data6['queue_id'] = queue['queue_id']
    oplog1 = await get_oplog(data6)

    assert len(oplog1['log']) == 3, 'Лог получен'

    assert await move_to_slow(), 'Записи перемещены в архив'

    data7 = load_json('oplog.json')
    data7['queue_id'] = queue['queue_id']
    data7['cursor'] = oplog1['cursor']

    response = await web_app_client.post('/v1/oplog', json=data7)
    assert response.status == 410, await response.text()
    content = await response.json()
    assert content['code'] == 'CURSOR_TOO_OLD'


async def test_oplog_with_field_duplicates_part(
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
    response = await web_app_client.post('/v1/oplog', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_FIELDS'
    assert content['details']['errors'][0]['index'] == 2


async def test_oplog_unknown_part(
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
    response = await web_app_client.post('/v1/oplog', json=data4)
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == 'FIND_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'FIELD_NOT_FOUND'
    assert content['details']['errors'][0]['index'] == 1
