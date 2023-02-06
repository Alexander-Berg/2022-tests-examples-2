import datetime

import bson
import pytest


NOW = datetime.datetime(2019, 12, 5, 12, 15, 0)
SECONDS_IN_DAY = datetime.timedelta(days=1).total_seconds()


async def _check_tasks_assigned(cbox, login):
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks '
            'WHERE supporter_login = $1',
            login,
        )
    return bool(result)


@pytest.mark.config(
    CHATTERBOX_LINES={
        'garbage': {
            'name': 'Тест мува',
            'types': ['client'],
            'priority': 4,
            'sort_order': 1,
        },
    },
)
@pytest.mark.parametrize(
    'task_id, params, expected_status',
    [
        ('5b2cae5cb2682a976914c2a1', {}, 400),
        ('5b2cae5cb2682a976914c2a1', {'line': 'garbage'}, 200),
        (
            '5b2cae5cb2682a976914c2a1',
            {'line': 'garbage', 'status': 'archived'},
            200,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_move_simple(cbox, patch_auth, task_id, params, expected_status):
    patch_auth(login='support', superuser=True)
    await cbox.post('/v1/tasks/{0}/move'.format(task_id), params=params)
    assert cbox.status == expected_status

    if expected_status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['line'] == params['line']
        assert task['updated'] == NOW

        expected_history = [
            {
                'action': 'move',
                'created': NOW,
                'login': 'support',
                'line': 'first',
                'new_line': params['line'],
                'status': 'in_progress',
            },
        ]

        if params.get('status'):
            assert task['status'] == params['status']
            expected_history[0]['new_status'] = params['status']

        assert task['history'] == expected_history
        assert task['support_admin'] == 'superuser'

        assert not await _check_tasks_assigned(cbox, 'support')

        await cbox.post('/v1/tasks/take/', data={})
        assert cbox.status == 404


@pytest.mark.translations(
    chatterbox={
        'errors.moving_task_in_external_status': {
            'ru': 'Перемещать тикет в статусе {status} запрещено',
            'en': 'It is not allowed to move ticket in status {status}',
        },
    },
)
@pytest.mark.parametrize(
    'locale, error_message',
    [
        ('ru', 'Перемещать тикет в статусе archived запрещено'),
        ('en', 'It is not allowed to move ticket in status archived'),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_task_in_external_status(cbox, locale, error_message):
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a2/move',
        params={'line': 'garbage'},
        headers={'Accept-Language': locale},
    )
    assert cbox.status == 400
    assert cbox.body_data == {
        'message': error_message,
        'status': 'request_error',
    }


async def test_move_permissions(cbox, patch_auth):
    patch_auth(superuser=False, groups=[], login='simple_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a2/move', params={'line': 'garbage'},
    )
    assert cbox.status == 403
