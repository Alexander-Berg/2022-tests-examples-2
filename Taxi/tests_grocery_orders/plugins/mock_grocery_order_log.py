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
            self.personal_email_id = None
            self.period = None

        def set_order_ids_response(
                self, order_ids, personal_email_id=None, period=None,
        ):
            self.order_ids = order_ids
            self.personal_email_id = personal_email_id
            self.period = period

        def times_get_order_ids_called(self):
            return mock_get_order_ids.times_called

        def times_called_ids_by_range(self):
            return mock_ids_by_range.times_called

        def set_order_id_response(self, order_id):
            self.order_id = order_id

        def times_orders_info_called(self):
            return mock_orders_info.times_called

        def set_not_canceled_order_count(
                self, count, yandex_uid, personal_phone_id,
        ):
            self.not_canceled_orders_count = count
            self.yandex_uid = yandex_uid
            self.personal_phone_id = personal_phone_id

        def flush_all(self):
            mock_ids_by_range.flush()
            mock_orders_info.flush()
            mock_get_order_ids.flush()
            mock_get_order_id.flush()

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/get-order-ids',
    )
    def mock_get_order_ids(request):
        return {'order_ids': context.order_ids}

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/get-order-id',
    )
    def mock_get_order_id(request):
        if context.order_id is None:
            return mockserver.make_response(status=404)
        return {'order_id': context.order_id}

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/orders-info',
    )
    def mock_orders_info(request):
        assert request.json['user_identity']['yandex_uid'] is not None
        assert request.json['user_identity']['bound_yandex_uids'] is not None

        return {'not_canceled_orders_count': context.not_canceled_orders_count}

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/ids-by-range',
    )
    def mock_ids_by_range(request):
        if context.personal_email_id is not None:
            assert (
                request.json['personal_email_id'] == context.personal_email_id
            )
        if context.period is not None:
            if 'start' in context.period:
                assert (
                    request.json['period']['start'] == context.period['start']
                )
            if 'end' in context.period:
                assert request.json['period']['end'] == context.period['end']

        return {'order_ids': context.order_ids}

    return context
