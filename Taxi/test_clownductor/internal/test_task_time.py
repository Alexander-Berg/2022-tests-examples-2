import pytest

from clownductor.internal.tasks import processor
from clownductor.internal.utils import postgres


@pytest.mark.features_off('task_processor_enabled')
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_tasks_time(patch, web_context):
    @patch('clownductor.internal.tasks.processor._get_ready_tasks_ids')
    async def _get_ready_tasks_ids(context, qos_config):
        return [1]

    # pylint: disable=protected-access
    await processor._update_tasks(web_context)

    async with postgres.primary_connect(web_context) as conn:
        task = await conn.fetchrow('select * from task_manager.tasks;')
        job = await conn.fetchrow('select * from task_manager.jobs;')

    assert task['started_at'] is not None
    assert task['real_time'] is not None
    assert task['total_time'] is not None
    assert job['real_time'] is not None
    assert job['total_time'] is not None
