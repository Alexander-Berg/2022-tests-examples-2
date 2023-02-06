# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='trust')
def mock_trust(mockserver, taxi_config):
    class Context:
        def __init__(self):
            self.bindings_create = HandleContext()
            self.bindings_start = HandleContext()

    context = Context()

    @mockserver.json_handler('/yb-trust-payments/bindings')
    def _mock_bindings_create(request):
        handler = context.bindings_create
        handler(request)

        response = handler.response or {
            'status': 'success',
            'purchase_token': 'purchase_token',
        }

        return mockserver.make_response(
            json=response, status=handler.status_code,
        )

    @mockserver.json_handler(
        '/yb-trust-payments/bindings/purchase_token/start',
    )
    def _mock_bindings_start(request):
        handler = context.bindings_start
        handler.process(None, request.headers)

        response = handler.response or {
            'status': 'success',
            'binding_url': 'binding_url',
        }

        return mockserver.make_response(
            json=response, status=handler.status_code,
        )

    taxi_config.set(
        YB_TRUST_PAYMENTS_CLIENT_QOS={
            '__default__': {'attempts': 1, 'timeout-ms': 1000},
        },
    )

    return context
