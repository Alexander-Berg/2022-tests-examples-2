import pytest


@pytest.fixture(name='routehistory', autouse=True)
def mock_eats_core_integrations(mockserver):
    class Context:
        def __init__(self):
            self.created_since = None
            self.results = None
            self.max_results = None

        def set_data(self, created_since=None, results=None, max_results=None):
            self.created_since = created_since
            self.results = results
            self.max_results = max_results

        @property
        def times_called(self):
            return grocery_get.times_called

    context = Context()

    @mockserver.json_handler('/routehistory/routehistory/grocery-get')
    def grocery_get(request):
        assert request.json['created_since'] == context.created_since
        if context.max_results:
            assert request.json['max_results'] == context.max_results

        return mockserver.make_response(
            json={'results': context.results}, status=200,
        )

    return context
