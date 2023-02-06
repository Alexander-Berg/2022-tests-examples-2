import pytest


@pytest.fixture(name='grocery_order_log')
def mock_grocery_order_log(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.order_ids = []
            self.order_id = None
            self.not_canceled_orders_count = None
            self.yandex_uid = None
            self.personal_phone_id = None
            self.get_order_ids_check_data = None

        def set_order_ids_check_data(self, check_data):
            self.get_order_ids_check_data = check_data

        def set_order_ids_response(self, order_ids):
            self.order_ids = order_ids

        def times_get_order_ids_called(self):
            return mock_get_order_ids.times_called

        def times_orders_info_called(self):
            return mock_orders_info.times_called

        def set_not_canceled_order_count(
                self, count, yandex_uid, personal_phone_id,
        ):
            self.not_canceled_orders_count = count
            self.yandex_uid = yandex_uid
            self.personal_phone_id = personal_phone_id

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/get-order-ids',
    )
    def mock_get_order_ids(request):
        body = request.json
        if context.get_order_ids_check_data is not None:
            for key, value in context.get_order_ids_check_data.items():
                if value is not None:
                    assert body[key] == value
                else:
                    assert key not in body
        print(context.order_ids)
        return {'order_ids': context.order_ids}

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/orders-info',
    )
    def mock_orders_info(request):
        assert request.json['user_identity']['yandex_uid'] is not None
        assert request.json['user_identity']['bound_yandex_uids'] is not None

        return {'not_canceled_orders_count': context.not_canceled_orders_count}

    return context
