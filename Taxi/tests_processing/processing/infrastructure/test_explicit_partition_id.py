# pylint: disable=import-error

from processing_plugins import stq_worker_conftest_plugin
import pytest
from tests_processing import util


@pytest.fixture
def stq_mocked_queues_with_tags():
    return ['testsuite_example']


@pytest.mark.processing_queue_config(
    'explicit_partition_id.yaml',
    scope='testsuite',
    queue='example',
    tag_getter_url=util.UrlMock('/tag-getter'),
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_flow.json')
async def test_explicit_partition_id_do_processing(
        processing, ydb, testpoint, mockserver,
):
    queue = processing.testsuite.example
    item_id = '1234'
    order_ids = [2, 57, 179]
    order_idx = 0

    @testpoint('ProcessingNgQueue::DoProcessingIteration::Tag')
    def process_tp(data):
        assert data['tag'] == str(order_ids[order_idx])

    @testpoint('ProcessingNgQueue::CreateEvent::Tag')
    def create_tp(data):
        assert data['tag'] == str(order_ids[order_idx])

    @mockserver.handler('/tag-getter')
    def tag_handler(request):
        assert request.json['tag'] == str(order_ids[order_idx])
        return mockserver.make_response(status=200)

    for order_id in order_ids:
        order_tag = str(order_id)
        await queue.send_event(
            item_id,
            {'order-key': order_idx, 'partition-id': order_tag},
            tag=order_tag,
        )
        order_idx += 1

    assert process_tp.times_called == 3
    assert create_tp.times_called == 3
    assert tag_handler.times_called == 3


@pytest.mark.processing_queue_config(
    'explicit_partition_id.yaml',
    scope='testsuite',
    queue='example',
    tag_getter_url=util.UrlMock('/tag-getter'),
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.experiments3(filename='ydb_flow.json')
async def test_explicit_partition_id_current_state(
        taxi_processing, processing, ydb, testpoint, mockserver,
):
    queue = processing.testsuite.example
    item_id = '1234'
    order_id = '179'

    @testpoint('ProcessingNgQueue::EvaluateStateManager::Tag')
    def tag_tp(data):
        assert data['tag'] == order_id

    @mockserver.handler('/tag-getter')
    def tag_handler(request):
        assert request.json['tag'] == order_id
        return mockserver.make_response(status=200)

    await queue.send_event(item_id, {'partition-id': order_id}, tag=order_id)
    current_state = await taxi_processing.get(
        '/v1/testsuite/example/current-state', params={'item_id': item_id},
    )
    assert current_state.json()['current-state']['tag'] == order_id
    assert tag_tp.times_called == 1
    assert tag_handler.times_called


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
    'explicit_partition_id.yaml',
    scope='testsuite',
    queue='example',
    tag_getter_url=util.UrlMock('/tag-getter'),
)
@pytest.mark.config(
    PROCESSING_TAGS_PARAMS={'testsuite': {'enabled': True, 'count': 100}},
)
async def test_explcit_partition_id_starter(
        processing, taxi_processing, stq, ydb, testpoint, mockserver,
):
    scope = 'testsuite'
    queue = 'example'
    item_id = '1543'

    ydb.execute(
        """
    INSERT INTO events
    (scope, queue, item_id, idempotency_token, need_start, due)
    VALUES ('{}', '{}', '{}', 'token1', True,
    JUST(TIMESTAMP('2020-12-31T21:00:00.000000Z')))
    """.format(
            scope, queue, item_id,
        ),
    )

    @testpoint('AutomatedProcessingEventsStarter::CountAbandons::Tag')
    def tag_tp(data):
        assert data['tag']

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

    assert tag_tp.times_called
