import pytest


@pytest.fixture(name='grocery_caas_promo')
def mock_grocery_caas_promo(mockserver):
    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/best-offers',
    )
    def best_offers_handler(request):
        return context.category_data

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/cashback',
    )
    def cashback_handler(request):
        return context.category_data

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/discounts',
    )
    def discounts_handler(request):
        return context.category_data

    class Context:
        def __init__(self):
            self.mapping = {
                'best-offers': best_offers_handler,
                'promo-caas': discounts_handler,
                'cashback-caas': cashback_handler,
            }
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
                    },
                    {'product_id': 'some_id2', 'tags': []},
                    {'product_id': 'some_id3'},
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
                    {'product_id': 'some_id_22', 'tags': []},
                    {'product_id': 'some_id_23'},
                ],
                'subcategories': [
                    {
                        'subcategory_id': 'test_subcategory_1',
                        'tanker_key': 'test_tanker_key_1',
                        'keyset_tanker_key': {
                            'key': 'test_tanker_key_1',
                            'keyset': 'virtual_catalog',
                        },
                    },
                    {
                        'subcategory_id': 'test_subcategory_2',
                        'tanker_key': 'test_tanker_key_2',
                        'keyset_tanker_key': {
                            'key': 'test_tanker_key_2',
                            'keyset': 'virtual_catalog',
                        },
                    },
                    {
                        'subcategory_id': 'test_subcategory_3',
                        'tanker_key': 'test_tanker_key_3',
                        'keyset_tanker_key': {
                            'key': 'test_tanker_key_3',
                            'keyset': 'virtual_catalog',
                        },
                    },
                ],
            }

        @property
        def category_data(self):
            return self._category_data

        def times_called(self, category_name):
            return self.mapping[category_name].times_called

        def has_calls(self, category_name):
            return self.mapping[category_name].has_calls

    context = Context()

    return context
