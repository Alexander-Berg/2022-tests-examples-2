# pylint: disable=redefined-outer-name
from hiring_trigger_zend.generated.cron import run_cron


async def test_example():
    await run_cron.main(['hiring_trigger_zend.crontasks.example', '-t', '0'])
