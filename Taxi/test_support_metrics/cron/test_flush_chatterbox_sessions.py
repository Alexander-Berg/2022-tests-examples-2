import datetime

import pytest

from support_metrics.generated.cron import run_cron


LAST_EVENT_DATETIME = datetime.datetime(
    2022, 6, 15, 6, 54, tzinfo=datetime.timezone.utc,
)
_NOW = (
    LAST_EVENT_DATETIME + datetime.timedelta(days=3, seconds=1)
).isoformat()


async def _run_cron():
    await run_cron.main(
        ['support_metrics.crontasks.flush_chatterbox_sessions', '-t', '0'],
    )


async def _query_sessions(db):
    result = await db.primary_fetch(
        'SELECT * FROM sessions.chatterbox_sessions '
        'ORDER BY task_id, opened_ts',
    )
    return [(row['task_id'], row['opened_ts']) for row in result]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_sessions': {
            'chunk_size': 10000,
            'one_run_limit': 50000,
            'till_days_from_now': 3,
            'enabled': True,
        },
    },
)
async def test_full_flush_in_one_run(cron_context):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_sessions(db) == []


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_sessions': {
            'chunk_size': 2,
            'one_run_limit': 20,
            'till_days_from_now': 4,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_day_limit(cron_context):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_sessions(db) == [
        (
            'task_3',
            datetime.datetime(
                2022, 6, 15, 6, 54, tzinfo=datetime.timezone.utc,
            ),
        ),
    ]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_sessions': {
            'chunk_size': 2,
            'one_run_limit': 2,
            'till_days_from_now': 3,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_run_limit(cron_context):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_sessions(db) == [
        (
            'task_3',
            datetime.datetime(
                2022, 6, 15, 6, 54, tzinfo=datetime.timezone.utc,
            ),
        ),
    ]
