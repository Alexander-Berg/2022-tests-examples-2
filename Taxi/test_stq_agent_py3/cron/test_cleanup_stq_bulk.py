import pytest

from stq_agent_py3.generated.cron import run_cron


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'example_queue_0'),
        ('stq_2', 'dbstq_2', 'example_queue_1'),
    ],
)
@pytest.mark.now('2021-02-20 10:00:00')
async def test_cleanup_stq_bulk(stq_db):
    await run_cron.main(
        ['stq_agent_py3.crontasks.cleanup_stq_bulk', '-t', '0'],
    )
    for shard in stq_db.iter_shards():
        assert len(await shard.find().to_list(None)) == 1


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'example_queue_0'),
        ('stq_2', 'dbstq_2', 'example_queue_1'),
    ],
)
@pytest.mark.now('2021-02-20 10:00:00')
@pytest.mark.filldb(stq_locks='non_empty')
async def test_cleanup_stq_bulk_locked(stq_db):
    locked_shard = 'dbstq.example_queue_0'

    await run_cron.main(
        ['stq_agent_py3.crontasks.cleanup_stq_bulk', '-t', '0'],
    )
    for shard in stq_db.iter_shards():
        num_docs = len(await shard.find().to_list(None))
        if shard.full_name == locked_shard:
            assert num_docs == 2
        else:
            assert num_docs == 1
