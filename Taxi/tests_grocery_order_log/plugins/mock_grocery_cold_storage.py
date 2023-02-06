import pytest

ORDERS = 'orders'

ITEM_IDS = 'item_ids'
FIELDS = 'fields'


@pytest.fixture(name='grocery_cold_storage')
def mock_grocery_cold_storage(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.response_body = {'items': []}
            self.item_ids = None
            self.fields = None
            self.prefetch_item_ids = None
            self.prefetch_fields = None

        @property
        def orders_times_called(self) -> int:
            return _get_order_log.times_called

        @property
        def prefetch_times_called(self) -> int:
            return _prefetch_order_log.times_called

        def set_get_request(self, *, item_ids=None, fields=None):
            if item_ids is not None:
                assert isinstance(item_ids, set)
                self.item_ids = item_ids
            if fields is not None:
                self.fields = fields

        def set_prefetch_request(self, *, item_ids=None, fields=None):
            if item_ids is not None:
                assert isinstance(item_ids, set)
                self.prefetch_item_ids = item_ids
            if item_ids is not None:
                self.prefetch_fields = fields

        def set_order_log_response(self, status_code=200, items=None):
            self.status_code = status_code
            self.response_body = {'items': items if items is not None else []}

    context = Context()

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/order-log',
    )
    def _get_order_log(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if context.item_ids is not None:
            assert set(body[ITEM_IDS]) == context.item_ids
        if context.fields is not None:
            assert body[FIELDS] == context.fields

        return mockserver.make_response(
            status=context.status_code, json=context.response_body,
        )

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/prefetch/order-log',
    )
    def _prefetch_order_log(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if context.prefetch_item_ids is not None:
            assert set(body[ITEM_IDS]) == context.prefetch_item_ids
        if context.prefetch_fields is not None:
            assert body[FIELDS] == context.prefetch_fields

        return {}

    return context
