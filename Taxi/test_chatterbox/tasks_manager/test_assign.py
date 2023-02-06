import datetime

import bson
import pytest

from test_chatterbox import plugins as conftest


async def get_task_by_id(cbox: conftest.CboxWrap, task_id: str) -> dict:
    return await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )


@pytest.mark.parametrize(
    ['task_id', 'expected_status_before_assign'],
    [
        ('5b2cae5cb2682a976914c2a1', None),
        ('5b2cae5cb2682a976914c2a2', None),
        ('5b2cae5cb2682a976914c2a3', 'new'),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_assign(
        cbox: conftest.CboxWrap,
        task_id: str,
        expected_status_before_assign: str,
):
    assigned_task = await get_task_by_id(cbox, task_id)

    assigned_task = await cbox.app.tasks_manager.assign(
        assigned_task, 'superuser',
    )
    assert assigned_task['_id'] == bson.ObjectId(task_id)
    assert assigned_task['status'] == 'in_progress'
    assert assigned_task['updated'] == datetime.datetime(2019, 1, 1, 12)
    expected_action = {
        'action': 'assign',
        'login': 'superuser',
        'created': datetime.datetime(2019, 1, 1, 12),
        'line': 'first',
    }
    if expected_status_before_assign is not None:
        expected_action['meta_changes'] = [
            {
                'change_type': 'set',
                'field_name': 'status_before_assign',
                'value': 'new',
            },
        ]
    assert assigned_task['history'] == [expected_action]
    assert (
        assigned_task['meta_info'].get('status_before_assign')
        == expected_status_before_assign
    )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_offer_skip_count '
            'WHERE supporter_login = $1',
            'superuser',
        )
    assert result[0]['offer_skip_count'] == 0


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_assign_old_tasks_change(cbox: conftest.CboxWrap):
    task_for_assign = await get_task_by_id(cbox, '5b2cae5cb2682a976914c2a3')

    await cbox.app.tasks_manager.assign(task_for_assign, 'superuser')

    previous_task = await get_task_by_id(cbox, '5b2cae5cb2682a976914c2a2')
    assert previous_task['status'] == 'in_progress'
    assert previous_task['updated'] == datetime.datetime(2019, 1, 1, 12)
    assert previous_task['history'] == [
        {
            'action': 'take_another_task',
            'login': 'superuser',
            'created': datetime.datetime(2019, 1, 1, 12),
        },
    ]

    old_task = await get_task_by_id(cbox, '5b2cae5cb2682a976914c2a1')
    assert old_task['status'] == 'in_progress'
    assert old_task['updated'] == datetime.datetime(2019, 1, 1, 0)
    assert old_task['history'] == []
