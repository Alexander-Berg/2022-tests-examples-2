# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='user_state')
def mock_user_state(mockserver):
    class Context:
        def __init__(self):
            self.last_payment_method = HandleContext()
            self.service = None

    context = Context()

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_save_last_pm(request):
        payment_method = request.json.get('flows')[0]

        handler = context.last_payment_method
        handler.process(payment_method, request.headers)

        if context.service is not None:
            assert request.query['service'] == context.service

        return {}

    return context
