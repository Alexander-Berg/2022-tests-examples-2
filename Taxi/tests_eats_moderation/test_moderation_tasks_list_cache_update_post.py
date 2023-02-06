TASK1 = {'task_id': '123', 'context_id': 1, 'payload_id': 1, 'tag': None}
TASK2 = {'task_id': '456', 'context_id': 1, 'payload_id': 2, 'tag': None}


def make_payload(queue, data):
    return {
        'scope': 'eda',
        'queue': queue,
        'external_id': None,
        'value': (
            '{"scope":"eda","queue":' '"' + queue + '","data":"' + data + '"}'
        ),
    }


def make_moderation(
        ident,
        task_id,
        payload_id,
        status,
        moderator_id,
        reasons=None,
        tag=None,
):
    if not reasons:
        reasons = []
    return {
        'id': ident,
        'task_id': task_id,
        'payload_id': payload_id,
        'status': status,
        'moderator_id': moderator_id,
        'tag': tag,
        'reasons': reasons,
    }


def make_item(
        task_id,
        status,
        queue,
        data,
        moderator_context,
        reasons=None,
        context='',
):
    if not reasons:
        reasons = []
    return {
        'task_id': task_id,
        'status': status,
        'payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + data + '"}'
        ),
        'reasons': reasons,
        'moderator_context': moderator_context,
        'context': context,
        'queue': queue,
    }


def make_item_a(
        task_id, status, queue, data, adata, moderator_context, context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': (
            '{"scope":"eda", '
            '"queue":"' + queue + '", '
            '"data":"' + data + '"}'
        ),
        'actual_payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + adata + '"}'
        ),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'queue': queue,
    }


def make_history(status, queue, data, moderator):
    return {
        'status': status,
        'payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + data + '"}'
        ),
        'reasons': [],
        'moderator_context': moderator,
    }


def make_item_history(
        task_id, status, queue, data, moderator_context, history, context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + data + '"}'
        ),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'history': history,
        'queue': queue,
    }


def make_item_history_a(
        task_id,
        status,
        queue,
        data,
        adata,
        moderator_context,
        history,
        context='',
):
    return {
        'task_id': task_id,
        'status': status,
        'payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + data + '"}'
        ),
        'actual_payload': (
            '{"scope":"eda",'
            '"queue":"' + queue + '",'
            '"data":"' + adata + '"}'
        ),
        'reasons': [],
        'moderator_context': moderator_context,
        'context': context,
        'history': history,
        'queue': queue,
    }


async def test_moderation_tasks_list_post(
        taxi_eats_moderation,
        insert_moderation_task,
        insert_context,
        insert_payload,
        insert_moderator,
        insert_moderation,
        insert_reason,
):
    insert_moderation_task(
        task_id=TASK1['task_id'],
        context_id=TASK1['context_id'],
        payload_id=TASK1['payload_id'],
        tag=TASK1['tag'],
    )

    insert_context(value='{"place_id": 1234567}')

    payload = make_payload('restapp_moderation_hero', 'qwerty')
    insert_payload(
        scope=payload['scope'],
        queue=payload['queue'],
        external_id=payload['external_id'],
        value=payload['value'],
    )

    insert_moderator(value='Petrov')

    moderation = make_moderation('456', '123', 1, 'process', 1)
    insert_moderation(
        ident=moderation['id'],
        task_id=moderation['task_id'],
        payload_id=moderation['payload_id'],
        status=moderation['status'],
        moderator_id=moderation['moderator_id'],
        tag=moderation['tag'],
        reasons=moderation['reasons'],
    )

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks/list', json={},
    )
    assert response.status_code == 200
    json = response.json()
    assert json == {
        'items': [
            make_item(
                '123',
                'process',
                'restapp_moderation_hero',
                'qwerty',
                'Petrov',
                context='{"place_id":1234567}',
            ),
        ],
    }

    insert_moderation_task(
        task_id=TASK2['task_id'],
        context_id=TASK2['context_id'],
        payload_id=TASK2['payload_id'],
        tag=TASK2['tag'],
    )

    payload = make_payload('restapp_moderation_hero', 'ytrewq')
    insert_payload(
        scope=payload['scope'],
        queue=payload['queue'],
        external_id=payload['external_id'],
        value=payload['value'],
    )

    moderation = make_moderation('789', '456', 2, 'process', 1)
    insert_moderation(
        ident=moderation['id'],
        task_id=moderation['task_id'],
        payload_id=moderation['payload_id'],
        status=moderation['status'],
        moderator_id=moderation['moderator_id'],
        tag=moderation['tag'],
        reasons=moderation['reasons'],
    )

    await taxi_eats_moderation.invalidate_caches(clean_update=False)

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks/list', json={'pagination': {'limit': 0}},
    )
    assert response.status_code == 200
    json = response.json()
    assert json == {'items': []}

    insert_moderator(value='Ivanov')
    moderation = make_moderation('012', '456', 2, 'rejected', 2, [1])
    insert_moderation(
        ident=moderation['id'],
        task_id=moderation['task_id'],
        payload_id=moderation['payload_id'],
        status=moderation['status'],
        moderator_id=moderation['moderator_id'],
        tag=moderation['tag'],
        reasons=moderation['reasons'],
    )
    for reason in moderation['reasons']:
        insert_reason(str(reason), str(reason))

    await taxi_eats_moderation.invalidate_caches(clean_update=False)

    response = await taxi_eats_moderation.post(
        '/moderation/v1/tasks/list', json={},
    )
    assert response.status_code == 200
    json = response.json()
    assert json == {
        'items': [
            make_item(
                '123',
                'process',
                'restapp_moderation_hero',
                'qwerty',
                'Petrov',
                context='{"place_id":1234567}',
                reasons=[],
            ),
            make_item(
                '456',
                'rejected',
                'restapp_moderation_hero',
                'ytrewq',
                'Ivanov',
                reasons=[{'reason_title': '1', 'reason_text': '1'}],
                context='{"place_id":1234567}',
            ),
        ],
    }
