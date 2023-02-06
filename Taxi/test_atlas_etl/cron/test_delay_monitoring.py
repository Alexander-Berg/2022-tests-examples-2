import datetime

import pytest

from taxi.maintenance import run
from taxi.util import dates

from atlas_etl.crontasks import delay_monitoring


TIMESTAMP_NOW = 1619827200
NOW = datetime.datetime.utcfromtimestamp(TIMESTAMP_NOW)


@pytest.mark.now(NOW.isoformat())
async def test_solomon_stats(cron_context, loop, get_stats_by_label_values):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    await delay_monitoring.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(cron_context, {'sensor': 'delay'})
    assert stats == [
        {
            'kind': 'DGAUGE',
            'labels': {'etl_name': 'ods.weather', 'sensor': 'delay'},
            'timestamp': 1619827200.0,
            'value': 12059100.0,
        },
        {
            'kind': 'DGAUGE',
            'labels': {
                'etl_name': 'opteum.driver_order_metrics',
                'sensor': 'delay',
            },
            'timestamp': 1619827200.0,
            'value': 11022300.0,
        },
        {
            'kind': 'DGAUGE',
            'labels': {'etl_name': 'ods.food_orders', 'sensor': 'delay'},
            'timestamp': 1619827200.0,
            'value': 4470480.0,
        },
        {
            'kind': 'DGAUGE',
            'labels': {
                'etl_name': 'ods.callcenter_call_history',
                'sensor': 'delay',
            },
            'timestamp': 1619827200.0,
            'value': 52314900.0,
        },
        {
            'kind': 'DGAUGE',
            'labels': {'etl_name': 'ods.scooter_orders', 'sensor': 'delay'},
            'timestamp': 1619827200.0,
            'value': 287100.0,
        },
        {
            'kind': 'DGAUGE',
            'labels': {'etl_name': 'ods.scooter_positions', 'sensor': 'delay'},
            'timestamp': 1619827200.0,
            'value': 200700.0,
        },
    ]
