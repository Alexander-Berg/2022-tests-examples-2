import pytest

COUPONS_LIST = 'coupons-list'


@pytest.fixture(name='grocery_coupons')
def mock_grocery_coupons(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.check_request = {COUPONS_LIST: None}
            self.response = {COUPONS_LIST: {'coupons': []}}

        def check_coupons_list(self, **argv):
            self.check_request[COUPONS_LIST] = {}
            for key in argv:
                self.check_request[COUPONS_LIST][key] = argv[key]

        def set_coupons_list_response(self, response):
            self.response[COUPONS_LIST] = response

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def times_coupons_list_called(self):
            return mock_coupons_list.times_called

        def flush_all(self):
            mock_coupons_list.flush()

    context = Context()

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/list')
    def mock_coupons_list(request):
        if COUPONS_LIST in context.error_code:
            code = context.error_code[COUPONS_LIST]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_request[COUPONS_LIST] is not None:
            for key, value in context.check_request[COUPONS_LIST].items():
                assert request.json[key] == value, key

        return context.response[COUPONS_LIST]

    return context
