import pytest


@pytest.fixture
def trust_deliver_basket_success(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/deliver/',
        )
        def _handler(request):
            assert request.json == load_json(expected_request)

            resp_body = {
                'status': 'success',
                'status_desc': 'payment is updated',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock
