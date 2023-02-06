import dataclasses
import typing

import bson
import pytest
from tests_processing import util


@pytest.mark.processing_queue_config(
    'queue.yaml',
    scope='testsuite',
    queue='processing',
    bson_handler_url=util.UrlMock('/bson-handler'),
    failed_hanler_url=util.UrlMock('/failed-handler'),
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
        pytest.param(
            True,
            marks=[pytest.mark.experiments3(filename='migrate_to_ydb.json')],
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
async def test_bson_shared_state(
        processing, pgsql, mockserver, use_ydb, use_fast_flow, ydb,
):
    bson_handler_response = {
        'foo': 'bar',
        'bool': False,
        'int': 42,
        'float': 3.1415,
        'foos': ['fooe', 'fooa'],
        'bars': ['barrrr', 'barr'],
        'zero': 0,
    }
    mock_state = {'should_fail': True}

    @mockserver.handler('/bson-handler')
    def bson_handler(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(bson_handler_response),
        )

    @mockserver.json_handler('/failed-handler')
    def failed_handler(request):
        assert request.json['bson-response'] == bson_handler_response
        if mock_state['should_fail']:
            return mockserver.make_response('planned fail', status=500)
        return mockserver.make_response(status=200)

    # send event which should fail (and create checkpoint of shared_state)
    event_id = await processing.testsuite.processing.send_event(
        item_id='0123456789', payload={'reason': 'foo'}, expect_fail=True,
    )
    assert event_id

    # ensure checkpoint created
    @dataclasses.dataclass
    class ProcessingStateRow:
        scope: str
        queue: str
        item_id: str
        pipeline: typing.Optional[str]
        condition_key: typing.Optional[str]
        condition_reason: typing.Optional[str]
        shared_state_bson: bytes
        stage: typing.Optional[str]

    cursor = ydb.execute(
        'SELECT scope, queue, item_id, pipeline, condition_key, '
        'condition_reason, shared_state_bson, stage '
        'FROM processing_state',
    )
    row_list = list(cursor[0].rows[0].values())
    row = ProcessingStateRow(*row_list)

    assert row.scope.decode() == 'testsuite'
    assert row.queue.decode() == 'processing'
    assert row.item_id.decode() == '0123456789'
    assert row.pipeline.decode() == 'default-pipeline'
    assert not row.condition_key
    assert row.condition_reason.decode() == 'foo'
    bson_shared_state = bson.BSON.decode(row.shared_state_bson)
    assert bson_shared_state['bson-response'] == bson_handler_response
    assert row.stage.decode() == 'failed-stage'

    # next call won't fail but will use BSON data restored from checkpoint
    mock_state['should_fail'] = False
    await processing.testsuite.processing.call('0123456789', expect_fail=False)

    # called just once because will be skipped at second run
    assert bson_handler.times_called == 1

    # called every run
    assert failed_handler.times_called == 2
