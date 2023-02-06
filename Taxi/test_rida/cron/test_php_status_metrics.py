import asyncio

import pytest

from taxi.maintenance import run
from taxi.util import dates

from rida.crontasks import send_php_status_metrics


@pytest.mark.now('2021-11-20T11:00:00.0')
async def test_php_status_metrics(
        cron_context, mockserver, get_stats_by_label_values,
):
    @mockserver.json_handler('/rida-mvp/v3/php-status')
    def _mock_google_maps(request):
        return {
            'statuses': [
                {
                    'host': 'rida-mvp',
                    'status': {
                        'pool': 'www',
                        'process_manager': 'static',
                        'start_time': 1629992706,
                        'start_since': 594189,
                        'accepted_conn': 1143821,
                        'listen_queue': 0,
                        'max_listen_queue': 129,
                        'listen_queue_len': 128,
                        'idle_processes': 15,
                        'active_processes': 10,
                        'total_processes': 25,
                        'max_active_processes': 74,
                        'max_children_reached': 0,
                        'slow_requests': 0,
                    },
                },
            ],
        }

    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )

    loop = asyncio.get_event_loop()
    await send_php_status_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(cron_context, {'sensor': 'php_status'})

    assert stats == [
        {
            'value': 1629992706.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'start_time',
            },
        },
        {
            'value': 594189.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'start_since',
            },
        },
        {
            'value': 1143821.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'accepted_conn',
            },
        },
        {
            'value': 0.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'listen_queue',
            },
        },
        {
            'value': 129.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'max_listen_queue',
            },
        },
        {
            'value': 128.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'listen_queue_len',
            },
        },
        {
            'value': 15.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'idle_processes',
            },
        },
        {
            'value': 10.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'active_processes',
            },
        },
        {
            'value': 25.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'total_processes',
            },
        },
        {
            'value': 74.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'max_active_processes',
            },
        },
        {
            'value': 0.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'max_children_reached',
            },
        },
        {
            'value': 0.0,
            'kind': 'DGAUGE',
            'timestamp': 1637406000.0,
            'labels': {
                'sensor': 'php_status',
                'host': 'rida-mvp',
                'param': 'slow_requests',
            },
        },
    ]
