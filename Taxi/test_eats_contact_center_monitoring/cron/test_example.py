# pylint: disable=redefined-outer-name
from eats_contact_center_monitoring.generated.cron import run_cron


async def test_example():
    await run_cron.main(
        ['eats_contact_center_monitoring.crontasks.example', '-t', '0'],
    )
