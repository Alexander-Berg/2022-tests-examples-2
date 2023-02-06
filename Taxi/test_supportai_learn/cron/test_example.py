# pylint: disable=redefined-outer-name
from supportai_learn.generated.cron import run_cron


async def test_example():
    await run_cron.main(['supportai_learn.crontasks.example', '-t', '0'])
