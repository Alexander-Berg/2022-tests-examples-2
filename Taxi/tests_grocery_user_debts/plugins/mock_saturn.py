# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest


@pytest.fixture(name='saturn', autouse=True)
def mock_saturn(mockserver):
    class Context:
        def __init__(self):
            self.grocery_search = HandleContext()
            self.grocery_search_status = False

    context = Context()

    @mockserver.json_handler('/saturn/api/v1/grocery/search')
    def _mock_grocery_search(request):
        handler = context.grocery_search
        handler(request)

        if not handler.is_ok:
            return mockserver.make_response(status=handler.status_code)

        status = context.grocery_search_status

        return {
            'reqid': request.json['request_id'],
            'puid': request.json['puid'],
            'score': 100,
            'score_percentile': 90,
            'formula_id': request.json['formula_id'],
            'formula_description': 'grocery',
            'data_source': 'puid/2021-06-21',
            'status': 'accepted' if status else 'rejected',
        }

    return context
