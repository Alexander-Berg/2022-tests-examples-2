import pytest

from taxi.maintenance import run
from taxi.util import dates

from mia.crontasks import collect_db_metrics


@pytest.mark.now('2021-07-29T18:28:21+03:00')
@pytest.mark.pgsql('mia', files=['pg_mia_queries.sql'])
async def test_mia_collect_metrics(
        cron_context, loop, get_stats_by_label_values,
):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    await collect_db_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'db_queries_count'},
    )
    assert stats == [
        {
            'value': 1.0,
            'kind': 'DGAUGE',
            'timestamp': 1627572501.0,
            'labels': {'sensor': 'db_queries_count', 'db_status': 'pending'},
        },
        {
            'value': 2.0,
            'kind': 'DGAUGE',
            'timestamp': 1627572501.0,
            'labels': {
                'sensor': 'db_queries_count',
                'db_status': 'in_progress',
            },
        },
        {
            'value': 3.0,
            'kind': 'DGAUGE',
            'timestamp': 1627572501.0,
            'labels': {
                'sensor': 'db_queries_count',
                'db_status': 'finalizing',
            },
        },
    ]
