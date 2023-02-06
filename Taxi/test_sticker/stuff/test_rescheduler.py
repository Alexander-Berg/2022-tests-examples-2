# pylint: disable=protected-access,unused-variable
import os

import pytest

from sticker import dump_manager
from sticker.generated.cron import run_cron


async def test_reschedule(patch, monkeypatch, tmpdir, cron_context):
    monkeypatch.setattr(dump_manager, 'DUMPS_DIR', tmpdir)
    dump_dir = dump_manager._create_dump_dir('run_id_1')
    with open(os.path.join(dump_dir, 'PENDING'), 'w') as fp:
        fp.write('0\n1\n2\n4\n')
    with open(os.path.join(dump_dir, 'SCHEDULED'), 'w') as fp:
        fp.write('3\n')

    @patch('sticker.dump_manager._remove_dump_dir')
    def _remove_dump_dir(dump_dir):
        assert 'run_id_1' in dump_dir

    await run_cron.main(['sticker.stuff.rescheduler', '-t', '0', '-d'])

    async with cron_context.pg.master.acquire() as connection:
        query = 'SELECT * FROM sticker.mail_queue ORDER BY id;'
        rows = await connection.fetch(query)
    assert len(rows) == 8
    assert rows[0]['status'] == 'PENDING'
    assert rows[1]['status'] == 'PROCESSING'
    assert rows[2]['status'] == 'PENDING'
    assert rows[3]['status'] == 'SCHEDULED'
    assert len(_remove_dump_dir.calls) == 1


@pytest.mark.now('2021-02-18T14:10:00')
async def test_sender_emails_rescheduling(patch, mockserver, cron_context):
    @patch('sticker.dump_manager.reschedule_from_dumps')
    async def reschedule_from_dumps(*args, **kwargs):
        pass

    @mockserver.json_handler('/stq-agent/queues/api/add/sticker_send_email')
    async def _mock_stq_agent_queue(request):
        data = request.json
        assert data['task_id'] in ['4', '5']
        return {}

    await run_cron.main(['sticker.stuff.rescheduler', '-t', '0', '-d'])
    assert _mock_stq_agent_queue.times_called == 2
