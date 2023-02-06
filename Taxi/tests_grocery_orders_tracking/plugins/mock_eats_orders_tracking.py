import pytest


@pytest.fixture(name='eats_orders_tracking')
def mock_eats_orders_tracking(mockserver, load_json):
    class Context:
        def __init__(self):
            self.tracking_response = None
            self.tracking_headers = None
            self.tracking_error_code = None

        def set_tracking_error_code(self, code):
            self.tracking_error_code = code

        def set_tracking_response(self, response):
            self.tracking_response = response

        def check_tracking_headers(self, headers):
            self.tracking_headers = headers

        def times_tracking_called(self):
            return mock_tracking.times_called

    context = Context()

    @mockserver.json_handler(
        '/eats-orders-tracking/eats/v1/eats-orders-tracking/v1/tracking',
    )
    def mock_tracking(request):
        if context.tracking_headers is not None:
            for key, value in context.tracking_headers.items():
                assert request.headers[key] == value
        if context.tracking_error_code is not None:
            return mockserver.make_response(
                'fail', status=context.tracking_error_code,
            )
        if context.tracking_response is not None:
            return context.tracking_response
        return load_json(
            '../test_orders_state_tracking/eda_orders_tracking_response.json',
        )

    return context
