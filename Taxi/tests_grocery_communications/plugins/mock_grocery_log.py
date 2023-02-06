import pytest


@pytest.fixture(name='grocery_order_log')
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.successful_meta_orders = []
            self.failed_order_ids = []

        def times_sms_send_called(self):
            return mock_get_orders_meta_by_ids.times_called

        def set_get_orders_meta_response(
                self, successful_meta_orders, failed_order_ids,
        ):
            self.successful_meta_orders = successful_meta_orders
            self.failed_order_ids = failed_order_ids

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/v1/order-log/v1/get-orders-meta-by-ids',
    )
    def mock_get_orders_meta_by_ids(request):
        return {
            'orders_meta': context.successful_meta_orders,
            'failed_order_ids': context.failed_order_ids,
        }

    return context
