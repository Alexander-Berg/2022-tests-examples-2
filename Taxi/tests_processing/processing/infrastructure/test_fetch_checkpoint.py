import json

import bson
import pytest
from tests_processing import util


@pytest.mark.processing_queue_config(
    'queue_tp.yaml',
    bad_handler_url=util.UrlMock('/bad-handle'),
    good_handler_url=util.UrlMock('/good-handle'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.config(PROCESSING_CHECKPOINT_LIMIT={'testsuite': 1})
async def test_checkpoint_serializer_bug(
        processing, testpoint, ydb, stq, mockserver,
):
    item_id = 'foo'
    queue = processing.testsuite.example

    @mockserver.json_handler('/bad-handle')
    def bad_mock(request):
        return mockserver.make_response('internal error', status=500)

    @mockserver.json_handler('/good-handle')
    def good_mock(request):
        return mockserver.make_response('success', status=200)

    await queue.send_event(item_id, {'kind': 'create'}, expect_fail=True)
    # actually i don't care, but for linter's sake
    assert bad_mock.times_called
    assert good_mock.times_called

    for _ in range(4):
        cursor = ydb.execute(
            'SELECT handlers_result_bson, finished_handlers '
            'FROM processing_state',
        )
        finished_handlers = cursor[0].rows[0]['finished_handlers']
        assert finished_handlers == b'["handle-to-succeed"]'
        handlers_result = bson.BSON.decode(
            cursor[0].rows[0]['handlers_result_bson'],
        )
        # shared state is serialized by same logic so no need to check
        assert handlers_result == {'request-b': True}
        with stq.flushing():
            await queue.call(item_id, expect_fail=True)


@pytest.mark.processing_queue_config(
    'queue.yaml',
    scope='testsuite',
    queue='example',
    success_handler_url=util.UrlMock('/success-handler'),
    failure_handler_url=util.UrlMock('/failure-handler'),
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
async def test_checkpoint_get(
        processing, taxi_processing, mockserver, use_ydb, use_fast_flow,
):
    item_id = '1234512345'
    queue = processing.testsuite.example
    success_handler_response = {'success': True}
    mock_state = {'should_fail': True}

    @mockserver.handler('/success-handler')
    def success_handler(request):
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            response=json.dumps(success_handler_response),
        )

    @mockserver.handler('/failure-handler')
    def failed_handler(request):
        if mock_state['should_fail']:
            return mockserver.make_response('planned fail', status=500)
        return mockserver.make_response(status=200)

    async def get_checkpoint():
        get_params = {'item_id': item_id}
        return await taxi_processing.get(
            '/v1/testsuite/example/checkpoint', params=get_params,
        )

    # No events were emited, no pipeline
    resp = await get_checkpoint()
    assert resp.status_code == 404

    # Failure pipeline, should contains checkpoint
    event_id = await queue.send_event(
        item_id=item_id, payload={'key': 'handle-default'}, expect_fail=True,
    )
    assert event_id

    resp = await get_checkpoint()
    assert resp.status_code == 200

    checkpoint = resp.json()
    assert checkpoint['event_id'] == event_id
    assert checkpoint['condition_key'] == 'handle-default'
    assert 'condition_reason' not in checkpoint
    assert checkpoint['pipeline'] == 'default-pipeline'
    assert checkpoint['stage'] == 'failure-stage'
    assert (
        checkpoint['shared_state']['success-response']
        == success_handler_response
    )

    # Success pipeline, no checkpoints
    mock_state['should_fail'] = False

    event_id = await queue.send_event(
        item_id=item_id, payload={'key': 'handle-default'}, expect_fail=False,
    )
    assert event_id

    resp = await get_checkpoint()
    assert resp.status_code == 404

    assert success_handler.times_called == 2
    assert failed_handler.times_called == 3
