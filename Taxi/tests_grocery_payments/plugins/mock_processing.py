# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='processing', autouse=True)
def mock_processing(mockserver):
    class Context:
        def __init__(self):
            self.create_event = HandleContext()

    context = Context()

    @mockserver.json_handler('/processing/v1/grocery', prefix=True)
    def _mock_create(request):
        context.create_event(request)

        return {'event_id': 'event_id'}

    return context
