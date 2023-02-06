import datetime

import pytest

from support_metrics.generated.cron import run_cron


LAST_EVENT_DATETIME = datetime.datetime(
    2019, 7, 14, 12, 1, 32, tzinfo=datetime.timezone.utc,
)
_NOW = (
    LAST_EVENT_DATETIME + datetime.timedelta(days=5, seconds=1)
).isoformat()


async def _run_cron():
    await run_cron.main(
        [
            'support_metrics.crontasks.flush_chatterbox_ivr_calls_events',
            '-t',
            '0',
        ],
    )


async def _query_events_ids(db):
    result = await db.primary_fetch(
        'SELECT * FROM events.chatterbox_ivr_calls_events ORDER BY id',
    )
    return [row['id'] for row in result]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_ivr_calls_events': {
            'chunk_size': 10000,
            'one_run_limit': 50000,
            'till_days_from_now': 5,
            'enabled': True,
        },
    },
)
async def test_full_flush_in_one_run(cron_context, monkeypatch):

    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == []


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_ivr_calls_events': {
            'chunk_size': 2,
            'one_run_limit': 20,
            'till_days_from_now': 6,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_day_limit(cron_context, monkeypatch):

    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == ['task_10_calls_count']


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_ivr_calls_events': {
            'chunk_size': 2,
            'one_run_limit': 6,
            'till_days_from_now': 6,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_run_limit(cron_context, monkeypatch):

    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert len(await _query_events_ids(db)) == 4
