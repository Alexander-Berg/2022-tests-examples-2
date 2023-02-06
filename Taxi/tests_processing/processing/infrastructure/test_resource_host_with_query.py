import dataclasses
from typing import List

import pytest

from tests_processing import util


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.processing_queue_config(
                    'handler-template-query-in-url.yaml',
                    scope='testsuite',
                    queue='example',
                    handler_url=util.UrlMock('/stage?foo={foo-value}'),
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.processing_queue_config(
                    'handler-query-in-url.yaml',
                    scope='testsuite',
                    queue='example',
                    handler_url=util.UrlMock('/stage?foo=foo'),
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.processing_queue_config(
                    'handler-no-query-in-url.yaml',
                    scope='testsuite',
                    queue='example',
                    handler_url=util.UrlMock(f'/stage'),
                ),
            ],
        ),
    ],
)
async def test_resource_host_with_query(mockserver, processing):
    item_id = '1'

    @mockserver.json_handler('/stage')
    def mock_resource(request):
        assert request.query.get('foo') == 'foo'
        assert request.query.get('bar') == 'baz'
        return {}

    await processing.testsuite.example.send_event(
        item_id, payload={}, expect_fail=False,
    )

    assert mock_resource.times_called == 1
