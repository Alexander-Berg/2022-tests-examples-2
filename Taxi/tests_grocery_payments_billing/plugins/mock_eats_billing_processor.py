# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='eats_billing_processor')
def mock_eats_billing_processor(mockserver):
    class Context:
        def __init__(self):
            self.v1_create = HandleContext()

    context = Context()

    @mockserver.json_handler('/eats-billing-processor/v1/create')
    def _v1_create(request):
        handler = context.v1_create
        handler(request)

        return mockserver.make_response(status=200, json={'event_id': '1'})

    return context
