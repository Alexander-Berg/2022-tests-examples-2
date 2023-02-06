import asyncio

import pytest

from taxi.maintenance import run
from taxi.util import dates

from taxi_takeout.crontasks import send_metrics


@pytest.mark.config(
    TAKEOUT_SERVICES_V2=[{'name': 'a'}, {'name': 'b'}, {'name': 'c'}],
)
@pytest.mark.pgsql('taxi_takeout', files=['test_taxi_takeout.sql'])
async def test_send_metrics(cron_context, get_stats_by_label_values):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    loop = asyncio.get_event_loop()
    await send_metrics.do_stuff(stuff_context, loop)
    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'jobs.count_jobs_in_pending'},
    )
    assert stats == [
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'jobs.count_jobs_in_pending',
                'jobs_service': 'a',
            },
        },
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'jobs.count_jobs_in_pending',
                'jobs_service': 'b',
            },
        },
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'jobs.count_jobs_in_pending',
                'jobs_service': 'c',
            },
        },
    ]
