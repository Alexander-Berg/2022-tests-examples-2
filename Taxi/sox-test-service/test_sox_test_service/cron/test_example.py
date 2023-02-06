# pylint: disable=redefined-outer-name
from sox_test_service.generated.cron import run_cron


async def test_example():
    await run_cron.main(['sox_test_service.crontasks.example', '-t', '0'])
