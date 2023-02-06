async def test_task_id_status(taxi_eats_moderation):
    response = await taxi_eats_moderation.get(
        '/moderation/v1/task/status?task_id=123', json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'task_id': '123',
                'status': 'process',
                'payload': '{"data":"qwerty"}',
                'reasons': [],
                'moderator_context': 'Petrov',
                'context': '{"place_id":"1","partner_id":"23"}',
                'queue': 'restapp_moderation_hero',
            },
        ],
    }


async def test_tag_status(taxi_eats_moderation):
    response = await taxi_eats_moderation.get(
        '/moderation/v1/task/status?tag=1', json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'task_id': '123',
                'status': 'process',
                'payload': '{"data":"qwerty"}',
                'reasons': [],
                'moderator_context': 'Petrov',
                'context': '{"place_id":"1","partner_id":"23"}',
                'queue': 'restapp_moderation_hero',
            },
        ],
    }
