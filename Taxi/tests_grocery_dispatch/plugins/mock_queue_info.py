import pytest

QUEUE_INFO_DEFAULT_RESPONSE = {
    'couriers': [
        {'courier_id': '43', 'checkin_timestamp': '2020-10-05T16:28:00.000Z'},
        {'courier_id': '33', 'checkin_timestamp': '2020-10-05T16:28:00.000Z'},
    ],
}


@pytest.fixture(autouse=True, name='queue_info')
def mock_queue_info(mockserver):
    class Context:
        def __init__(self):
            self.queue_info_response = None

        def set_queue_info_response(self, response):
            self.queue_info_response = response

        def times_queue_info_called(self):
            return mock_queue_info_.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/queue-info',
    )
    def mock_queue_info_(request):
        if context.queue_info_response is not None:
            return context.queue_info_response

        return QUEUE_INFO_DEFAULT_RESPONSE

    return context


@pytest.fixture(autouse=True, name='queue_info_v2')
def mock_queue_info_v2(mockserver):
    class Context:
        def __init__(self):
            self.queue_info_response = None

        def set_queue_info_response(self, response):
            self.queue_info_response = response

        def times_queue_info_v2_called(self):
            return mock_queue_info_v2_.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def mock_queue_info_v2_(request):
        if context.queue_info_response is not None:
            return context.queue_info_response

        return QUEUE_INFO_DEFAULT_RESPONSE

    return context
