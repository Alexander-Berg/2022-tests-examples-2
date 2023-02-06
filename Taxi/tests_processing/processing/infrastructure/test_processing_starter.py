# pylint: disable=import-error

from processing_plugins import stq_worker_conftest_plugin
import pytest


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.now('2021-01-01T00:01:00+03')
@pytest.mark.parametrize(
    'expect_to_abandons',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_STARTER={
                        'enabled': True,
                        'non-handled-threshold': 2000,
                        'disabled-delay': 1000,
                        'enabled-delay': 0,
                        'chunk-size': 1000,
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_STARTER={
                        'enabled': True,
                        'non-handled-threshold': 120000,
                        'disabled-delay': 1000,
                        'enabled-delay': 0,
                        'chunk-size': 1000,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('processing_db', files=['abandoned-events.sql'])
async def test_processing_starter(
        taxi_processing,
        taxi_processing_monitor,
        testpoint,
        expect_to_abandons,
):
    scope = 'testsuite'
    queue = 'foo'

    @testpoint('ProcessingNgQueue::RunAbandons::Enqueue')
    def enqueue_tp(data):
        assert data['scope'] == scope
        assert data['queue'] == queue
        assert data['item_id'] == '0123456789'

    runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'testsuite_starter', taxi_processing,
    )
    await runnable.call(
        task_id=f'procaas_starter_{scope}_{queue}',
        args=[scope, queue],
        kwargs={},
        expect_fail=False,
    )

    if expect_to_abandons:
        assert enqueue_tp.times_called == 1
    else:
        assert enqueue_tp.times_called == 0


@pytest.mark.parametrize(
    'calls_expected',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.pgsql(
                    'processing_db', files=['abandoned-events-underlimit.sql'],
                ),
                pytest.mark.now('2021-01-01T00:01:00+03'),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.pgsql(
                    'processing_db', files=['abandoned-events-overlimit.sql'],
                ),
                pytest.mark.now('2021-01-01T00:01:00+03'),
            ],
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.pgsql(
                    'processing_db', files=['abandoned-events-overlimit.sql'],
                ),
                pytest.mark.now('2021-01-01T00:01:01+03'),
            ],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo-limited.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.config(
    PROCESSING_STARTER={
        'enabled': True,
        'non-handled-threshold': 2000,
        'disabled-delay': 1000,
        'enabled-delay': 0,
        'chunk-size': 1000,
    },
)
@pytest.mark.config(PROCESSING_SOFT_LIMIT_PENALTY=61)
async def test_processing_starter_limited(
        taxi_processing, testpoint, calls_expected,
):
    scope = 'testsuite'
    queue = 'foo'

    @testpoint('ProcessingNgQueue::RunAbandons::Enqueue')
    def enqueue_tp(data):
        pass

    runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'testsuite_starter', taxi_processing,
    )
    await runnable.call(
        task_id=f'procaas_starter_{scope}_{queue}',
        args=[scope, queue],
        kwargs={},
        expect_fail=False,
    )
    assert enqueue_tp.times_called == calls_expected


# Well no annotation for ydb queryies so this.
# Maybe move to separate files and read them at least?
OVERLIMIT_QUERY = """--!syntax_v1
            INSERT INTO `events` (
                scope,
                queue,
                item_id,
                event_id,
                order_key,
                payload_v2,
                idempotency_token,
                need_handle,
                due,
                need_start
            )
            VALUES
            (
                JUST('testsuite'),
                JUST('foo'),
                JUST('0123456789'),
                JUST('abcdef000002'),
                JUST(0),
                CAST('{"kind": "etc"}' AS String?),
                JUST('idempotency_token_0'),
                JUST(TRUE),
                JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
                JUST(TRUE)
            ),
            (
                JUST('testsuite'),
                JUST('foo'),
                JUST('0123456789'),
                JUST('abcdef000003'),
                JUST(1),
                CAST('{"kind": "etc"}' AS String?),
                JUST('idempotency_token_1'),
                JUST(TRUE),
                JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
                JUST(TRUE)
            ),
            (
                JUST('testsuite'),
                JUST('foo'),
                JUST('0123456789'),
                JUST('abcdef000004'),
                JUST(2),
                CAST('{"kind": "etc"}' AS String?),
                JUST('idempotency_token_2'),
                JUST(TRUE),
                JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
                JUST(TRUE)
            );
            """
UNDERLIMIT_QUERY = """--!syntax_v1
            INSERT INTO `events` (
                scope,
                queue,
                item_id,
                event_id,
                order_key,
                payload_v2,
                idempotency_token,
                need_handle,
                due,
                need_start
            )
            VALUES(
                JUST('testsuite'),
                JUST('foo'),
                JUST('0123456789'),
                JUST('abcdef000002'),
                JUST(0),
                CAST('{"kind": "etc"}' AS String?),
                JUST('idempotency_token_2'),
                JUST(TRUE),
                JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')),
                JUST(TRUE)
            );
            """


@pytest.mark.parametrize(
    'calls_expected,query',
    [
        pytest.param(
            0,
            OVERLIMIT_QUERY,
            marks=[pytest.mark.now('2021-01-01T00:01:00+03')],
        ),
        pytest.param(
            1,
            UNDERLIMIT_QUERY,
            marks=[pytest.mark.now('2021-01-01T00:01:00+03')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo-limited.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.config(
    PROCESSING_STARTER={
        'enabled': True,
        'non-handled-threshold': 2000,
        'disabled-delay': 1000,
        'enabled-delay': 0,
        'chunk-size': 1000,
    },
)
@pytest.mark.config(PROCESSING_SOFT_LIMIT_PENALTY=61)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_abandoned.json')
async def test_processing_starter_ydb_parametrization(
        taxi_processing, testpoint, ydb, calls_expected, query, use_fast_flow,
):
    scope = 'testsuite'
    queue = 'foo'

    @testpoint('ProcessingNgQueue::RunAbandons::Enqueue')
    def enqueue_tp(data):
        pass

    ydb.execute(query)
    runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'testsuite_starter', taxi_processing,
    )
    await runnable.call(
        task_id=f'procaas_starter_{scope}_{queue}',
        args=[scope, queue],
        kwargs={},
        expect_fail=False,
    )
    assert enqueue_tp.times_called == calls_expected


@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo-limited.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.config(
    PROCESSING_STARTER={
        'enabled': True,
        'non-handled-threshold': 2000,
        'disabled-delay': 1000,
        'enabled-delay': 0,
        'chunk-size': 1000,
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
        pytest.param(
            marks=[pytest.mark.experiments3(filename='migrate_to_ydb.json')],
        ),
    ],
)
@pytest.mark.experiments3(filename='ydb_abandoned.json')
async def test_processing_starter_ydb_need_start_cleared(
        taxi_processing, testpoint, ydb, use_fast_flow,
):
    scope = 'testsuite'
    queue = 'foo'

    @testpoint('ProcessingNgQueue::RunAbandons::Enqueue')
    def enqueue_tp(data):
        pass

    ydb.execute(UNDERLIMIT_QUERY)
    runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'testsuite_starter', taxi_processing,
    )
    await runnable.call(
        task_id=f'procaas_starter_{scope}_{queue}',
        args=[scope, queue],
        kwargs={},
        expect_fail=False,
    )
    assert enqueue_tp.times_called == 1
    all_started_query = """
        --!syntax_v1
        SELECT event_id FROM `events` WHERE need_start = True
    """
    cursor = ydb.execute(all_started_query)
    assert len(cursor) == 1
    rows = cursor[0].rows
    assert not rows
