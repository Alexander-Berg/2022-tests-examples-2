# pylint: disable=redefined-outer-name
from jaeger.generated.cron import run_cron


async def test_example():
    await run_cron.main(['jaeger.crontasks.example', '-t', '0'])
