import datetime

from dateutil import parser as date_parser
# pylint: disable=import-error
from processing_plugins import stq_worker_conftest_plugin
import pytest
from tests_processing import util

# pylint: disable=redefined-outer-name
@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.mark.processing_queue_config(
    'handler.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
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
@pytest.mark.parametrize('bad_requests', [2, 3, 4, 5])
async def test_reschedule_policy(
        stq,
        mockserver,
        bad_requests,
        processing,
        statistics,
        taxi_processing,
        use_ydb,
        use_fast_flow,
        ydb,
):
    item_id = '1'
    retries = 4
    iteration = 0

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if iteration < bad_requests:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    queue = processing.testsuite.example
    should_be_good, should_fail = False, False

    async with statistics.capture(taxi_processing) as capture:
        await queue.send_event(item_id, payload={})
        for iteration in range(1, bad_requests + 1):
            if use_ydb:
                ydb_query = """
                    SELECT handling_counters_v2 FROM events
                """
                ydb_cursor = ydb.execute(ydb_query)
                ydb_event = ydb_cursor[0].rows[0]
                assert (
                    ydb_event[0].decode()
                    == '{"default-pipeline.stage-1.reschedule-handler":'
                    + str(iteration)
                    + '}'
                )

            should_be_good = iteration == bad_requests
            should_fail = (iteration == retries) and not should_be_good
            with stq.flushing():
                await queue.call(item_id, expect_fail=should_fail)
                if should_fail or should_be_good:
                    break
                stq['testsuite_example'].next_call()

    assert mock_fallback.times_called == min(bad_requests + 1, retries + 1)
    assert (
        capture.statistics.get(
            'processing.handler.testsuite.example.reschedule-handler.success',
            0,
        )
        == should_be_good
    )
    assert (
        capture.statistics.get(
            'processing.handler.testsuite.example.reschedule-handler.error', 0,
        )
        == should_fail
    )


@pytest.mark.processing_queue_config(
    'ignore_handler.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
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
async def test_reschedule_policy_afterward(
        stq,
        mockserver,
        processing,
        statistics,
        taxi_processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '1'
    retries = 4
    iteration = 0

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        return mockserver.make_response(status=500)

    queue = processing.testsuite.example

    async with statistics.capture(taxi_processing) as capture:
        await queue.send_event(item_id, payload={})
        for iteration in range(1, retries + 1):
            with stq.flushing():
                await queue.call(item_id)
                if iteration < retries:
                    stq['testsuite_example'].next_call()

    assert mock_fallback.times_called == retries + 1
    assert (
        capture.statistics.get(
            'processing.handler.testsuite.example.reschedule-handler.success',
            0,
        )
        == 0
    )
    assert (
        capture.statistics.get(
            'processing.handler.testsuite.example.reschedule-handler.error', 0,
        )
        == 1
    )


# Arslan what to do with abandoned
@pytest.mark.parametrize(
    'calls_expected',
    [
        pytest.param(
            2,
            marks=[
                pytest.mark.pgsql(
                    'processing_db', files=['abandoned-events.sql'],
                ),
                pytest.mark.now('2021-01-01T00:01:00+03'),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.pgsql(
                    'processing_db', files=['event-has-abandoned.sql'],
                ),
                pytest.mark.now('2021-01-01T00:01:00+03'),
            ],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'abandoned_rescheduling.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.config(
    PROCESSING_STARTER={
        'enabled': True,
        'non-handled-threshold': 5000,
        'disabled-delay': 1000,
        'enabled-delay': 3000,
        'chunk-size': 1000,
    },
)
@pytest.mark.config(PROCESSING_SOFT_LIMIT_PENALTY=61)
async def test_reschedule_policy_abandoned(
        taxi_processing, testpoint, calls_expected,
):
    scope = 'testsuite'
    queue = 'example'

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
    )
    assert enqueue_tp.times_called == calls_expected


async def _fetch_events_from_pg(pgsql):
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT reschedule_due ' 'FROM processing.events ORDER BY order_key',
    )
    return [i for i in cursor][0]


async def _fetch_events_from_ydb(ydb):
    db_name = '`events`'
    cursor = ydb.execute(
        'SELECT reschedule_due, order_key FROM {} ORDER BY order_key'.format(
            db_name,
        ),
    )
    return [
        datetime.datetime.fromtimestamp(
            row['reschedule_due'] / 1e6,
            tz=datetime.timezone(datetime.timedelta(hours=3)),
        )
        for row in cursor[0].rows
    ]


TIME = '2021-01-01T00:00:00+03'


@pytest.mark.processing_queue_config(
    'ignore_handler.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.now(TIME)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
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
async def test_reschedule_policy_pg_write(
        mockserver, processing, pgsql, ydb, use_ydb, use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def _mock_fallback(request):
        return mockserver.make_response(status=500)

    queue = processing.testsuite.example

    await queue.send_event(item_id, payload={})
    from_db = []
    if use_ydb:
        from_db = await _fetch_events_from_ydb(ydb)
    else:
        from_db = await _fetch_events_from_pg(pgsql)
    assert from_db[0] == date_parser.parse(TIME) + datetime.timedelta(
        seconds=5,
    )
