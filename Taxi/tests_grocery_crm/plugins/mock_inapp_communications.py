import pytest


@pytest.fixture(name='inapp_communications', autouse=True)
def mock_inapp_communications(mockserver):
    class Context:
        def __init__(self):
            self.saved_informers = []
            self.expected_request = None

        def set_request_check(self, request):
            self.expected_request = request

        def set_informers(self, informers):
            self.saved_informers = informers

        def grocery_comm_times_called(self):
            return mock_grocery_communications.times_called

        def flush(self):
            mock_grocery_communications.flush()

    context = Context()

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/grocery-communications',
    )
    def mock_grocery_communications(request):
        body = request.json
        if context.expected_request is not None:
            for key, value in context.expected_request.items():
                if value is not None:
                    assert body[key] == value
                else:
                    assert key not in body
        return mockserver.make_response(
            json={'informers': context.saved_informers},
        )

    return context
