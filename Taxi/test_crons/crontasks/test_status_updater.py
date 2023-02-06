import pytest

from crons.generated.cron import run_cron
from crons.lib import thresholds as th


@pytest.mark.now('2020-10-01T13:05:00')
async def test_status_updater(cron_context):
    await run_cron.main(['crons.crontasks.status_updater', '-t', '0'])
    tasks = (
        await cron_context.mongo_wrapper.primary.cron_monitor.find().to_list(
            None,
        )
    )
    tasks_by_id = {task['_id']: task for task in tasks}

    # logs_errors_filters-crontasks-disabler
    task = tasks_by_id['logs_errors_filters-crontasks-disabler']
    assert task['monitoring_status'] == th.CheckStatus.WARN.value
    assert task['monitoring_reason'] == th.MonitoringReason.COUNT.value

    # replication-queue_mongo-order_offers
    task = tasks_by_id['replication-queue_mongo-order_offers']
    assert task['monitoring_status'] == th.CheckStatus.CRIT.value
    assert task['monitoring_reason'] == th.MonitoringReason.COUNT.value

    # replication-mysql-eda_bigfood_promo_requirement_items
    task = tasks_by_id['replication-mysql-eda_bigfood_promo_requirement_items']
    assert task['monitoring_status'] == th.CheckStatus.SUCCESS.value
    assert task['monitoring_reason'] == th.MonitoringReason.SUCCESS.value
