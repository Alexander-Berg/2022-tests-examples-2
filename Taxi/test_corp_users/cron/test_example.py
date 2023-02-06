# pylint: disable=redefined-outer-name
from corp_users.generated.cron import run_cron


async def test_example():
    await run_cron.main(['corp_users.crontasks.example', '-t', '0'])
