# pylint: disable=redefined-outer-name
from hiring_harvester.generated.cron import run_cron


async def test_example():
    await run_cron.main(['hiring_harvester.crontasks.headhunter', '-t', '0'])
