import pytest


async def test_add_kill_command(mongodb, scripts_client):
    response = await scripts_client.post(
        '/1/kill/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    command = list(
        mongodb.script_commands.find(
            {}, {'created_at': False, 'updated_at': False, '_id': False},
        ),
    )
    assert command == [
        {
            'command': 'send_signal',
            'script_id': '1',
            'args': [9],
            'kwargs': {},
            'status': 'queued',
        },
    ]


@pytest.mark.parametrize(
    'script_id, status', [('2', 403), ('non-existing', 404), ('3', 406)],
)
async def test_cant_kill_script(scripts_client, script_id, status):
    response = await scripts_client.post(
        f'/{script_id}/kill/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == status, await response.text()


async def test_kill_twice(scripts_client):
    response = await scripts_client.post(
        '/1/kill/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200

    response = await scripts_client.post(
        '/1/kill/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 406
    assert (await response.json()) == {
        'status': 'error',
        'message': 'Kill command already in queue',
        'code': 'ALREADY_KILLING',
    }
