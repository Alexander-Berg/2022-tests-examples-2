import pytest


class TimetableContext:
    def __init__(self):
        self.response = []
        self.mock = None

    def set_mock(self, mock):
        self.mock = mock

    def reset(self):
        pass

    def wait_call(self):
        self.mock.wait_call()

    def set_response(self, response):
        self.response = response


@pytest.fixture(autouse=True)
def mock_timetable_airport_queue(mockserver):
    timetable_context = TimetableContext()

    @mockserver.json_handler('/timetable/v1/airport/rov/flight/')
    def handler(request):
        return timetable_context.response

    timetable_context.set_mock(handler)
    return timetable_context
