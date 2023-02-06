import pytest


@pytest.fixture(name='grocery_caas_upsale')
def mock_grocery_caas_recent(mockserver):
    class Context:
        def __init__(self):
            upsale_ids = ['product-3', 'product-5', 'product-7', 'product-8']
            self._upsale_items = {
                'items': [
                    {'product_id': upsale_id} for upsale_id in upsale_ids
                ],
            }

        @property
        def upsale_items(self):
            return self._upsale_items

        @property
        def times_called(self):
            return upsale_handler.times_called

        @property
        def has_calls(self):
            return upsale_handler.has_calls

    context = Context()

    @mockserver.json_handler('/grocery-upsale/internal/upsale/v1/match')
    def upsale_handler(request):
        return context.upsale_items

    return context
