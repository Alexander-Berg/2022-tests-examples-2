import datetime

import bson
import pytest

from test_chatterbox import plugins as conftest


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    'expected_stq_calls',
    [
        [
            {
                'args': [{'$oid': '5b2cae5cb2682a976914c2a1'}],
                'kwargs': {'action': 'export', 'log_extra': None},
            },
        ],
    ],
)
async def test_export_enqueue_success(
        cbox: conftest.CboxWrap, stq, expected_stq_calls, mock_random_str_uuid,
):
    mock_random_str_uuid()
    doc = await cbox.app.tasks_manager.enqueue_export(
        bson.ObjectId('5b2cae5cb2682a976914c2a1'), 'superuser',
    )
    stq_calls = [
        {'args': call['args'], 'kwargs': call['kwargs']}
        for call in (
            stq.startrack_ticket_import_queue.next_call()
            for _ in range(stq.startrack_ticket_import_queue.times_called)
        )
    ]

    assert stq_calls == expected_stq_calls
    assert doc['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'export',
        'created': datetime.datetime(2019, 1, 1, 12, 0),
        'in_addition': False,
        'line': 'first',
        'login': 'superuser',
    }

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            '5b2cae5cb2682a976914c2a1',
        )
        assert len(result) == 1
        assert result[0]['count'] == 0
