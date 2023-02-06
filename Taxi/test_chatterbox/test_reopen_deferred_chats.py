import datetime

import bson
import pytest

from chatterbox.crontasks import reopen_deferred_chats

NOW = datetime.datetime(2018, 5, 7, 19, 34)
TASK_UPDATED = datetime.datetime(2018, 5, 7, 12, 34, 56)


@pytest.mark.now(NOW.isoformat())
async def test_reopen_deferred(cbox_context, loop):
    await reopen_deferred_chats.do_stuff(cbox_context, loop)

    task_to_reopen = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task_to_reopen['status'] == 'reopened'
    assert task_to_reopen['history'] == [
        {'action': 'reopen', 'created': NOW, 'login': 'superuser'},
    ]
    assert 'reopen_at' not in task_to_reopen

    task_to_be_deferred = await (
        cbox_context.data.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId('5b2cae5db2682a976914c2a2')},
        )
    )
    assert task_to_be_deferred['status'] == 'deferred'
    assert task_to_be_deferred['reopen_at'] == datetime.datetime(
        2018, 5, 8, 12, 34, 56,
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(support_chatterbox='online')
async def test_reopen_online(cbox_context, loop):
    await reopen_deferred_chats.do_stuff(cbox_context, loop)

    task_to_reopen = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task_to_reopen['status'] == 'ready_to_offer'
    assert task_to_reopen['history'] == [
        {'action': 'reopen_to_offer', 'created': NOW, 'login': 'superuser'},
    ]
    assert 'reopen_at' not in task_to_reopen

    task_to_be_deferred = await (
        cbox_context.data.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId('5b2cae5db2682a976914c2a2')},
        )
    )
    assert task_to_be_deferred['status'] == 'deferred'
    assert task_to_be_deferred['reopen_at'] == datetime.datetime(
        2018, 5, 8, 12, 34, 56,
    )
