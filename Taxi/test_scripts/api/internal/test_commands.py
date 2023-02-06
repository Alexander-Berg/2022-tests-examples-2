async def test_get_next_command(scripts_client):
    response = await scripts_client.post(
        '/v1/scripts/commands/next/', json={'script_id': '123'},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'sleep_for': 15,
        'command': {
            'name': 'send_signal',
            'id': '123',
            'args': [9],
            'kwargs': {},
        },
    }


async def test_get_oldest_command(scripts_client):
    response = await scripts_client.post(
        '/v1/scripts/commands/next/', json={'script_id': '1234'},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'sleep_for': 15,
        'command': {'name': 'c1', 'id': '12345', 'args': [], 'kwargs': {}},
    }


async def test_apply_commands(mongodb, scripts_client):
    response = await scripts_client.post(
        '/v1/scripts/commands/apply/',
        json={'command_id': '12345', 'status': 'failed'},
    )
    assert response.status == 200

    response = await scripts_client.post(
        '/v1/scripts/commands/apply/',
        json={'command_id': '12346', 'status': 'success'},
    )
    assert response.status == 200

    commands = list(
        mongodb.script_commands.find(
            {'script_id': '1234'}, {'created_at': False, 'updated_at': False},
        ),
    )
    assert commands == [
        {
            '_id': '12345',
            'command': 'c1',
            'script_id': '1234',
            'status': 'failed',
            'args': [],
            'kwargs': {},
        },
        {
            '_id': '12346',
            'command': 'c2',
            'script_id': '1234',
            'status': 'success',
            'args': [],
            'kwargs': {},
        },
    ]
