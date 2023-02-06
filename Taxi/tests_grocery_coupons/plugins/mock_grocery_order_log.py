import pytest


@pytest.fixture(name='grocery_order_log')
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.yandex_uid = None
            self.not_canceled_orders_count = None

            self.check_request_flag = False

        def check_request(self, yandex_uid=None):
            self.yandex_uid = yandex_uid

            self.check_request_flag = True

        def set_not_canceled_orders_count(self, count):
            self.not_canceled_orders_count = count

        def times_orders_info(self):
            return mock_orders_info.times_called

        def flush(self):
            mock_orders_info.flush()

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/orders-info',
    )
    def mock_orders_info(request):
        if context.check_request_flag:
            if context.yandex_uid:
                assert (
                    request.json['user_identity']['yandex_uid']
                    == context.yandex_uid
                )

        return {
            'not_canceled_orders_count': (context.not_canceled_orders_count),
        }

    return context
