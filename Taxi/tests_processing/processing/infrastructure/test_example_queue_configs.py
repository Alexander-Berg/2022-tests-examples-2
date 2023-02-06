import dataclasses
import datetime
import typing

import bson
import pytest
from tests_processing import util


@pytest.mark.processing_queue_config(
    'testsuite-example.yaml',
    scope='testsuite',
    queue='example',
    deadline_fallback_resource_url=util.UrlMock('/fallback'),
    example_resource_a=util.UrlMock('/resource-a'),
    example_resource_b=util.UrlMock('/resource-b'),
)
@pytest.mark.parametrize('deadline_fallback_activate', [False, True])
@pytest.mark.experiments3(filename='exp-pipeline-level.json')
@pytest.mark.experiments3(filename='exp-stage-level.json')
@pytest.mark.experiments3(filename='exp-handler-level.json')
@pytest.mark.experiments3(filename='exp-queue-level.json')
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
async def test_example_queue(
        stq,
        mockserver,
        testpoint,
        deadline_fallback_activate,
        mocked_time,
        processing,
        use_ydb,
        use_fast_flow,
):
    item_id = '123456789'

    @testpoint('handle-default')
    async def tp_handle_default(data):
        pass

    @mockserver.json_handler('/resource-a')
    async def mock_resource_a(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {'foo': 'bar'}

    @mockserver.json_handler('/resource-b')
    async def mock_resource_b(request):
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json == {
            'shared-state': {
                'foo': 'bar',
                'example-key': 'example-value',
                'pipeline-exp': True,
                'stage-exp': True,
                'handler-exp': True,
                'queue-exp': True,
                'deadline-handler-result': {
                    'result': (
                        'fallback' if deadline_fallback_activate else 'ok'
                    ),
                },
            },
        }
        return {}

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        if deadline_fallback_activate:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    await processing.testsuite.example.send_event(
        item_id, payload={'kind': 'create'},
    )

    # for state-1
    event_id = await processing.testsuite.example.send_event(
        item_id,
        payload={'kind': 'regular'},
        expect_fail=deadline_fallback_activate,
    )
    assert tp_handle_default.times_called == 1
    tp_data = (await tp_handle_default.wait_call(timeout=2.0))['data']
    assert event_id == tp_data['event']['event_id']
    assert mock_resource_a.times_called == 1

    if deadline_fallback_activate:
        mocked_time.sleep(10000)
        await processing.testsuite.example.call(item_id, expect_fail=False)

    assert mock_resource_b.times_called == 1
    if deadline_fallback_activate:
        assert mock_fallback.times_called == 2
    else:
        assert mock_fallback.times_called == 1

    eta = mocked_time.now() + datetime.timedelta(minutes=5)
    await processing.testsuite.example.send_event(
        item_id, payload={'kind': 'regular'}, eta=eta,
    )
    assert mock_resource_b.times_called == 1

    # ensure item_id is finished
    await processing.testsuite.example.send_event(
        item_id, payload={'kind': 'finish'},
    )

    # check that processing will reschedule if some future event exists
    with stq.flushing():
        # call STQ worker to do processing iteration
        await processing.testsuite.example.call(item_id)
        assert stq['testsuite_example'].times_called == 1
        call = stq['testsuite_example'].next_call()
        assert call['id'] == f'testsuite_example_{item_id}'
        assert call['eta'] >= eta

    # execute future event
    mocked_time.sleep(301)
    with stq.flushing():
        await processing.testsuite.example.call(item_id)
        assert mock_resource_b.times_called == 2
        assert stq['testsuite_example'].times_called == 1


@pytest.mark.processing_queue_config(
    'testsuite-example.yaml',
    scope='testsuite',
    queue='example',
    deadline_fallback_resource_url=util.UrlMock('/fallback'),
    example_resource_a=util.UrlMock('/resource-a'),
    example_resource_b=util.UrlMock('/resource-b'),
)
@pytest.mark.parametrize(
    'enable_checkpoints',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_CHECKPOINTS={
                        'default': True,
                        'overrides': [],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_CHECKPOINTS={
                        'default': False,
                        'overrides': [],
                    },
                ),
            ],
        ),
    ],
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
async def test_failed_handler(
        processing,
        mockserver,
        pgsql,
        ydb,
        testpoint,
        enable_checkpoints,
        use_ydb,
        use_fast_flow,
):
    item_id = '1234567890'

    @testpoint('handle-default')
    async def _tp_handle_default(data):
        pass

    @mockserver.json_handler('/resource-a')
    async def _mock_resource_a(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {}  # this answer will cause fail in handler 'bar'

    @mockserver.json_handler('/fallback')
    def _mock_fallback(request):
        return {'result': 'ok'}

    # create item
    await processing.testsuite.example.send_event(item_id, {'kind': 'create'})

    # for state-1
    await processing.testsuite.example.send_event(
        item_id, {'kind': 'regular'}, expect_fail=True,
    )

    @dataclasses.dataclass
    class ProcessingStateRow:
        scope: str
        queue: str
        item_id: str
        pipeline: typing.Optional[str]
        condition_key: typing.Optional[str]
        condition_reason: typing.Optional[str]
        shared_state: str
        shared_state_bson: dict
        stage: typing.Optional[str]
        finshed_handlers: list
        handlers_result: str
        handlers_result_bson: bytes

    # ensure processing state saved
    cursor = ydb.execute(
        'SELECT scope, queue, item_id, pipeline, '
        'condition_key, condition_reason, NULL AS shared_state, '
        'shared_state_bson, stage, finished_handlers, '
        'NULL AS handlers_result, handlers_result_bson '
        'FROM processing_state',
    )
    row_list = list(cursor[0].rows[0].values())
    row = ProcessingStateRow(*row_list)

    assert row.scope.decode() == 'testsuite'
    assert row.queue.decode() == 'example'
    assert row.item_id.decode() == item_id
    assert row.pipeline.decode() == 'default-pipeline'
    assert row.condition_key.decode() == 'handle-by-default'
    assert not row.condition_reason
    assert not row.shared_state
    assert row.stage.decode() == 'stage-2'
    assert row.shared_state_bson == bson.BSON.encode(
        {'example-key': 'example-value'},
    )
    assert row.finshed_handlers == b'["deadline-fallback"]'
    assert bson.BSON.decode(row.handlers_result_bson) == {
        'deadline-handler-result': {'result': 'ok'},
    }


@pytest.mark.processing_queue_config(
    'testsuite-example.yaml',
    scope='testsuite',
    queue='example',
    deadline_fallback_resource_url=util.UrlMock('/fallback'),
    example_resource_a=util.UrlMock('/resource-a'),
    example_resource_b=util.UrlMock('/resource-b'),
)
@pytest.mark.parametrize(
    'pipeline, curr_state_state',
    [(None, 'state-7'), ('pipeline-7', 'state-9')],
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
async def test_handle_single_event(
        processing,
        pipeline,
        curr_state_state,
        testpoint,
        use_ydb,
        use_fast_flow,
):
    @testpoint('point-7')
    def point_7(request):
        pass

    result = await processing.testsuite.example.handle_single_event(
        'item_id_1',
        prev_state={'state': None},
        curr_state={'state': curr_state_state},
        payload={'kind': 'regular'},
        pipeline=pipeline,
    )
    assert point_7.times_called == 1
    assert result == {'state': curr_state_state, 'prev_state': None}
