import pytest

from crons.generated.cron import run_cron
from crons.lib import thresholds


@pytest.mark.now('2020-10-01T13:05:00')
async def test_collector(cron_context):
    await run_cron.main(['crons.crontasks.collector', '-t', '0'])
    tasks = (
        await cron_context.mongo_wrapper.primary.cron_monitor.find().to_list(
            None,
        )
    )
    tasks_by_id = {task['_id']: task for task in tasks}

    # logs_errors_filters-crontasks-disabler
    task = tasks_by_id['logs_errors_filters-crontasks-disabler']
    assert task['service'] == 'logs_errors_filters'
    assert task['monitoring_status'] == thresholds.CheckStatus.WARN.value
    assert task['monitoring_reason'] == thresholds.MonitoringReason.COUNT.value
    last_launches = task['last_launches']
    assert [launch['link'] for launch in last_launches] == ['2', '3', '4']
    services = (
        await cron_context.mongo_wrapper.primary.cron_services.find().to_list(
            None,
        )
    )
    services_by_id = {service['_id']: service for service in services}
    assert 'logs_errors_filters' in services_by_id

    # check that crit from time threshold overwrite warn from count threshold
    task = tasks_by_id['logs_warnings_filters-crontasks-disabler']
    assert task['service'] == 'logs_warnings_filters'
    assert task['monitoring_status'] == thresholds.CheckStatus.CRIT.value
    assert task['monitoring_reason'] == thresholds.MonitoringReason.TIME.value
    last_launches = task['last_launches']
    assert [launch['link'] for launch in last_launches] == ['12', '13', '14']

    # check warn from time threshold with disabled count threshold
    task = tasks_by_id['logs_info_filters-crontasks-disabler']
    assert task['service'] == 'logs_info_filters'
    assert task['monitoring_status'] == thresholds.CheckStatus.WARN.value
    assert task['monitoring_reason'] == thresholds.MonitoringReason.TIME.value
    last_launches = task['last_launches']
    assert [launch['link'] for launch in last_launches] == ['10']

    # replication-queue_mongo-order_offers
    task = tasks_by_id['replication-queue_mongo-order_offers']
    assert task['service'] == 'replication'
    last_launches = task['last_launches']
    assert [launch['link'] for launch in last_launches] == ['6', '7']
    assert task['monitoring_status'] == thresholds.CheckStatus.CRIT.value
    assert task['monitoring_reason'] == thresholds.MonitoringReason.COUNT.value

    # replication-mysql-eda_bigfood_promo_requirement_items
    task = tasks_by_id['replication-mysql-eda_bigfood_promo_requirement_items']
    assert task['service'] == 'replication'
    last_launches = task['last_launches']
    assert [launch['link'] for launch in last_launches] == ['8']
    assert task['monitoring_status'] == thresholds.CheckStatus.SUCCESS.value
    assert 'monitoring_reason' not in task
