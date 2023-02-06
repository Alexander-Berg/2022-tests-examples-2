# pylint: disable=redefined-outer-name
from selfemployed_fns_receipts.generated.cron import run_cron


async def test_example():
    await run_cron.main(
        ['selfemployed_fns_receipts.crontasks.example', '-t', '0'],
    )
