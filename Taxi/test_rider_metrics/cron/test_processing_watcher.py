# pylint: disable=redefined-outer-name

from rider_metrics.generated.cron import run_cron


async def test_processing_watcher():
    await run_cron.main(
        ['rider_metrics.crontasks.processing_watcher', '-t', '0'],
    )
