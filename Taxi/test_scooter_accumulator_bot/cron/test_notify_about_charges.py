# pylint: disable=redefined-outer-name
from scooter_accumulator_bot.generated.cron import run_cron


async def test_notify_about_charges():
    await run_cron.main(
        ['scooter_accumulator_bot.crontasks.notify_about_charges', '-t', '0'],
    )
