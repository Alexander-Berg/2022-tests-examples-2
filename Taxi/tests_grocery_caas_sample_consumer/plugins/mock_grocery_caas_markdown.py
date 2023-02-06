import pytest


@pytest.fixture(name='grocery_caas_markdown')
def mock_grocery_caas_markdown(mockserver):
    class Context:
        def __init__(self):
            self._category_data = {
                'items': [
                    {'id': 'some_id1', 'item_type': 'product'},
                    {'id': 'some_id2', 'item_type': 'product'},
                    {'id': 'some_id3', 'item_type': 'product'},
                    {'id': 'test_subcategory_1', 'item_type': 'subcategory'},
                    {'id': 'some_id_11', 'item_type': 'product'},
                    {'id': 'some_id_12', 'item_type': 'product'},
                    {'id': 'some_id_13', 'item_type': 'product'},
                    {'id': 'test_subcategory_2', 'item_type': 'subcategory'},
                    {'id': 'some_id_21', 'item_type': 'product'},
                    {'id': 'some_id_22', 'item_type': 'product'},
                    {'id': 'some_id_23', 'item_type': 'product'},
                    {'id': 'test_subcategory_3', 'item_type': 'subcategory'},
                    {'id': 'some_id1', 'item_type': 'product'},
                    {'id': 'some_id_13', 'item_type': 'product'},
                    {'id': 'some_id_23', 'item_type': 'product'},
                    {'id': 'test_subcategory_3', 'item_type': 'subcategory'},
                    {'id': 'some_id2', 'item_type': 'product'},
                ],
                'products': [
                    {
                        'product_id': 'some_id1',
                        'tags': ['test_tag_1', 'test_tag_2'],
                        'quantity': '12.3',
                    },
                    {'product_id': 'some_id2', 'tags': []},
                    {'product_id': 'some_id3', 'quantity': '34.56'},
                    {
                        'product_id': 'some_id_11',
                        'tags': ['test_tag_11', 'test_tag_12'],
                    },
                    {'product_id': 'some_id_12', 'tags': []},
                    {'product_id': 'some_id_13'},
                    {
                        'product_id': 'some_id_21',
                        'tags': ['test_tag_21', 'test_tag_22'],
                    },
                    {
                        'product_id': 'some_id_22',
                        'tags': [],
                        'quantity': '78.9',
                    },
                    {'product_id': 'some_id_23'},
                ],
                'subcategories': [
                    {
                        'subcategory_id': 'test_subcategory_1',
                        'tanker_key': 'test_tanker_key_1',
                    },
                    {
                        'subcategory_id': 'test_subcategory_2',
                        'tanker_key': 'test_tanker_key_2',
                    },
                    {
                        'subcategory_id': 'test_subcategory_3',
                        'tanker_key': 'test_tanker_key_3',
                    },
                ],
            }

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
