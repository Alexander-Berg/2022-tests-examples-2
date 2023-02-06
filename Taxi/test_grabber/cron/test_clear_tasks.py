# pylint: disable=redefined-outer-name
from grabber.generated.cron import run_cron


async def test_clear_tasks():
    await run_cron.main(['grabber.crontasks.clear_tasks', '-t', '0'])
