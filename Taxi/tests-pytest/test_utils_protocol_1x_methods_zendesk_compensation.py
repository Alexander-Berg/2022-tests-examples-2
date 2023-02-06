import json
import mocks
import pytest

from utils.protocol_1x.methods import zendesk_compensation


@pytest.mark.parametrize(
    'data,expected_status,expected_response,expected_stq_put',
    [
        (
            {
                'order_id': 'some_order_id',
                'compensation_amount': '123',
                'comment': '456',
            },
            None,
            {},
            {
                'queue': 'support_info_compensation_ticket',
                'task_id': None,
                'args': ('some_order_id', '123', '456'),
                'kwargs': {},
                'eta': None,
            },
        ),
    ],
)
@pytest.inline_callbacks
def test_zendesk_compensation(data, expected_status, expected_response,
                              expected_stq_put, patch):

    @patch('taxi_stq._client.put')
    @pytest.inline_callbacks
    def _dummy_put(queue, eta=None, task_id=None, args=None, kwargs=None):
        yield

    request = mocks.FakeRequest(content=json.dumps(data))
    response = yield zendesk_compensation.Method().POST(request)
    assert request.response_code == expected_status
    if expected_status is not None:
        assert response == expected_response

    stq_put_calls = _dummy_put.calls
    if expected_stq_put is None:
        assert not stq_put_calls
    else:
        del stq_put_calls[0]['kwargs']['log_extra']
        assert stq_put_calls[0] == expected_stq_put
