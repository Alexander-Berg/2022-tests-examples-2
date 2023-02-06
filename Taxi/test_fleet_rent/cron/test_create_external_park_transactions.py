from fleet_rent.generated.cron import run_cron


async def test_notify(patch):
    @patch(
        'fleet_rent.use_cases.notify_park_on_rent_terminated.'
        'NotifyOnRentTerminated.notify_all_stuck',
    )
    async def _notify_all_stuck():
        pass

    await run_cron.main(
        ['fleet_rent.crontasks.notify_park_on_rent_terminated', '-t', '0'],
    )
