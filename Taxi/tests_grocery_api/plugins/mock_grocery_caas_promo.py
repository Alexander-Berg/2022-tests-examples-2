import pytest


@pytest.fixture(name='grocery_caas_promo')
def mock_grocery_caas_promo(mockserver):
    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/cashback',
    )
    def cashback_handler(request):
        assert 'layout_id' in request.json
        return context.cashback_category_data

    @mockserver.json_handler(
        '/grocery-caas-promo/internal/v1/caas-promo/v1/category/discounts',
    )
    def discounts_handler(request):
        assert 'layout_id' in request.json
        return context.money_category_data

    class Context:
        def __init__(self):
            self.mapping = {
                'promo-caas': discounts_handler,
                'cashback-caas': cashback_handler,
            }
            self._money_category_data = {
                'items': [],
                'products': [],
                'subcategories': [],
            }
            self._cashback_category_data = {
                'items': [],
                'products': [],
                'subcategories': [],
            }

        def add_product(self, *, product_id, is_cashback=False):
            data = (
                self._cashback_category_data
                if is_cashback
                else self._money_category_data
            )
            data['items'].append({'id': product_id, 'item_type': 'product'})
            data['products'].append({'product_id': product_id})

        def add_products(self, *, product_ids, is_cashback=False):
            for product_id in product_ids:
                self.add_product(
                    product_id=product_id, is_cashback=is_cashback,
                )

        def add_subcategory(
                self,
                *,
                subcategory_id,
                title_tanker_key,
                keyset='virtual_catalog',
                is_cashback=False,
        ):
            data = (
                self._cashback_category_data
                if is_cashback
                else self._money_category_data
            )
            data['items'].append(
                {'id': subcategory_id, 'item_type': 'subcategory'},
            )
            data['subcategories'].append(
                {
                    'subcategory_id': subcategory_id,
                    'tanker_key': title_tanker_key,
                    'keyset_tanker_key': {
                        'key': title_tanker_key,
                        'keyset': keyset,
                    },
                },
            )

        @property
        def money_category_data(self):
            return self._money_category_data

        @property
        def cashback_category_data(self):
            return self._cashback_category_data

        def times_called(self, category_name):
            return self.mapping[category_name].times_called

        def has_calls(self, category_name):
            return self.mapping[category_name].has_calls

    context = Context()

    return context
