# pylint: disable=redefined-outer-name
import pytest

from stq_agent_py3.generated.cron import run_cron


@pytest.mark.redis_store(file='redis_workers_stats')
@pytest.mark.now('2021-04-29T15:00+00:00')
async def test_update_hosts_cpu_usages(db):
    await run_cron.main(
        ['stq_agent_py3.crontasks.update_hosts_cpu_usages', '-t', '0'],
    )
    docs = await db.stq_hosts.find().to_list(None)
    assert len(docs) == 1
    cpu_usages = docs[0].get('cpu_usages')
    assert 'updated' in cpu_usages
    assert cpu_usages['value'] == {'some_queue': 6.7}
