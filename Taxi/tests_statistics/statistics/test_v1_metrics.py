import datetime

import pytest
import pytz


_NOW = datetime.datetime(2019, 8, 2, 11, 52, 37, 12325)
_DEFAULT_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:51+0000', 'cardstorage', 'card.lpm.success', 300),
('2019-8-2 11:52+0000', 'cardstorage', 'card.lpm.success', 120),
('2019-8-2 11:52+0000', 'some-other', 'metric', 60)
"""

_VERY_OLD_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:40+0000', 'cardstorage', 'card.lpm.success', 999)
"""


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_DEFAULT_STATS, _VERY_OLD_STATS])
async def test_metrics_store(taxi_statistics, now, pgsql):
    now_bucket = now.replace(second=0, microsecond=0)
    metrics = [
        {'name': 'card.lpm.success', 'value': 70},
        {'name': 'card.lpm.error', 'value': 13},
    ]
    response = await taxi_statistics.post(
        'v1/metrics/store',
        json={
            'service': 'cardstorage',
            'time_bucket': f'{now_bucket.isoformat()}Z',
            'metrics': metrics,
        },
    )
    assert response.status_code == 200, response.content
    await taxi_statistics.invalidate_caches()
    cursor = pgsql['statistics'].cursor()
    cursor.execute(
        """
        SELECT time_bucket, service, metric_name, SUM(count)
        FROM statistics.metrics
        GROUP BY time_bucket, service, metric_name
        ORDER BY time_bucket, service, metric_name
        """,
    )
    prev_bukcet = now_bucket - datetime.timedelta(minutes=1)
    expected_stored = [
        (prev_bukcet, 'cardstorage', 'card.lpm.success', 300),
        (now_bucket, 'cardstorage', 'card.lpm.error', 13),
        (now_bucket, 'cardstorage', 'card.lpm.success', 120 + 70),
        (now_bucket, 'some-other', 'metric', 60),
    ]
    result = [
        (
            time_bucket.astimezone(pytz.UTC).replace(tzinfo=None),
            service,
            metric_name,
            count,
        )
        for time_bucket, service, metric_name, count in cursor
    ]
    assert expected_stored == result


