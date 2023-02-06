import datetime

import pytest

from support_metrics.generated.cron import run_cron


_NOW = datetime.datetime(
    2021, 10, 12, 16, 10, 00, tzinfo=datetime.timezone.utc,
).isoformat()


async def _run_cron():
    await run_cron.main(
        [
            'support_metrics.crontasks.flush_chatterbox_offered_tasks',
            '-t',
            '0',
        ],
    )


async def _query_task_ids(db):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_tasks.offered_tasks ORDER BY id',
    )
    return [row['id'] for row in result]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_offered_tasks': {
            'chunk_size': 10,
            'one_run_limit': 20,
            'till_days_from_now': 1,
            'enabled': True,
        },
    },
)
async def test_full_flush_in_one_run(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_task_ids(db) == []


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_offered_tasks': {
            'chunk_size': 10,
            'one_run_limit': 20,
            'till_days_from_now': 2,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_day_limit(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_task_ids(db) == ['task_1', 'task_2']


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_offered_tasks': {
            'chunk_size': 2,
            'one_run_limit': 2,
            'till_days_from_now': 1,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_run_limit(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_task_ids(db) == [
        'task_1',
        'task_2',
        'task_3',
        'task_4',
        'task_5',
    ]
