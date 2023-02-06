# pylint: disable=redefined-outer-name
from lookup_configs.generated.cron import run_cron


async def test_count_drivers():
    await run_cron.main(['lookup_configs.crontasks.count_drivers', '-t', '0'])
