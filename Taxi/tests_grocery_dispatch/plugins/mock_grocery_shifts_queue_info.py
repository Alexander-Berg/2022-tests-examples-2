import pytest

GROCERY_SHIFTS_QUEUE_DEFAULT_RESPONSE = {
    'couriers': [
        {'courier_id': '43', 'checkin_timestamp': '2020-10-05T16:28:00.000Z'},
        {'courier_id': '33', 'checkin_timestamp': '2020-10-05T16:28:00.000Z'},
    ],
}


@pytest.fixture(autouse=True, name='grocery_shifts_queue_info')
def mock_grocery_shifts_queue_info(mockserver):
    class Context:
        def __init__(self):
            self.grocery_shifts_queue_response = None

        def set_grocery_queue_response(self, response):
            self.grocery_shifts_queue_response = response

        def times_grocery_queue_called(self):
            return mock_grocery_shifts_queue_.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/grocery-shifts/queue-info',
    )
    def mock_grocery_shifts_queue_(request):
        if context.grocery_shifts_queue_response is not None:
            return context.grocery_shifts_queue_response

        return GROCERY_SHIFTS_QUEUE_DEFAULT_RESPONSE

    return context
