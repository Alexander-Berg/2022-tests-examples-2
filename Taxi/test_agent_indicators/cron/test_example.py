# pylint: disable=redefined-outer-name
from agent_indicators.generated.cron import run_cron


async def test_example():
    await run_cron.main(['agent_indicators.crontasks.example', '-t', '0'])
