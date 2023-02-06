import pytest

PAYLOAD_KEY = 'payload-key'


@pytest.fixture(name='adjust_provider')
def mock_adjust_provider(mockserver):
    data = {}

    @mockserver.json_handler('/eats-adjust-provider/events')
    def mock_events(request):
        expected_payload = data.get(PAYLOAD_KEY, None)
        if expected_payload is not None:
            assert request.json == expected_payload

        return mockserver.make_response('', 204)

    class Context:
        def check_event_payload(self, payload):
            data[PAYLOAD_KEY] = payload

        def events_times_called(self):
            return mock_events.times_called

        def flush(self):
            mock_events.flush()

    context = Context()
    return context
