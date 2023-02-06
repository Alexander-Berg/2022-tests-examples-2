import pytest


@pytest.fixture(name='payments_tracking', autouse=True)
def mock_grocery_payments_tracking(mockserver):
    class Context:
        def __init__(self):
            self.update_status_data = None

        def check_update_status(self, **argv):
            self.update_status_data = {}
            for key in argv:
                self.update_status_data[key] = argv[key]

        def times_update_status_called(self):
            return mock_update_status.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-payments-tracking'
        '/internal/v1/payments-tracking/update-status',
    )
    def mock_update_status(request):
        if context.update_status_data is not None:
            for key, value in context.update_status_data.items():
                assert request.json[key] == value, key

    return context
