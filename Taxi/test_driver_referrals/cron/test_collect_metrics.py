# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
from driver_referrals.generated.cron import run_cron


async def test_collect_metrics(patch):
    @patch('taxi.util.graphite.send')
    async def send(*args, **kwargs):
        pass

    await run_cron.main(['driver_referrals.jobs.collect_metrics', '-t', '0'])
