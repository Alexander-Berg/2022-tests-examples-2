import pytest


CREATE_COMPENSATION = 'create-compensation-handler'


@pytest.fixture(name='grocery_cashback', autouse=True)
def mock_grocery_coupons(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.check_create_compensation_data = None

        def check_create_compensation(self, **argv):
            self.check_create_compensation_data = {}
            for key in argv:
                self.check_create_compensation_data[key] = argv[key]

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def times_create_called(self):
            return mock_create_compensation.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-cashback/cashback/v1/create-compensation',
    )
    def mock_create_compensation(request):
        if CREATE_COMPENSATION in context.error_code:
            code = context.error_code[CREATE_COMPENSATION]
            return mockserver.make_response('{}', code)

        if context.check_create_compensation_data is not None:
            for key, value in context.check_create_compensation_data.items():
                assert request.json[key] == value, key
        return {}

    return context
