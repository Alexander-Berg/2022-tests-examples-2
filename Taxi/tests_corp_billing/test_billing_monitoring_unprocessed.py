import pytest


@pytest.mark.config(CORP_BILLING_FAILED_TOPICS_MONITORING_ENABLED=True)
@pytest.mark.pgsql('corp_billing', files=('failed_topics.sql',))
async def test_monitoring_unprocessed(taxi_corp_billing, testpoint):
    @testpoint('billing-monitoring-unprocessed-pg-periodic-task-finished')
    def billing_monitoring_finished(data):
        return data

    await taxi_corp_billing.enable_testpoints()
    await taxi_corp_billing.run_periodic_task(
        'billing-monitoring-unprocessed-pg-periodic-task',
    )

    metrics_data = (await billing_monitoring_finished.wait_call())['data']
    assert metrics_data == {
        '$meta': {'solomon_children_labels': 'topic_type'},
        'drive/order': {'count': 2},
        'eats/order': {'count': 1},
        'claim/order': {'count': 0},
        'discount/order': {'count': 0},
    }
