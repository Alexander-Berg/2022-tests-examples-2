import pytest


@pytest.fixture(name='eats_compensations_matrix', autouse=True)
def mock_eats_compensations_matrix(mockserver):
    class Context:
        def __init__(self):
            self.error_code = None
            self.inner_request = None
            self.compensation_list_response = None
            self.compensation_get_by_id_response = None
            self.get_pack_by_id_response = None
            self.get_situation_by_code_response = None

        def set_error_code(self, code):
            self.error_code = code

        def set_compensation_list_response(self, response):
            self.compensation_list_response = response

        def set_get_by_id_response(self, response):
            self.compensation_get_by_id_response = response

        def set_get_pack_by_id_response(self, response):
            self.get_pack_by_id_response = response

        def set_get_by_code_response(self, response):
            self.get_situation_by_code_response = response

        def times_compensation_list_called(self):
            return mock_eats_compensations_list.times_called

        def times_get_by_id_called(self):
            return mock_get_situation_by_id.times_called

        def times_get_pack_by_id_called(self):
            return mock_get_pack_by_id.times_called

        def times_get_by_code_called(self):
            return mock_get_situation_by_code.times_called

        def check_request(self, request):
            self.inner_request = request

    context = Context()

    @mockserver.json_handler(
        '/eats-compensations-matrix'
        '/eats-compensations-matrix/v1/api/compensation/submit_situation',
    )
    def mock_eats_compensations_list(request):
        if context.inner_request:
            assert context.inner_request == request.json
        if context.error_code:
            return mockserver.make_response(
                '{"code": "'
                + str(context.error_code)
                + '", "message": "Test error"}',
                status=context.error_code,
            )
        if context.compensation_list_response:
            return context.compensation_list_response
        return {}

    @mockserver.json_handler(
        '/eats-compensations-matrix'
        '/eats-compensations-matrix/v1/api/compensation/get_pack_by_id',
    )
    def mock_get_pack_by_id(request):
        if context.inner_request:
            assert context.inner_request == request.json
        if context.error_code:
            return mockserver.make_response(
                '{"code": "'
                + str(context.error_code)
                + '", "message": "Test error"}',
                status=context.error_code,
            )
        if context.get_pack_by_id_response:
            return context.get_pack_by_id_response
        return {}

    @mockserver.json_handler(
        '/eats-compensations-matrix'
        '/eats-compensations-matrix/v1/api/compensation/get_situation_by_code',
    )
    def mock_get_situation_by_code(request):
        if context.inner_request:
            assert context.inner_request == request.json
        if context.error_code:
            return mockserver.make_response(
                '{"code": "'
                + str(context.error_code)
                + '", "message": "Test error"}',
                status=context.error_code,
            )
        if context.get_situation_by_code_response:
            return context.get_situation_by_code_response
        return {}

    @mockserver.json_handler(
        '/eats-compensations-matrix'
        '/eats-compensations-matrix/v1/api/compensation/get_situation_by_id',
    )
    def mock_get_situation_by_id(request):
        if context.compensation_get_by_id_response:
            return context.compensation_get_by_id_response
        return {}

    return context
