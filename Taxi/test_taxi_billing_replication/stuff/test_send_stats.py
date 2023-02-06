import pytest

from taxi_billing_replication import cron_run


@pytest.mark.now('2020-04-13T14:15:00+0')
@pytest.mark.usefixtures('fixed_secdist')
@pytest.mark.pgsql('billing_replication', files=['test_send_stats.sql'])
async def test_send_stats(
        patch, billing_replictaion_cron_app, monkeypatch, load_json,
):
    expected_metrics = load_json('expected_sent_metrics.json')
    actual_metrics = []

    # patch GET_OLDEST_UPDATED query because of now() call in origin
    monkeypatch.setattr(
        'taxi_billing_replication.queries.stats.GET_OLDEST_UPDATED',
        """
        SELECT '2020-04-13 14:10:00.000000'::timestamp - MIN(updated)
        FROM {queue_table} WHERE fail_count < 5;
        """,
    )

    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        actual_metrics.extend(data.as_dict()['sensors'])

    module = 'taxi_billing_replication.stuff.send_stats'
    await cron_run.run_replication_task([module, '-t', '0'])
    assert actual_metrics == expected_metrics
