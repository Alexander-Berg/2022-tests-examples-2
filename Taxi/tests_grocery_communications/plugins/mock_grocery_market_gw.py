import pytest


@pytest.fixture(name='grocery_market_gw')
def mock_grocery_market_gw(mockserver):
    class Context:
        def __init__(self):
            self.v1_notify_expected_json = None
            self.v1_notify_response_code = None

        def set_v1_notify(self, expected_json, response_code):
            self.v1_notify_expected_json = expected_json
            self.v1_notify_response_code = response_code

        def times_gw_v1_notify_called(self):
            return mock_check_v1_notify_request.times_called

    context = Context()

    @mockserver.json_handler('/grocery-market-gw/internal/market-gw/v1/notify')
    def mock_check_v1_notify_request(request):
        assert request.json == context.v1_notify_expected_json
        return mockserver.make_response(status=context.v1_notify_response_code)

    return context
