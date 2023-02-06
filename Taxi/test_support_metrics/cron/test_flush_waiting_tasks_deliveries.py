import datetime

import pytest

from support_metrics.generated.cron import run_cron


LAST_EVENT_DATETIME = datetime.datetime(
    2021, 10, 2, 16, 17, 56, tzinfo=datetime.timezone.utc,
)
_NOW = (
    LAST_EVENT_DATETIME + datetime.timedelta(days=3, seconds=1)
).isoformat()


async def _run_cron():
    await run_cron.main(
        [
            (
                'support_metrics.crontasks.'
                'flush_chatterbox_waiting_tasks_deliveries'
            ),
            '-t',
            '0',
        ],
    )


async def _query_delivery_ids(db):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_deliveries.waiting_task_deliveries '
        'ORDER BY id',
    )
    return [row['id'] for row in result]


async def _query_task_ids(db):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_tasks.waiting_tasks ORDER BY id',
    )
    return [row['id'] for row in result]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_waiting_tasks_deliveries': {
            'chunk_size': 10000,
            'one_run_limit': 50000,
            'till_days_from_now': 3,
            'enabled': True,
        },
    },
)
async def test_full_flush_in_one_run(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_delivery_ids(db) == []
    assert await _query_task_ids(db) == []


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_waiting_tasks_deliveries': {
            'chunk_size': 2,
            'one_run_limit': 20,
            'till_days_from_now': 4,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_day_limit(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_delivery_ids(db) == [3]
    assert await _query_task_ids(db) == ['task_2', 'task_3', 'task_4']


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_AUTOFLUSH_CONFIG={
        'chatterbox_waiting_tasks_deliveries': {
            'chunk_size': 2,
            'one_run_limit': 2,
            'till_days_from_now': 3,
            'enabled': True,
        },
    },
)
async def test_chunked_flush_with_run_limit(cron_context, monkeypatch):
    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_delivery_ids(db) == [3]
    assert await _query_task_ids(db) == ['task_2', 'task_3', 'task_4']
