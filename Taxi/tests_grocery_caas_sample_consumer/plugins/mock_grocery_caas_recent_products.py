import pytest


@pytest.fixture(name='grocery_caas_recent_products')
def mock_grocery_caas_recent(mockserver):
    class Context:
        def __init__(self):
            self._category_data = {
                'product_ids': [
                    'some_id1',
                    'some_id2',
                    'some_id3',
                    'some_id4',
                ],
            }

            self._presented = {'presented': True}
            self._orders_data = {'orders': []}

        @property
        def category_data(self):
            return self._category_data

        @property
        def orders_data(self):
            return self._orders_data

        @property
        def presented(self):
            return self._presented

        @property
        def times_called(self):
            return category_handler.times_called

        @property
        def has_calls(self):
            return category_handler.has_calls

        @property
        def times_called_presence(self):
            return presence_handler.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-fav-goods/internal/v1/recent-goods/check-presence',
    )
    def presence_handler(request):
        return context.presented

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/get')
    def category_handler(request):
        return context.category_data

    return context
