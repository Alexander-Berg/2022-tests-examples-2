# pylint: disable=redefined-outer-name
from jaeger_collector.generated.cron import run_cron


async def test_example():
    await run_cron.main(['jaeger_collector.crontasks.example', '-t', '0'])
