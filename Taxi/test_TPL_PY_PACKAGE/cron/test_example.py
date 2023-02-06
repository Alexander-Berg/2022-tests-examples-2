# pylint: disable=redefined-outer-name
from TPL_PY_PACKAGE.generated.cron import run_cron


async def test_example():
    await run_cron.main(['TPL_PY_PACKAGE.crontasks.example', '-t', '0'])
