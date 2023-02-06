import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'queue.yaml',
    scope='testsuite',
    queue='example',
    first_handler_url=util.UrlMock('/first_stage'),
    second_handler_url=util.UrlMock('/second_stage'),
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
async def test_cleanup_processing_state(
        testpoint,
        processing,
        taxi_processing,
        ydb,
        pgsql,
        mockserver,
        use_ydb,
        use_fast_flow,
):
    @testpoint('added_event_to_ydb')
    def added_event_to_ydb(data):
        pass

    @mockserver.json_handler('/stq-agent/queues/api/cleanup')
    def mock_second(request):
        assert request.json['queue_name'] == 'testsuite_example'
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/first_stage')
    def mock_first(request):
        return {}

    @mockserver.json_handler('/second_stage')
    def mock_second(request):
        return mockserver.make_response(status=500)

    event_ydb_name = '`events`'
    event_pg_name = 'processing.events'
    processing_state_ydb_name = '`processing_state`'
    processing_state_pg_name = 'processing_noncritical.processing_state'
    processing_db = 'processing_db'
    processing_noncritical_db = 'processing_noncritical_db'

    item_id = 'foo'
    queue = processing.testsuite.example

    get_pg_rows_count = lambda db, db_name: _get_pg_rows_count(
        pgsql, db, item_id, db_name,
    )
    get_ydb_rows_count = lambda db_name: _get_ydb_rows_count(
        ydb, item_id, db_name,
    )

    event_id = await queue.send_event(item_id, {}, expect_fail=True)

    if use_ydb:
        await added_event_to_ydb.wait_call()

    if use_ydb:
        await get_ydb_rows_count(event_ydb_name) == 1
        await get_ydb_rows_count(processing_state_ydb_name) == 1
    else:
        await get_pg_rows_count(processing_db, event_pg_name) == 1
        await get_pg_rows_count(
            processing_noncritical_db, processing_state_pg_name,
        ) == 1

    result = await taxi_processing.post(f'/tests/v1/cleanup/testsuite/example')
    assert result.status == 200

    if use_ydb:
        await get_ydb_rows_count(event_ydb_name) == 0
        await get_ydb_rows_count(processing_state_ydb_name) == 0
    else:
        await get_pg_rows_count(processing_db, event_pg_name) == 0
        await get_pg_rows_count(
            processing_noncritical_db, processing_state_pg_name,
        ) == 0


async def _get_pg_rows_count(pgsql, db, item_id, db_name):
    cursor = pgsql[db].cursor()
    cursor.execute(
        'SELECT * FROM {} WHERE item_id=%(item_id)s'.format(db_name),
        {'item_id': item_id},
    )

    return len(list(cursor))


async def _get_ydb_rows_count(ydb, item_id, db_name):
    cursor = ydb.execute(
        'SELECT * FROM {} where item_id="{}"'.format(db_name, item_id),
    )

    return len(cursor[0].rows)
