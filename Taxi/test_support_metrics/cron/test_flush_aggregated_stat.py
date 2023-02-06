import asyncio
import datetime

import pytest

from taxi.maintenance import run

from support_metrics.crontasks import flush_aggregated_stat_table
from support_metrics.generated.cron import run_cron

LAST_STAT_DATETIME = datetime.datetime(
    2019, 7, 4, 12, 1, 32, tzinfo=datetime.timezone.utc,
)
_NOW = (LAST_STAT_DATETIME + datetime.timedelta(days=5, seconds=1)).isoformat()


async def _run_cron():
    await run_cron.main(
        ['support_metrics.crontasks.flush_aggregated_stat_table', '-t', '0'],
    )


async def _query_events_ids(db):
    result = await db.primary_fetch(
        'SELECT id FROM events.aggregated_stat ORDER BY id',
    )
    return [row['id'] for row in result]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_FLUSH_AGGREGATED_STAT={
        '__default__': {
            'chunk_size': 20000,
            'one_run_limit': 500000,
            'stat_intervals': {
                '1min': {'till_days_from_now': 5},
                '1hour': {'till_days_from_now': 100},
            },
        },
        'aggregated_stat': {'1hour': [{'till_days_from_now': 5}]},
    },
)
async def test_full_stats_flush_in_one_run(cron_context, monkeypatch):

    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == []


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_FLUSH_AGGREGATED_STAT={
        '__default__': {
            'chunk_size': 1,
            'one_run_limit': 1,
            'stat_intervals': {
                '1min': {'till_days_from_now': 7},
                '1hour': {'till_days_from_now': 7},
            },
        },
    },
)
async def test_chunked_flush_with_run_limit(cron_context, monkeypatch):

    await _run_cron()
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == [
        'stat_hour_1',
        'stat_hour_2',
        'stat_min_2',
    ]


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_FLUSH_AGGREGATED_STAT={
        '__default__': {
            'chunk_size': 10,
            'one_run_limit': 10,
            'stat_intervals': {
                '1min': {'till_days_from_now': 1},
                '1hour': {'till_days_from_now': 10},
            },
        },
    },
)
@pytest.mark.parametrize(
    'aggregated_stat_conf, expected_result',
    [
        (
            {
                '1min': [
                    {'till_days_from_now': 1, 'names': ['name_1']},
                    {'till_days_from_now': 15, 'names': ['name_2']},
                ],
                '1hour': [
                    {'till_days_from_now': 3, 'names': ['name_1', 'name_2']},
                ],
            },
            ['stat_min_2'],
        ),
        (
            {
                '1min': [{'till_days_from_now': 10, 'names': ['name_1']}],
                '1hour': [
                    {'till_days_from_now': 3, 'names': ['name_1', 'name_3']},
                ],
            },
            ['stat_hour_2', 'stat_min_1'],
        ),
        (
            {
                '1min': [
                    {'till_days_from_now': 10, 'names': ['name_1']},
                    {'till_days_from_now': 2},
                ],
                '1hour': [{'till_days_from_now': 3}],
            },
            ['stat_min_1'],
        ),
        (
            {
                '1min': [
                    {'till_days_from_now': 2},
                    {'till_days_from_now': 10, 'names': ['name_1']},
                ],
                '1hour': [{'till_days_from_now': 3}],
            },
            ['stat_min_1'],
        ),
        (
            {'1hour': [{'till_days_from_now': 3, 'names': ['name_1']}]},
            ['stat_hour_2'],
        ),
        ({'1hour': [{'till_days_from_now': 3}]}, []),
        ({}, ['stat_hour_1', 'stat_hour_2']),
        (
            {'1min': [{'till_days_from_now': 10}]},
            ['stat_hour_1', 'stat_hour_2', 'stat_min_1', 'stat_min_2'],
        ),
    ],
)
async def test_flush_specific_names(
        cron_context, monkeypatch, aggregated_stat_conf, expected_result,
):
    monkeypatch.setitem(
        cron_context.config.SUPPORT_METRICS_FLUSH_AGGREGATED_STAT,
        'aggregated_stat',
        aggregated_stat_conf,
    )
    context = run.StuffContext(
        lock=None,
        task_id='1',
        start_time=datetime.datetime.utcnow(),
        data=cron_context,
    )
    await flush_aggregated_stat_table.do_stuff(
        task_context=context, loop=asyncio.AbstractEventLoop(),
    )
    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == expected_result


@pytest.mark.now(_NOW)
@pytest.mark.config(
    SUPPORT_METRICS_FLUSH_AGGREGATED_STAT={
        '__default__': {
            'chunk_size': 10,
            'one_run_limit': 10,
            'stat_intervals': {
                '1min': {'till_days_from_now': 1},
                '1hour': {'till_days_from_now': 10},
            },
        },
        'aggregated_stat': {
            '1min': [
                {'till_days_from_now': 2, 'names': ['name_1']},
                {'till_days_from_now': 100, 'names': ['name_1']},
                {'till_days_from_now': 10, 'names': ['name_2']},
            ],
        },
    },
)
async def test_names_duplicate_found(cron_context, monkeypatch):
    with pytest.raises(RuntimeError):
        await _run_cron()

    db = cron_context.postgresql.support_metrics[0]
    assert await _query_events_ids(db) == [
        'stat_hour_1',
        'stat_hour_2',
        'stat_min_2',
    ]