@pytest.mark.parametrize(
    'service, timestamp, interval, expected_code, expected_metrics',
    [
        ('cardstorage', _NOW, 121, 200, {'card.lpm.success': 420}),
        (
            'cardstorage',
            _NOW - datetime.timedelta(minutes=1),
            60,
            200,
            {'card.lpm.success': 300},
        ),
        ('cardstorage', _NOW, 59, 200, {'card.lpm.success': 120}),
        ('cardstorage', _NOW, 601, 410, None),
        ('cardstorage', _NOW - datetime.timedelta(minutes=1), 541, 410, None),
        ('some-other', _NOW, 599, 200, {'metric': 60}),
        ('not-in-db', _NOW, 599, 200, {}),
    ],
)
@pytest.mark.pgsql('statistics', queries=[_DEFAULT_STATS])
@pytest.mark.now(_NOW.isoformat())
async def test_metrics_list(
        taxi_statistics,
        service,
        timestamp,
        interval,
        expected_code,
        expected_metrics,
):
    response = await taxi_statistics.post(
        'v1/metrics/list',
        json={
            'service': service,
            'timestamp': f'{timestamp.isoformat()}Z',
            'interval': interval,
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response = response.json()
        metrics = {
            metric['name']: metric['value'] for metric in response['metrics']
        }
        assert metrics == expected_metrics


@pytest.mark.parametrize(
    'metric_names, expected_metrics',
    [
        (None, {'card.lpm.success', 'card.lpm.error'}),
        (
            ['card.lpm.success', 'card.lpm.error'],
            {'card.lpm.success', 'card.lpm.error'},
        ),
        (['card.lpm.success'], {'card.lpm.success'}),
        (['card.lpm.limited'], set()),
        ([], set()),
    ],
)
@pytest.mark.pgsql(
    'statistics',
    queries=[
        """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52+0000', 'cardstorage', 'card.lpm.success', 120),
('2019-8-2 11:52+0000', 'cardstorage', 'card.lpm.error', 3)
""",
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_metrics_names(
        taxi_statistics, now, metric_names, expected_metrics,
):
    request = {
        'service': 'cardstorage',
        'timestamp': f'{now.isoformat()}Z',
        'interval': 100,
    }
    if metric_names is not None:
        request['metric_names'] = metric_names
    response = await taxi_statistics.post('v1/metrics/list', json=request)
    assert response.status_code == 200
    response = response.json()
    got_names = {metric['name'] for metric in response['metrics']}
    assert got_names == expected_metrics


@pytest.mark.parametrize('sync_before_read', [True, False])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_DEFAULT_STATS])
async def test_store_list(taxi_statistics, now, sync_before_read):
    now_bucket = now.replace(second=0, microsecond=0)
    metrics = [
        {'name': 'card.lpm.success', 'value': 70},
        {'name': 'card.lpm.error', 'value': 13},
    ]
    response = await taxi_statistics.post(
        'v1/metrics/store',
        json={
            'service': 'cardstorage',
            'time_bucket': f'{now_bucket.isoformat()}Z',
            'metrics': metrics,
        },
    )
    assert response.status_code == 200, response.content
    if sync_before_read:
        await taxi_statistics.invalidate_caches()

    response = await taxi_statistics.post(
        'v1/metrics/list',
        json={
            'service': 'cardstorage',
            'timestamp': f'{now.isoformat()}Z',
            'interval': 100,
        },
    )
    assert response.status_code == 200
    response = response.json()
    metrics = {
        metric['name']: metric['value'] for metric in response['metrics']
    }
    assert metrics == {'card.lpm.success': 420 + 70, 'card.lpm.error': 13}


@pytest.mark.now(datetime.datetime(2019, 8, 3, 11, 52, 37, 12325).isoformat())
async def test_repeative_store_2(taxi_statistics, pgsql, now):
    await _send(now, taxi_statistics, 0)
    await _send(now, taxi_statistics, 1)
    await _send(now, taxi_statistics, 0)
    await taxi_statistics.invalidate_caches()
    cursor = pgsql['statistics'].cursor()
    cursor.execute('SELECT SUM(count) FROM statistics.metrics')
    assert next(cursor)[0] == 150


def _make_stats(
        queued=0, written=0, retries=0, fails=0, cancelled=0, expired=0,
):
    return dict(
        queued=queued,
        written=written,
        retries=retries,
        fails=fails,
        cancelled=cancelled,
        expired=expired,
    )


def _make_ok_chunk_stats(chunks=0, atoms=0, records=0):
    return {
        'chunks': _make_stats(queued=chunks, written=chunks),
        'atoms': _make_stats(queued=atoms, written=atoms),
        'records': _make_stats(queued=records, written=records),
    }


EXTRA_WRITE_STATS = ['periodic_writer_task_runs', 'chunk_size', 'atom_lags']


def _chunk_config(chunk_size=1, retries=1, log_atom_size_threshold=None):
    value = {
        'enabled': True,
        'shuffling': False,
        'max_chunk_size': chunk_size,
        'write_retries': retries,
        'write_workers': 1,
    }
    if log_atom_size_threshold:
        value['log_atom_size_threshold'] = log_atom_size_threshold
    return pytest.mark.config(STATISTICS_WRITE_METRICS_CHUNKING=value)


@pytest.mark.parametrize(
    'write_stats,chunk_1_action,worker_called',
    [
        pytest.param(
            _make_ok_chunk_stats(chunks=3, atoms=3, records=6),
            None,
            3,
            marks=[
                _chunk_config(
                    chunk_size=1, retries=1, log_atom_size_threshold=1,
                ),
            ],
            id='small_chunk ok',
        ),
        pytest.param(
            _make_ok_chunk_stats(chunks=1, atoms=3, records=6),
            None,
            1,
            marks=[_chunk_config(chunk_size=10, retries=1)],
            id='medium_chunk ok',
        ),
        pytest.param(
            {
                'chunks': _make_stats(queued=4, written=3, retries=1, fails=1),
                'atoms': _make_stats(queued=4, written=3, retries=1, fails=1),
                'records': _make_stats(
                    queued=8, written=6, retries=2, fails=2,
                ),
            },
            'lock_timeout',
            3 + 1 + 1,
            marks=[_chunk_config(chunk_size=1, retries=1)],
            id='small_chunk with lock timeout',
        ),
        pytest.param(
            {
                'chunks': _make_stats(queued=4, written=3, fails=1),
                'atoms': _make_stats(queued=4, written=3, fails=1),
                'records': _make_stats(queued=8, written=6, fails=2),
            },
            'runtime_error',
            3 + 1,
            marks=[_chunk_config(chunk_size=1, retries=1)],
            id='small_chunk with runtime_error',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('WritingTask')
async def test_chunking_write(
        taxi_statistics,
        now,
        testpoint,
        write_stats,
        chunk_1_action,
        worker_called,
):
    @testpoint('metric_writer_start')
    def writer_start_tp(data):
        if not writer_start_tp.cleaned:
            writer_start_tp.cleaned = True
            return {'reset_stats': True}
        return None

    writer_start_tp.cleaned = False

    @testpoint('metric_writer_end')
    def writer_end_tp(data):
        writer_end_tp.stats = data

    writer_end_tp.stats = {}

    @testpoint('metric_writer_worker')
    def worker_tp(data):
        if chunk_1_action and data['chunk_id'] == 1:
            return {'action': chunk_1_action}
        return None

    await _store(now, taxi_statistics, 'svc1', {'success': 10, 'error': 4}, 0)
    await _store(now, taxi_statistics, 'svc1', {'success': 9, 'error': 5}, 1)
    await _store(now, taxi_statistics, 'svc2', {'success': 20, 'error': 1}, 0)
    await _store(now, taxi_statistics, 'svc2', {'success': 30, 'error': 1}, 0)

    await taxi_statistics.run_periodic_task('WritingTask')
    if chunk_1_action:
        await taxi_statistics.run_periodic_task('WritingTask')
    await writer_end_tp.wait_call()
    stats = writer_end_tp.stats

    for extra in EXTRA_WRITE_STATS:
        stats.pop(extra)
    assert stats == write_stats
    assert worker_tp.times_called == worker_called


@pytest.mark.pgsql(
    'statistics',
    queries=[
        """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:00+0000', 'cardstorage', 'card.lpm.success', 50)
""",
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_repeative_store(taxi_statistics, pgsql, now):
    expected = 50
    await _validate(taxi_statistics, expected, pgsql, now)
    for second in range(30):
        await _send(now, taxi_statistics, second)
        expected += 50
        await _validate(taxi_statistics, expected, pgsql, now)
    print('first iteration finished at', expected)
    await taxi_statistics.invalidate_caches()
    await _validate(taxi_statistics, expected, pgsql, now)
    for second in range(50):
        await _send(now, taxi_statistics, second % _NOW.second)
        expected += 50
        await _validate(taxi_statistics, expected, pgsql, now)
    print('second iteration finished at', expected)
    await taxi_statistics.invalidate_caches()
    await _validate(taxi_statistics, expected, pgsql, now)


@pytest.mark.now(_NOW.isoformat())
async def test_same_second(taxi_statistics, now, pgsql):
    await _send(now, taxi_statistics, second=0, microsecond=0)
    await _send(now, taxi_statistics, second=0, microsecond=1)
    await taxi_statistics.invalidate_caches()
    await _validate(
        taxi_statistics, expected=100, pgsql=pgsql, now=now, retry=False,
    )
    cursor = pgsql['statistics'].cursor()
    cursor.execute('SELECT COUNT(1) FROM statistics.metrics')
    assert next(cursor)[0] == 1


async def _validate(taxi_statistics, expected, pgsql, now, retry=True):
    response = await taxi_statistics.post(
        'v1/metrics/list',
        json={
            'service': 'cardstorage',
            'timestamp': f'{now.isoformat()}Z',
            'interval': 100,
        },
    )
    assert response.status_code == 200
    response = response.json()
    metrics = [{'name': 'card.lpm.success', 'value': expected}]
    if not retry:
        cursor = pgsql['statistics'].cursor()
        cursor.execute('SELECT SUM(count) FROM statistics.metrics')
        assert next(cursor)[0] == expected
        assert response['metrics'] == metrics

    if response['metrics'] != metrics:
        await taxi_statistics.invalidate_caches()
        await _validate(taxi_statistics, expected, pgsql, now, retry=False)


async def _send(now, taxi_statistics, second, microsecond=0):
    now_bucket = now.replace(second=second, microsecond=microsecond)
    metrics = [{'name': 'card.lpm.success', 'value': 50}]
    request = {
        'service': 'cardstorage',
        'time_bucket': f'{now_bucket.isoformat()}Z',
        'metrics': metrics,
    }
    response = await taxi_statistics.post('v1/metrics/store', json=request)
    assert response.status_code == 200


async def _store(now, taxi_statistics, service, metrics, second):
    now_bucket = now.replace(second=second, microsecond=0)
    request = {
        'service': service,
        'time_bucket': f'{now_bucket.isoformat()}Z',
        'metrics': [{'name': k, 'value': v} for k, v in metrics.items()],
    }
    response = await taxi_statistics.post('v1/metrics/store', json=request)
    assert response.status_code == 200


_STATS_FOR_INCREASED_TIMEOUT = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name,
                                count, updated)
VALUES
('2022-3-30 12:00:00+0000', 's1', 'test1', 300, '2022-3-30 12:00:01+0000'),
('2022-3-30 12:00:01+0000', 's1', 'test1', 120, '2022-3-30 12:00:01+0000'),
('2019-3-30 12:00:00+0000', 's2', 'test2', 60, '2022-3-30 12:00:01+0000')
"""


@pytest.mark.now(datetime.datetime(2022, 3, 30, 12, 0, 1).isoformat())
@pytest.mark.config(STATISTICS_PG_READ_DELAY_FOR_TIMEOUT_INCREASE=120)
@pytest.mark.pgsql('statistics', queries=[_STATS_FOR_INCREASED_TIMEOUT])
async def test_increased_pg_timeout(
        taxi_statistics, mocked_time, taxi_statistics_monitor,
):
    async def get_stats(taxi_statistics_monitor):
        await taxi_statistics.run_periodic_task('ReadingTask')
        metrics = await taxi_statistics_monitor.get_metric('metrics')
        return metrics['pg-counter-common-stats']

    stats = await get_stats(taxi_statistics_monitor)
    # increased timeout on service start, it's ok
    assert stats['increased_pg_read_timeout'] == 1
    assert stats['is_startup'] == 1

    mocked_time.sleep(60)

    stats = await get_stats(taxi_statistics_monitor)
    # not enough time passed to fire alert again
    assert stats['increased_pg_read_timeout'] == 0
    # passed startup state, so metric doesn't change
    assert stats['is_startup'] == 0

    mocked_time.sleep(60)

    # no fresh metrics, lag from last successfull reading is big now
    stats = await get_stats(taxi_statistics_monitor)
    assert stats['increased_pg_read_timeout'] == 1
    assert stats['is_startup'] == 0


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[])
async def test_metrics_store_with_control_symbols(taxi_statistics, now, pgsql):
    now_bucket = now.replace(second=0, microsecond=0)
    metrics = [
        {'name': 'card.lpm.\tsuccess', 'value': 70},
        {'name': 'card.\nlpm.error', 'value': 70},
    ]
    response = await taxi_statistics.post(
        'v1/metrics/store',
        json={
            'service': 'cardstorage',
            'time_bucket': f'{now_bucket.isoformat()}Z',
            'metrics': metrics,
        },
    )
    assert response.status_code == 200, response.content
    await taxi_statistics.invalidate_caches()
    cursor = pgsql['statistics'].cursor()
    cursor.execute(
        """
        SELECT metric_name
        FROM statistics.metrics
        """,
    )
    result = [metric_name for metric_name in cursor]
    assert [('card.lpm.error',), ('card.lpm.success',)] == result
