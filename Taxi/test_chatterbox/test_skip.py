import datetime

import bson
import pytest


NOW = datetime.datetime(2019, 12, 5, 12, 15, 0)
SECONDS_IN_DAY = datetime.timedelta(days=1).total_seconds()
SUPPORT_NAME = 'support_1'


async def _assign_task(cbox, login, task_id):
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.execute(
            'INSERT INTO chatterbox.supporter_tasks (supporter_login, task_id)'
            ' VALUES ($1, $2)',
            login,
            task_id,
        )
    return bool(result)


async def _check_tasks_assigned(cbox, login):
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_tasks '
            'WHERE supporter_login = $1',
            login,
        )
    return bool(result)


@pytest.mark.parametrize(
    'task_id, expected_status, expected_task_status, '
    'expected_status_before_assign, expected_skipped_by_list',
    [
        ('bad_id', 400, None, None, None),
        ('5b2cae5cb2682a976914c2a2', 400, None, None, None),
        ('0b2cae5cb2682a976914c2a0', 404, None, None, None),
        (
            '5b2cae5cb2682a976914c2a4',
            200,
            'new',
            None,
            ['support_10', 'support_15', SUPPORT_NAME],
        ),
        ('5b2cae5cb2682a976914c2a1', 200, 'new', 'new', [SUPPORT_NAME]),
        (
            '5b2cae5cb2682a976914c2a3',
            200,
            'reopened',
            'reopened',
            ['support_10', 'support_15', SUPPORT_NAME],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_skip_simple(
        cbox,
        patch_auth,
        task_id,
        expected_status,
        expected_task_status,
        expected_status_before_assign,
        expected_skipped_by_list,
):
    patch_auth(login=SUPPORT_NAME, superuser=True)
    await _assign_task(cbox, SUPPORT_NAME, task_id)
    await cbox.post('/v1/tasks/{0}/skip'.format(task_id))
    assert cbox.status == expected_status

    if expected_status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['updated'] == NOW

        expected_history = [
            {'action': 'skip', 'created': NOW, 'login': SUPPORT_NAME},
        ]

        assert task['history'] == expected_history
        assert task['support_admin'] == 'superuser'
        assert task['skipped_by'] == expected_skipped_by_list
        assert (
            task['meta_info'].get('status_before_assign')
            == expected_status_before_assign
        )
        assert not await _check_tasks_assigned(cbox, SUPPORT_NAME)


async def test_skip_permissions(cbox, patch_auth):
    patch_auth(superuser=False, groups=[], login='simple_user')
    await cbox.post('/v1/tasks/5b2cae5cb2682a976914c2a2/skip')
    assert cbox.status == 403
