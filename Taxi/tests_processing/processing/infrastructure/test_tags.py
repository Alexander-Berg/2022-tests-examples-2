# pylint: disable=import-error
import datetime
import re

from processing_plugins import stq_worker_conftest_plugin
import pytest


@pytest.fixture(autouse=True)
def stq_mocked_queues_with_tags():
    return ['testsuite_example']


@pytest.mark.config(
    PROCESSING_STARTER={
        'enabled': True,
        'non-handled-threshold': 2000,
        'disabled-delay': 1000,
        'enabled-delay': 0,
        'chunk-size': 1000,
    },
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_abandoned.json')
@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.config(
    PROCESSING_TAGS_PARAMS={'testsuite': {'enabled': True, 'count': 100}},
)
async def test_tag_in_starter(processing, taxi_processing, stq, ydb):
    scope = 'testsuite'
    queue = 'example'

    ydb.execute(
        """
    INSERT INTO events
    (scope, queue, item_id, idempotency_token, need_start, due)
    VALUES ('{}', '{}', '1543', 'token1', True,
    JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')))
    """.format(
            scope, queue,
        ),
    )

    stq_runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'tags_testsuite', taxi_processing,
    )
    with stq.flushing():
        await stq_runnable.call(task_id='tags_testsuite', args=[])
        assert stq['tags_testsuite'].times_called == 1

    runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'testsuite_starter', taxi_processing,
    )
    await runnable.call(
        task_id=f'procaas_starter_{scope}_{queue}',
        args=[scope, queue],
        kwargs={},
        expect_fail=False,
    )


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.config(
    PROCESSING_TAGS_PARAMS={'testsuite': {'enabled': True, 'count': 100}},
)
async def test_tags_actualizer(taxi_processing, stq, ydb):
    # cannot use marker, because task is created after reloading config
    await taxi_processing.suspend_periodic_tasks(['tags_reader_testsuite'])

    # will remove data explicitly,
    # because task may be written smth to db before suspending
    ydb.execute('DELETE FROM available_hosts')
    ydb.execute(
        'INSERT INTO available_hosts'
        '(scope, hostname, last_activity_ts, available)'
        'VALUES ("testsuite", "host1", CurrentUtcTimestamp(), true),'
        '("testsuite", "host2", CurrentUtcTimestamp(), true),'
        '("testsuite", "host3", CurrentUtcTimestamp(), false)',
    )
    ydb.execute(
        'INSERT INTO tags_mapping (scope, tag_id, hostname)'
        'VALUES ("testsuite", "tag1", NULL),'
        '("testsuite", "tag2", "host1"),'
        '("testsuite", "tag3", "host3"),'
        '("testsuite", "tag4", NULL)',
    )
    # call STQ worker to do tags actualization
    stq_runnable = stq_worker_conftest_plugin.StqQueueCaller(
        'tags_testsuite', taxi_processing,
    )
    with stq.flushing():
        await stq_runnable.call(task_id='tags_testsuite', args=[])
        assert stq['tags_testsuite'].times_called == 1

    cursor = ydb.execute(
        'SELECT tag_id, hostname FROM tags_mapping ORDER BY tag_id ASC',
    )
    assert len(cursor) == 1
    ydb_rows = cursor[0].rows
    assert ydb_rows[0] == {
        'tag_id': b'tag1',
        'hostname': b'host2',
    }  # because host1 was busy
    assert ydb_rows[1] == {
        'tag_id': b'tag2',
        'hostname': b'host1',
    }  # dont change
    assert ydb_rows[2] == {
        'tag_id': b'tag3',
        'hostname': b'host1',
    }  # goes to next in list
    assert ydb_rows[3] == {
        'tag_id': b'tag4',
        'hostname': b'host2',
    }  # goes to the head of hosts list in cycle


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.config(
    PROCESSING_TAGS_PARAMS={'testsuite': {'enabled': True, 'count': 100}},
)
@pytest.mark.now('2022-01-01T00:01:00+03')
async def test_read_tags(taxi_processing, stq, ydb, now, testpoint):
    @testpoint('stq_dispatcher::set_tags')
    def set_tags_testpoint(request):
        assert request['queue'] == 'testsuite_example'
        assert sorted(request['tags']) == ['t1', 't3']

    # note stq job will not run in test,
    # because it only runs when called explicitly
    ydb.execute(
        'INSERT INTO tags_mapping(scope, tag_id, hostname)'
        'VALUES ("x", "x1", "host55"),'
        '("testsuite", "t1", "host55"),'
        '("testsuite", "t2", "host1"),'
        '("testsuite", "t3", "host55")',
    )
    await taxi_processing.run_periodic_task('tags_reader_testsuite')
    cursor = ydb.execute(
        'SELECT * FROM available_hosts ' 'WHERE hostname = "host55"',
    )
    assert cursor[0].rows[0] == {
        'hostname': b'host55',
        'available': True,
        'last_activity_ts': (
            now - datetime.datetime(1970, 1, 1)
        ).total_seconds() * 1000_000,
        'scope': b'testsuite',
    }
    assert set_tags_testpoint.times_called == 1


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'tag,tags_count,expected_source_id',
    [
        pytest.param(
            None,
            None,
            r'^[\.\w_-]+:src-events:0$',
            marks=[],
            id='no config set',
        ),
        pytest.param(
            None,
            None,
            r'^[\.\w_-]+:src-events:0$',
            marks=[
                pytest.mark.config(
                    PROCESSING_TAGS_PARAMS={
                        'testsuite': {'enabled': False, 'count': 100},
                    },
                ),
            ],
            id='disabled',
        ),
        pytest.param(
            # if this test will fail, because hashing algorithm changes,
            # it IS a problem
            'v001/testsuite/36',
            100,
            r'^src-events/v001/testsuite/36$',
            marks=[
                pytest.mark.config(
                    PROCESSING_TAGS_PARAMS={
                        'testsuite': {'enabled': True, 'count': 100},
                    },
                ),
            ],
            id='100-tags',
        ),
        pytest.param(
            'v001/testsuite/6',
            10,
            r'^src-events/v001/testsuite/6$',
            marks=[
                pytest.mark.config(
                    PROCESSING_TAGS_PARAMS={
                        'testsuite': {'enabled': True, 'count': 10},
                    },
                ),
            ],
            id='10-tags',
        ),
    ],
)
async def test_send_tag(
        processing,
        tag,
        tags_count,
        testpoint,
        ydb,
        taxi_processing,
        expected_source_id,
):
    if tags_count is not None:
        values = [
            '("testsuite", "v001/testsuite/{}", "host55")'.format(tag_id)
            for tag_id in range(tags_count)
        ]
        request = (
            'INSERT INTO tags_mapping(scope, tag_id, hostname)'
            'VALUES {}'.format(','.join(values))
        )
        ydb.execute(request)
    await taxi_processing.run_periodic_task('tags_reader_testsuite')

    # todo check stq calls instead of tespoint
    @testpoint('tags-actualizer::calc_tag_for_item')
    def tag_for_item_tp(data):
        assert data == tag

    expected_source_id = re.compile(expected_source_id)

    @testpoint('logbroker_publish')
    def logbroker_tp(data):
        assert expected_source_id.match(data['source_id']), data['source_id']

    await processing.testsuite.example.send_event('1234', payload={}, tag=tag)
    if tag is None:
        assert tag_for_item_tp.times_called == 0
    else:
        assert tag_for_item_tp.times_called == 1

    events = await processing.testsuite.example.events('1234')
    assert len(events) == 1

    if tag is None:
        assert tag_for_item_tp.times_called == 0
    else:
        assert tag_for_item_tp.times_called == 1

    assert logbroker_tp.times_called == 1
