import pytest

OPEN_HATCH = 'open-hatch-handler'


@pytest.fixture(name='robot_sdc')
def mock_robot_sdc(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.check_open_hatch_data = None

        def check_open_hatch(self, **argv):
            self.check_open_hatch_data = {}
            for key in argv:
                self.check_open_hatch_data[key] = argv[key]

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def times_open_hatch_called(self):
            return mock_open_hatch.times_called

        def flush_all(self):
            mock_open_hatch.flush()

    context = Context()

    @mockserver.json_handler('/robot-sdc/api/robots/.*/open_hatch', regex=True)
    def mock_open_hatch(request):
        if OPEN_HATCH in context.error_code:
            code = context.error_code[OPEN_HATCH]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_open_hatch_data is not None:
            for key, value in context.check_open_hatch_data.items():
                assert request.json[key] == value, key

        return {'job_id': 123456}

    return context
