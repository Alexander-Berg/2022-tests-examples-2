# pylint: disable=import-error

from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='grocery_sensitive', autouse=True)
def mock_grocery_sensitive(mockserver, taxi_config):
    class Context:
        def __init__(self):
            self.store = HandleContext()

    context = Context()

    @mockserver.json_handler('/grocery-sensitive/sensitive/v1/store')
    def _mock_sensitive_store(request):
        handler = context.store
        handler(request)

        return mockserver.make_response(json={}, status=handler.status_code)

    return context
