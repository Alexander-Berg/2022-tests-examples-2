# pylint: disable=redefined-outer-name
from supportai_reference_phrases.generated.cron import run_cron


async def test_example():
    await run_cron.main(
        ['supportai_reference_phrases.crontasks.example', '-t', '0'],
    )
