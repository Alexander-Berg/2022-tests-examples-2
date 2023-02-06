# pylint: disable=no-member
import datetime

import bson
import pytest

NOW = datetime.datetime(2019, 7, 29, 12)


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHAT_LINE_TRANSITIONS={'first': ['corp'], 'second': ['third']},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'third': {'types': ['client']},
        'first': {'mode': 'online', 'types': ['client']},
        'corp': {
            'mode': 'online',
            'types': ['client'],
            'title_tanker': 'lines.corp',
        },
    },
)
@pytest.mark.parametrize(
    'task_id, params, put_task',
    [
        (bson.ObjectId('5b2cae5cb2682a976914c2a1'), {'line': 'corp'}, False),
        (bson.ObjectId('5b2cae5cb2682a976914c2a2'), {'line': 'third'}, False),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_forward(cbox, stq, task_id, params, put_task):
    await cbox.post(
        '/v1/tasks/%s/forward' % task_id,
        params=params,
        data={'themes': ['1', '2'], 'themes_tree': ['1']},
    )
    assert cbox.status == 200
    if put_task:
        assert stq.chatterbox_online_chat_processing.times_called == 1
        call = stq.chatterbox_online_chat_processing.next_call()
        assert call['eta'] == datetime.datetime(1970, 1, 1, 0, 0)
        assert call['args'][0]['$oid'] == task_id
        assert call['args'][1] == []
    else:
        assert not stq.chatterbox_online_chat_processing.has_calls
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            ' FROM chatterbox.supporter_tasks WHERE task_id = $1',
            str(task_id),
        )
        assert result[0]['count'] == 0
