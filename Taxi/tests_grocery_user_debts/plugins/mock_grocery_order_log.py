import pytest


@pytest.fixture(name='grocery_order_log')
def mock_order_log(mockserver):
    class Context:
        def __init__(self):
            self.ids_by_range = []
            self.check_ids_by_range_data = None

        def mock_ids_by_range(self, ids):
            self.ids_by_range = ids

        def check_ids_by_range(self, **kwargs):
            self.check_ids_by_range_data = kwargs

        def ids_by_range_times_called(self):
            return _mock_ids_by_range.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/ids-by-range',
    )
    def _mock_ids_by_range(request):
        if context.check_ids_by_range_data is not None:
            for key, value in context.check_ids_by_range_data.items():
                assert request.json[key] == value, key

        return {'order_ids': context.ids_by_range}

    return context
