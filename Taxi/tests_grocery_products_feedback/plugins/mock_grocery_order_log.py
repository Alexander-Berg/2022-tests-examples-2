import pytest


@pytest.fixture(name='grocery_order_log')
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.yandex_uid = None
            self.order_id = None
            self.retrieve_raw_error = None
            self.calculations = None

            self.created_at = None
            self.status = None

            self.check_request_flag = False
            self.order_raw_response = None

        def set_order_raw(self, orders):
            self.order_raw_response = orders

        def set_retrieve_raw_error(self, code=500):
            self.retrieve_raw_error = code

        def times_order_raw_called(self):
            return mock_order_raw.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_order_raw(request):
        if context.retrieve_raw_error:
            return mockserver.make_response(
                '', status=context.retrieve_raw_error,
            )

        return context.order_raw_response

    return context
