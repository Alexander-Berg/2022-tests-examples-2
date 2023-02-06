# pylint: disable=redefined-outer-name
from flot.generated.cron import run_cron


async def test_example():
    await run_cron.main(['flot.crontasks.example', '-t', '0'])
