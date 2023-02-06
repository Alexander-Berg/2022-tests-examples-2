import bson
import pytest

from taxi import config
from taxi.core import async
from taxi.core import arequests
from taxi.external import order_core


@pytest.inline_callbacks
@pytest.mark.parametrize(
    'attempts, actual_attempts, response_code, expected_error',
    [
        (3, 1, 200, None),
        (3, 3, 500, order_core.CommunicationError),
        (3, 1, 400, order_core.CommunicationError),
        (3, 1, 499, order_core.CommunicationError),
        (3, 1, 404, order_core.CommunicationError),
        (3, 1, 409, order_core.EventRequestFailed),
        (1, 1, 500, order_core.CommunicationError),
        (3, 2, [500, 200], None),
    ])
def test_send_request(
        attempts, actual_attempts, response_code, expected_error, patch):
    yield config.ORDER_CORE_CLIENT_QOS.save({
        '__default__': {
            'attempts': 6,
            'timeout-ms': 3000,
        },
        'post-event': {
            'attempts': attempts,
            'timeout-ms': 300,
        }
    })

    if isinstance(response_code, int):
        response_codes_iter = iter([response_code] * actual_attempts)
    else:
        response_codes_iter = iter(response_code)

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def mock_post_event(url, timeout=None, *args, **kwargs):
        assert timeout == 0.3
        curr_code = next(response_codes_iter)
        yield
        content = ''
        headers = {}
        if curr_code == 200:
            content = bson.BSON.encode({})
            headers['Content-Type'] = 'application/bson'
        async.return_value(arequests.Response(
            status_code=curr_code, content=content, headers=headers))

    if expected_error is None:
        response = yield order_core._send_bson_request(
            'localhost/internal/processing/v1/event/foo', {}, {}, {}, 'post-event')
        assert response == {}
    else:
        with pytest.raises(expected_error):
            yield order_core._send_bson_request(
                'localhost/internal/processing/v1/event/foo', {}, {}, {}, 'post-event')
    assert len(mock_post_event.calls) == actual_attempts


@pytest.inline_callbacks
@pytest.mark.parametrize('attempts,called,expected_error', [
    (1, 1, None),
    (0, 0, RuntimeError)
])
def test_wrong_config(attempts, called, expected_error, patch):
    yield config.ORDER_CORE_CLIENT_QOS.save({
        '__default__': {
            'attempts': attempts,
            'timeout-ms': 3000,
        }
    })

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def mock_post_event(url, timeout=None, *args, **kwargs):
        yield async.return_value(arequests.Response(
            status_code=200, content=bson.BSON().encode({}), headers={
                'Content-Type': 'application/bson'
            }))

    if expected_error is None:
        response = yield order_core._send_bson_request(
            'localhost/internal/processing/v1/event/foo', {}, {}, {}, 'some_id')
        assert response == {}
    else:
        with pytest.raises(expected_error):
            yield order_core._send_bson_request(
                'localhost/internal/processing/v1/event/foo', {}, {}, {}, 'some_id')
    assert len(mock_post_event.calls) == called
