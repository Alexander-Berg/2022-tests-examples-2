# pylint: disable=redefined-outer-name
from grocery_salaries.generated.cron import run_cron


async def test_example():
    await run_cron.main(['grocery_salaries.crontasks.example', '-t', '0'])
