import datetime
import uuid

import pytest

from taxi.util import dates

from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import statistic


TST_DRIVER_ID = '100700_5b05621ee6c22ea2654849c0'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
TIMESTAMP_ISO = TIMESTAMP.isoformat()
TST_ZONE = 'zone3'
TST_EVENT_ID = '743'
UDID = '0'


@pytest.mark.now(TIMESTAMP_ISO)
async def test_process_monitoring_stats(stq3_context, mockserver, patch):

    Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=UDID,
        zone=TST_ZONE,
        event_id=uuid.uuid4().hex,
        value=12,
        mode=Events.ManualValueMode.ADDITIVE,
        reason='Tst reason',
    )

    @mockserver.json_handler(
        f'/driver-metrics-storage/v1/stats/events/unprocessed',
    )
    def patch_get_request(*args, **kwargs):
        return {
            'items': [
                {'count': 1, 'type': '$type'},
                {'count': 300, 'type': 'type1'},
                {'count': 101, 'type': 'type3'},
                {'count': 300, 'type': 'type2'},
                {'count': 299, 'type': 'type0'},
            ],
        }

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def send(*args, **kwags):
        pass

    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def push(*args, **kwags):
        pass

    await statistic.StatisticStqWorker(
        stq3_context, stq3_context.stq.driver_metrics_processing,
    ).do_work(task_id=statistic.MONITORING_STATS_TASK_NAME)

    utc_timestamp = dates.timestamp(TIMESTAMP, 'UTC', False)

    assert patch_get_request.times_called
    assert send.calls == [
        {
            'args': ('driver_metrics.blocking.type.all', 0, utc_timestamp),
            'kwags': {},
        },
        {
            'args': ('driver_metrics.blocking.stale.all', 0, utc_timestamp),
            'kwags': {},
        },
    ]

    solomon_push_data = push.calls[0]['args'][0]

    assert solomon_push_data.as_dict() == {
        'sensors': [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'blocking_aggregate': 'by_types',
                    'blocking_type': 'all',
                    'section': 'blocking_stats',
                },
                'value': 0,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'section': 'blocking_stats',
                    'sensor': 'stale_blocking',
                },
                'value': 0,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': '$type',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 1,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': 'type1',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 300,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': 'type3',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 101,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': 'type2',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 300,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': 'type0',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 299,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': 'driver-metrics',
                    'event_type': 'all',
                    'section': 'events_stats',
                    'sensor': 'overdue_events_count',
                },
                'value': 1001,
            },
        ],
        'ts': utc_timestamp,
    }
