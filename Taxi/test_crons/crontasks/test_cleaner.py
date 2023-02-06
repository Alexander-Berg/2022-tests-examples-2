import pytest

from crons.generated.cron import run_cron


@pytest.mark.now('2020-10-01T15:00:00')
async def test_cleaner(cron_context):
    await run_cron.main(['crons.crontasks.cleaner', '-t', '0'])
    tasks = (
        await cron_context.mongo_wrapper.primary.cron_monitor.find().to_list(
            None,
        )
    )
    assert len(tasks) == 1
    services = (
        await cron_context.mongo_wrapper.primary.cron_services.find().to_list(
            None,
        )
    )
    assert len(services) == 1
