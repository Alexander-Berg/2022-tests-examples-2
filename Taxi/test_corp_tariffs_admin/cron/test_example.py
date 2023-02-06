# pylint: disable=redefined-outer-name
from corp_tariffs_admin.generated.cron import run_cron


async def test_example():
    await run_cron.main(['corp_tariffs_admin.crontasks.example', '-t', '0'])
