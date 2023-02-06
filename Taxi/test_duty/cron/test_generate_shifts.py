# pylint: disable=redefined-outer-name
from duty.generated.cron import run_cron


async def test_generate_shifts():
    await run_cron.main(['duty.crontasks.generate_shifts', '-t', '0'])
