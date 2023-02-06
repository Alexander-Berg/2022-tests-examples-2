# pylint: disable=redefined-outer-name
from corp_edo.generated.cron import run_cron


async def test_example():
    await run_cron.main(['corp_edo.crontasks.example', '-t', '0'])
