import pytest


@pytest.fixture(name='grocery_caas_markdown')
def mock_grocery_caas_markdown(mockserver):
    class Context:
        def __init__(self):
            self._category_data = {
                'items': [],
                'products': [],
                'subcategories': [],
            }

        def add_product(self, *, product_id, quantity='1'):
            self._category_data['items'].append(
                {'id': product_id, 'item_type': 'product'},
            )
            self._category_data['products'].append(
                {'product_id': product_id, 'quantity': quantity},
            )

        @property
        def category_data(self):
            return self._category_data

        @property
        def times_called(self):
            return category_handler.times_called

        @property
        def has_calls(self):
            return category_handler.has_calls

    context = Context()

    @mockserver.json_handler(
        '/grocery-caas-markdown/internal/v1/caas-markdown/v2/category',
    )
    def category_handler(request):
        return context.category_data

    return context
