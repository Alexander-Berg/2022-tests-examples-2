# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='grocery_payments_tracking', autouse=True)
def mock_grocery_payments_tracking(mockserver):
    class Context:
        def __init__(self):
            self.update = HandleContext()

    context = Context()

    @mockserver.json_handler(
        '/grocery-payments-tracking/internal/v1/payments-tracking/update',
    )
    def _mock_update(request):
        context.update(request)

        return {}

    return context
