# pylint: disable=redefined-outer-name
from segment_splitter.generated.cron import run_cron


async def test_cron_run_spark():
    await run_cron.main(['segment_splitter.crontasks.run_cron', '-t', '0'])
