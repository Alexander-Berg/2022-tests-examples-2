import pytest


@pytest.fixture(name='grocery_orders_make')
def mock_grocery_orders_make(mockserver):
    status = 200
    check_request = False
    expected_request_body = {}
    error_code = None

    @mockserver.json_handler('/grocery-orders/internal/v1/orders/v1/make')
    def orders_make(request):
        if check_request:
            assert request.json == expected_request_body
        if status == 200:
            return {'order_id': '12345-grocery'}
        json = None
        if error_code:
            json = {'code': error_code, 'message': 'some_message'}
        return mockserver.make_response(status=status, json=json)

    class Context:
        def set_response_status(self, new_status, new_error_code=None):
            nonlocal status, error_code
            status = new_status
            error_code = new_error_code

        def check_request(self, expected_request):
            nonlocal check_request, expected_request_body
            check_request = True
            expected_request_body = expected_request

        @property
        def times_called(self):
            return orders_make.times_called

        @property
        def has_calls(self):
            return orders_make.has_calls

    context = Context()
    return context
