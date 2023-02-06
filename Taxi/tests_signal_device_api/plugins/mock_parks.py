# encoding=utf-8
import pytest


@pytest.fixture(name='parks')
def _mock_parks(mockserver):
    class ParksContext:
        def __init__(self):
            self.parks = None
            self.parks_response = {}

        def set_parks_response(self, response):
            self.parks_response = response

    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _get_parks(request):
        request.get_data()
        return context.parks_response

    context.parks = _get_parks

    return context
