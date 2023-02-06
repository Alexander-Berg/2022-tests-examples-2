# pylint: disable=redefined-outer-name
from stq_agent_py3.generated.cron import run_cron


async def test_stq_workers_stat():
    await run_cron.main(
        ['stq_agent_py3.crontasks.stq_workers_stat', '-t', '0'],
    )
