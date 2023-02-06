import pytest

from taxi.maintenance import run
from taxi.util import dates

from taxi_selfreg.crontasks import collect_metrics


@pytest.mark.config(
    SELFREG_METRICS_SETTINGS={
        'db_metrics': {
            'init_time': '2020-06-01T00:00:00.000Z',
            'read_chunk_size': 50,
            'enabled': True,
        },
    },
)
async def test_metrics_cron(cron_context, loop, get_stats_by_label_values):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    await collect_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'selfreg.db.profiles.committed.total'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'selfreg.db.profiles.committed.total',
                'selfreg_version': 'v1',
            },
            'timestamp': None,
            'value': 1,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'selfreg.db.profiles.committed.total',
                'selfreg_version': 'v2',
            },
            'timestamp': None,
            'value': 1,
        },
    ]
