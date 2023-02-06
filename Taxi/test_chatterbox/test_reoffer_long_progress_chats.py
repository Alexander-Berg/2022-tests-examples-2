# pylint: disable=no-member
import datetime

import bson
import pytest

from chatterbox.crontasks import reoffer_long_progress_tasks

NOW = datetime.datetime(2018, 6, 27, 15, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(support_chatterbox='online')
async def test_reopen_online(cbox_context, stq, loop):
    reoffered_task_ids = [
        bson.ObjectId('5b2cae5cb2682a976914c2a5'),
        bson.ObjectId('5b2cae5cb2682a976914c2a6'),
    ]
    reopened_task_ids = [bson.ObjectId('5b2cae5cb2682a976914c2a7')]

    await reoffer_long_progress_tasks.do_stuff(cbox_context, loop)
    task = await cbox_context.data.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId('5b2cae5cb2682a976914c2a8')},
    )
    assert task['status'] == 'closed'

    reopened_tasks = cbox_context.data.db.support_chatterbox.find(
        {'_id': {'$in': reopened_task_ids}},
    )
    async for task in reopened_tasks:
        assert task['status'] == 'reopened'
        assert task['updated'] == NOW
        assert task['history'] == [
            {'action': 'reopen', 'created': NOW, 'login': 'superuser'},
        ]
    stq_calls = [
        stq.chatterbox_online_chat_processing.next_call()
        for _ in range(stq.chatterbox_online_chat_processing.times_called)
    ]
    assert len(stq_calls) == len(reoffered_task_ids)
    for i, task_id in enumerate(reoffered_task_ids):
        assert stq_calls[i]['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
        assert stq_calls[i]['args'] == [{'$oid': str(task_id)}, []]
