import pytest


from taxi.core import async
from taxi.external import alice
from taxi.external import tvm


@pytest.inline_callbacks
def test_alice_send(patch):

    payload = {
        'event': 'on_assign',
        'service_data': 'on_assign_data',
        'callback_data': 'alice_specific_data',
        'not_needed': 'not_needed'  # wont' be used in request
    }
    tvm_src_service = 'imports'
    tvm_ticket = 'tvm ticket'

    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):

        assert src_service == tvm_src_service
        assert dst_service == 'alice'

        yield
        async.return_value({tvm.TVM_TICKET_HEADER: tvm_ticket})

    @patch('taxi.external.alice.Client._request')
    @async.inline_callbacks
    def alice_request(json, headers, *args, **kwargs):
        good_json = {
            'event': 'on_assign',
            'service': 'taxi',
            'service_data': 'on_assign_data',
            'callback_data': 'alice_specific_data'
        }
        assert json == good_json
        assert headers[tvm.TVM_TICKET_HEADER] == tvm_ticket

        yield
        async.return_value()

    created_payload = alice.make_common_payload(payload)
    yield alice.send(created_payload, tvm_src_service)
    assert len(get_auth_headers.calls) == 1
    assert len(alice_request.calls) == 1
