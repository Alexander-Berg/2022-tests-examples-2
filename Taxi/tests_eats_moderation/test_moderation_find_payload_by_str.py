def make_payload(queue, data):
    return {
        'scope': 'eda',
        'queue': queue,
        'external_id': None,
        'value': (
            '{"scope": "eda", "queue": '
            '"' + queue + '", "data": "' + data + '"}'
        ),
    }


def make_moderation(
        ident, task_id, payload_id, status, moderator_id, tag=None,
):
    return {
        'id': ident,
        'task_id': task_id,
        'payload_id': payload_id,
        'status': status,
        'reasons': [],
        'moderator_id': moderator_id,
        'tag': tag,
    }


async def test_moderation_find_payload_by_str_get(taxi_eats_moderation):
    response = await taxi_eats_moderation.get(
        '/moderation/v1/tasks/find_payload_by_str?field=data&value=ert',
    )

    assert response.status_code == 200
    assert response.json() == {'values': ['qwertyui']}

    response2 = await taxi_eats_moderation.get(
        '/moderation/v1/tasks/find_payload_by_str?field=data&value=tyu',
    )
    assert response2.status_code == 200
    assert response2.json() == {'values': ['qwertyui', 'tyuiop']}

    response3 = await taxi_eats_moderation.get(
        '/moderation/v1/tasks/find_payload_by_str?field=data&value=iOp',
    )
    assert response3.status_code == 200
    assert response3.json() == {'values': ['tyuiop']}
