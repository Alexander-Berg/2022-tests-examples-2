import pytest


@pytest.fixture
def taximeter_xservice_mock(mockserver):
    class ExamsContext:
        def __init__(self):
            self.response = {}

        def set_driver_exams_retrieve_response(self, data):
            self.response = data

    context = ExamsContext()

    @mockserver.json_handler(
        '/taximeter-xservice.taxi.yandex.net/utils/qc/driver/exams/retrieve',
    )
    def _driver_exams_retrieve(request):
        request.get_data()
        return context.response

    context.driver_exams_retrieve = _driver_exams_retrieve

    return context
