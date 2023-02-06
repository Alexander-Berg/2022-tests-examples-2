import pytest


@pytest.fixture(name='eats_core_integration')
def mock_eats_core_integration(mockserver):
    class Context:
        def __init__(self):
            self.courier_responses = []
            self.current_courier_response = 0
            self.courier_cursor = None

            self.courier_service_responses = []
            self.current_service_response = 0
            self.courier_service_cursor = None

        def set_courier_responses(self, responses):
            self.courier_responses = responses
            self.current_courier_response = 0

        def set_expected_courier_cursor(self, cursor):
            self.courier_cursor = cursor

        def courier_times_called(self):
            return mock_courier_update.times_called

        def set_courier_service_responses(self, responses):
            self.courier_service_responses = responses
            self.current_service_response = 0

        def set_courier_service_cursor(self, cursor):
            self.courier_service_cursor = cursor

        def courier_service_times_called(self):
            return mock_courier_service_update.times_called

    context = Context()

    @mockserver.json_handler(
        '/eats-core-integration/server/api/v1/courier/profiles/update',
    )
    async def mock_courier_update(request):
        if context.courier_cursor is not None:
            assert context.courier_cursor == request.query['cursor']

        response = context.courier_responses[context.current_courier_response]
        context.current_courier_response += 1
        return response

    @mockserver.json_handler(
        '/eats-core-integration/internal-api/v1/courier-service/updates',
    )
    async def mock_courier_service_update(request):
        if context.courier_service_cursor is not None:
            assert context.courier_service_cursor == request.query['cursor']

        response = context.courier_service_responses[
            context.current_service_response
        ]
        context.current_service_response += 1
        return response

    return context
