import enum

import pytest

COMBO_REVISION = 'pigeon_revision_{}'


def get_combo_group(
        *,
        options_to_select=1,
        is_select_unique=True,
        products=['pigeon-product-1'],
        title_tanker_key='title-tanker-key',
):
    return {
        'nameTankerKey': {'keyset': 'test-keyset', 'key': title_tanker_key},
        'optionsToSelect': options_to_select,
        'isSelectUnique': is_select_unique,
        'options': [{'skuId': product_id} for product_id in products],
    }


DEFAULT_GROUP = get_combo_group()


class ComboType(enum.Enum):
    DISCOUNT = 'discount'
    RECIPE = 'recipe'


@pytest.fixture(name='pigeon', autouse=True)
def mock_pigeon(mockserver):
    class Context:
        def __init__(self):
            self._combo_products = []

        def add_combo_product(
                self,
                *,
                combo_id,
                revision=None,
                combo_type=ComboType.DISCOUNT,
                linked_products=[],
                name_tanker_key={'keyset': 'test-keyset', 'key': 'test-key'},
                product_groups=[DEFAULT_GROUP],
                status='active',
        ):
            self._combo_products.append(
                {
                    'comboId': combo_id,
                    'comboRevision': (
                        COMBO_REVISION.format(combo_id)
                        if revision is None
                        else revision
                    ),
                    'linkedMetaProducts': [
                        {'skuId': product_id} for product_id in linked_products
                    ],
                    'nameTankerKey': name_tanker_key,
                    'groups': product_groups,
                    'meta': {'status': status, 'type': combo_type.value},
                },
            )

        @property
        def combo_products(self):
            return self._combo_products

    ctx = Context()

    @mockserver.json_handler('/pigeon/internal/export/v1/product-combos')
    def _mock_pigeon_response(request):
        return {'items': ctx.combo_products, 'lastCursor': 0}

    @mockserver.json_handler('/pigeon/internal/catalog/v1/categories')
    def _mock_categories_response(request):
        return {'items': [], 'lastCursor': 0}

    @mockserver.json_handler('/pigeon/internal/catalog/v1/groups')
    def _mock_groups_response(request):
        return {'items': [], 'lastCursor': 0}

    @mockserver.json_handler('/pigeon/internal/catalog/v1/layouts')
    def _mock_layouts_response(request):
        return {'items': [], 'lastCursor': 0}

    return ctx
