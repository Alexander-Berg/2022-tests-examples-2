import enum
from typing import List

import pytest


class ProductGroup:
    def __init__(
            self,
            is_selection_unique,
            options_to_select,
            products,
            title_tanker_key='title_tanker_key',
    ):
        self.is_selection_unique = is_selection_unique
        self.options_to_select = options_to_select
        self.products = products
        self.title_tanker_key = title_tanker_key

    def get_data(self):
        data = {
            'title_tanker_key': self.title_tanker_key,
            'is_selection_unique': self.is_selection_unique,
            'options_to_select': self.options_to_select,
            'products': self.products,
        }
        return data


class ComboType(enum.Enum):
    DISCOUNT = 'discount'
    RECIPE = 'recipe'


class ComboProduct:
    def __init__(
            self,
            combo_id,
            linked_meta_products,
            product_groups: List[ProductGroup],
            revision,
            combo_type=ComboType.RECIPE,
    ):
        self.combo_id = combo_id
        self.linked_meta_products = linked_meta_products
        self.product_groups = product_groups
        self.revision = revision
        self.combo_type = combo_type.value

    def get_data(self):
        product_groups_data = []
        for product_group in self.product_groups:
            product_groups_data.append(product_group.get_data())
        data = {
            'combo_id': self.combo_id,
            'linked_meta_products': self.linked_meta_products,
            'product_groups': product_groups_data,
            'revision': self.revision,
            'type': self.combo_type,
        }
        return data


@pytest.fixture(name='grocery_menu', autouse=True)
def mock_grocery_menu(mockserver):
    class Context:
        def __init__(self):
            self._combo_products = []

        def add_combo_product(self, combo_product: ComboProduct):
            self._combo_products.append(combo_product)

        @property
        def combo_products(self):
            return self._combo_products

        def flush_selected_times_called(self):
            _products_selected.flush()

        @property
        def selected_times_called(self):
            return _products_selected.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-menu/internal/v1/menu/v1/combo-products/list',
    )
    def _mock_combo_products(request):
        if 'cursor' in request.json:
            cursor = request.json['cursor']
        else:
            cursor = 0
        limit = request.json['limit']

        response_combo_products = []
        response_cursor = min(cursor + limit, len(context.combo_products))
        for combo_product in context.combo_products[cursor:response_cursor]:
            response_combo_products.append(combo_product.get_data())
        return {
            'combo_products': response_combo_products,
            'cursor': response_cursor,
        }

    @mockserver.json_handler(
        '/grocery-menu/internal/v1/menu/v1/combo-products/selected',
    )
    def _products_selected(request):
        response_combo_products = []
        for combo_product in context.combo_products:
            response_combo_products.append(combo_product.get_data())
        return mockserver.make_response(
            status=200, json={'combo_products': response_combo_products},
        )

    return context
