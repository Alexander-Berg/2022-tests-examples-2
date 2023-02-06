import bson
import pytest

from tests_processing import util


@pytest.mark.processing_queue_config(
    'queue.yaml',
    bson_handler_url=util.UrlMock('/bson-handler'),
    scope='testsuite',
    queue='processing',
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
async def test_bson_handler(processing, mockserver, use_ydb, use_fast_flow):
    bson_handler_response = {'foo': 'bar'}

    @mockserver.handler('/bson-handler')
    def bson_handler(request):
        assert request.content_type == 'application/bson'
        body = bson.BSON.decode(request.get_data())
        assert body == {'test': 'body'}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(bson_handler_response),
        )

    result = await processing.testsuite.processing.handle_single_event(
        'item_id_0', pipeline='default-pipeline', stage_id='default-stage',
    )
    assert bson_handler.times_called == 1
    assert result['bson-response'] == bson_handler_response
