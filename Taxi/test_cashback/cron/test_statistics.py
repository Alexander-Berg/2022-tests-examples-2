# pylint: disable=redefined-outer-name
import pytest

from cashback.modules import statistics


@pytest.mark.now('2021-08-15T12:00:00+0000')
@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_default_statistics(cron_runner, cron_context):
    await cron_runner.statistics()

    metric = statistics.module.metrics.Metric(application='test')
    sensors = await statistics.module.collect_statistic(cron_context)
    metric.add_sensors(sensors)

    # pylint: disable=protected-access
    assert metric.solomon_data._sensors == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'cashback_processing_orders',
            },
            'value': 1,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'cashback_events.done',
                'currency': 'RUB',
            },
            'value': 2,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'cashback_events.new',
                'currency': 'RUB',
            },
            'value': 2,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'cashback_events.failed',
                'currency': 'RUB',
            },
            'value': 1,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'cashback_events.done',
                'currency': 'EUR',
            },
            'value': 1,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'application': 'test',
                'sensor': 'abandoned',
                'currency': 'RUB',
            },
            'value': 1,
        },
    ]

    await statistics.module.do_statistics_iteration(cron_context)
