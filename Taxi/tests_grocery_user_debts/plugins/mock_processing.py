# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='processing', autouse=True)
def mock_processing(mockserver):
    class Context:
        def __init__(self):
            self.debts = HandleContext()
            self.non_critical = HandleContext()
            self.processing = HandleContext()
            self.tips = HandleContext()

    context = Context()

    @mockserver.json_handler('/processing/v1/grocery/debts_v2', prefix=True)
    def _mock_debts_v2(request):
        context.debts(request)

        return {'event_id': 'event_id'}

    @mockserver.json_handler('/processing/v1/grocery/processing', prefix=True)
    def _mock_processing(request):
        context.processing(request)

        return {'event_id': 'event_id'}

    @mockserver.json_handler(
        '/processing/v1/grocery/processing_tips', prefix=True,
    )
    def _mock_processing_tips(request):
        context.tips(request)

        return {'event_id': 'event_id'}

    @mockserver.json_handler(
        '/processing/v1/grocery/processing_non_critical', prefix=True,
    )
    def _mock_non_critical(request):
        context.non_critical(request)

        return {'event_id': 'event_id'}

    return context
