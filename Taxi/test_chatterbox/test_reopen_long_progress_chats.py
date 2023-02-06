# pylint: disable=no-member
import datetime

import bson
import pytest

from chatterbox.crontasks import reopen_long_progress_chats

NOW = datetime.datetime(2018, 6, 27, 15, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_AUTOREPLY_DELAY_RANGE=[600, 600],
    CHATTERBOX_DRIVERS_AUTOREPLY_DELAY_RANGE=[60, 60],
    CHATTERBOX_SMS_AUTOREPLY_DELAY_RANGE=[3600, 3600],
    REOPEN_LONG_TECHNICAL=True,
    TECHNICAL_STATUSES=['predispatch', 'routing'],
    CHATTERBOX_LINES={
        'second': {'types': ['client'], 'autoreply': True},
        'first': {'types': ['client'], 'autoreply': True},
    },
)
@pytest.mark.parametrize(
    'task_id_str,expected_status',
    [
        ('5b2cae5cb2682a976914c2a1', 'reopened'),
        ('5b2cae5db2682a976914c2a2', 'in_progress'),
        ('5b2cae5db2682a976914c2a3', 'reopened'),
        ('5b2cae5db2682a976914c2a4', 'autoreply_in_progress'),
        ('5b2cae5db2682a976914c2a5', 'reopened'),
        ('5b2cae5db2682a976914c2a6', 'autoreply_in_progress'),
        ('5b2cae5db2682a976914c2a7', 'reopened'),
        ('5b2cae5db2682a976914c2a8', 'autoreply_in_progress'),
        ('5b2cae5db2682a976914c2a9', 'reopened'),
        ('5b2cae5db2682a976914c2b0', 'autoreply_in_progress'),
        ('5b2cae5cb2682a976914c2b1', 'reopened'),
        ('5b2cae5cb2682a976914c2b2', 'predispatch'),
        ('5b2cae5cb2682a976914c2b3', 'reopened'),
        ('5b2cae5cb2682a976914c2b4', 'routing'),
    ],
)
async def test_reopen_long_progress(
        cbox_context, loop, task_id_str, expected_status,
):
    old_task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id_str)},
    )
    await reopen_long_progress_chats.do_stuff(cbox_context, loop)
    task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id_str)},
    )
    assert task['status'] == expected_status
    if expected_status == 'reopened':
        assert task['updated'] == NOW
        assert task['history'] == [
            {'action': 'reopen', 'created': NOW, 'login': 'superuser'},
        ]
    else:
        assert task['updated'] == old_task['updated']
        assert 'history' not in task


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(support_chatterbox='online')
@pytest.mark.config(
    STAY_IN_PROGRESS_TIME={'__default__': 40, 'corp': 10},
    REOPEN_LONG_TECHNICAL=True,
    TECHNICAL_STATUSES=['predispatch', 'routing'],
    CHATTERBOX_LONG_PROGRESS_STATUSES={
        'online': ['new', 'forwarded', 'accepted', 'in_progress'],
    },
)
async def test_reopen_online(cbox_context, stq, loop):
    reoffered_task_ids = [
        bson.ObjectId('5b2cae5cb2682a976914c2a5'),
        bson.ObjectId('5b2cae5cb2682a976914c2a6'),
        bson.ObjectId('5b2cae5cb2682a976914c2a7'),
        bson.ObjectId('5b2cae5cb2682a976914c2aa'),
        bson.ObjectId('5b2cae5cb2682a976914c2ab'),
        bson.ObjectId('5b2cae5cb2682a976914c2a9'),
        bson.ObjectId('5b2cae5cb2682a976914c2a1'),
    ]
    await reopen_long_progress_chats.do_stuff(cbox_context, loop)
    reoffered_tasks = cbox_context.data.db.support_chatterbox.find(
        {'_id': {'$in': reoffered_task_ids}},
    )
    async for task in reoffered_tasks:
        assert task['status'] == 'ready_to_offer'
        assert task['updated'] == NOW
        assert task['history'] == [
            {
                'action': 'reopen_to_offer',
                'created': NOW,
                'login': 'superuser',
            },
        ]

    task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId('5b2cae5cb2682a976914c2a0')},
    )
    assert task['status'] == 'predispatch'
    assert task.get('history', []) == []

    task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId('5b2cae5cb2682a976914c2a2')},
    )
    assert task['status'] == 'routing'
    assert task.get('history', []) == []

    stq_calls = [
        stq.chatterbox_online_chat_processing.next_call()
        for _ in range(stq.chatterbox_online_chat_processing.times_called)
    ]
    assert len(stq_calls) == len(reoffered_task_ids)
    for stq_call in stq_calls:
        assert stq_call['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
        assert bson.ObjectId(stq_call['args'][0]['$oid']) in reoffered_task_ids
    async with cbox_context.data.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)' ' FROM chatterbox.supporter_tasks',
        )
        assert result[0]['count'] == 0
