# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def check_command(web_app_client):
    async def do_it(
            task_run_id: str, status=200, command='kill', task_name='some',
    ):
        response = await web_app_client.post(
            f'/commands/v1/{command}/check/',
            json={'task_run_id': task_run_id, 'task_name': task_name},
        )
        data = await response.json()
        assert response.status == status, data
        return data

    return do_it


@pytest.fixture
def apply_command(web_app_client):
    async def do_it(
            task_run_id: str, status=200, command='kill', task_name='some',
    ):
        response = await web_app_client.post(
            f'/commands/v1/{command}/apply/',
            json={'task_run_id': task_run_id, 'task_name': task_name},
        )
        data = await response.json()
        assert response.status == status, data
        return data

    return do_it


@pytest.mark.parametrize(
    'task_run_id, status, result',
    [
        (
            'non-exists',
            404,
            {
                'code': 'TASK_NOT_FOUND',
                'message': 'Task for id non-exists not found',
            },
        ),
        (
            'terminated',
            400,
            {
                'code': 'TASK_IS_IN_BAD_STATUS',
                'message': 'Task for id terminated is in terminal status',
            },
        ),
        (
            'has-no-feature',
            400,
            {
                'code': 'TASK_CANT_BE_KILLED',
                'message': (
                    'Cron worker for task has-no-feature '
                    'do not know how to kill itself'
                ),
            },
        ),
        (
            'good-to-kill',
            200,
            {
                'change_doc_id': 'crons_good-to-kill_kill',
                'data': {'task_run_id': 'good-to-kill', 'task_name': 'some'},
            },
        ),
    ],
)
async def test_add_command_check(check_command, task_run_id, status, result):
    assert (
        await check_command(task_run_id=task_run_id, status=status)
    ) == result


@pytest.mark.parametrize(
    'task_run_id, status, result',
    [
        (
            'non-exists',
            404,
            {
                'code': 'TASK_NOT_FOUND',
                'message': 'Task for id non-exists not found',
            },
        ),
        (
            'terminated',
            400,
            {
                'code': 'TASK_IS_IN_BAD_STATUS',
                'message': 'Task for id terminated already finished',
            },
        ),
        ('good-to-kill', 200, {}),
    ],
)
async def test_add_command_apply(
        web_context, apply_command, task_run_id, status, result,
):

    assert (
        await apply_command(task_run_id=task_run_id, status=status)
    ) == result
    if result:
        return
    command = await web_context.mongo_wrapper.primary.cron_commands.find_one(
        {'task_run_id': task_run_id},
        {'_id': False, 'created_at': False, 'updated_at': False},
    )
    assert command == {
        'task_run_id': task_run_id,
        'task_name': 'some',
        'command': 'kill',
        'args': [],
        'kwargs': {'timeout': 10},
        'status': 'queued',
    }


async def test_add_command_check_n_apply(
        web_context, check_command, apply_command,
):
    check_result = await check_command(task_run_id='good-to-kill')
    await apply_command(**check_result['data'])
    command = await web_context.mongo_wrapper.primary.cron_commands.find_one(
        {'task_run_id': check_result['data']['task_run_id']},
        {'_id': False, 'created_at': False, 'updated_at': False},
    )
    assert command == {
        'task_run_id': check_result['data']['task_run_id'],
        'task_name': 'some',
        'command': 'kill',
        'args': [],
        'kwargs': {'timeout': 10},
        'status': 'queued',
    }


@pytest.mark.parametrize(
    'task_run_id, result',
    [
        (
            'good-to-kill',
            {
                'sleep_for': 15,
                'command': {
                    'args': [],
                    'kwargs': {'timeout': 10},
                    'name': 'kill',
                },
            },
        ),
        ('non-existing', {'sleep_for': 15}),
    ],
)
async def test_get_command(web_app_client, apply_command, task_run_id, result):
    await apply_command('good-to-kill')
    response = await web_app_client.post(
        '/commands/v1/get-next/',
        json={
            'task_name': 'some',
            'host': 'some.host',
            'task_run_id': task_run_id,
        },
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == result
