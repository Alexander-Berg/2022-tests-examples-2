# pylint: disable=import-only-modules
import pytest


@pytest.mark.suspend_periodic_tasks('monitor-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_small.sql',
    ],
)
async def test_monitor(taxi_crm_scheduler, taxi_crm_scheduler_monitor, pgsql):
    await taxi_crm_scheduler.run_periodic_task('monitor-periodic')

    metrics = await taxi_crm_scheduler_monitor.get_metric('monitor-component')
    assert metrics['tasks-success-precise']['crm_policy'] == 0
    assert metrics['tasks-failed-precise']['crm_policy'] == 0
    assert metrics['thread-count']['crm_policy'] == 0
