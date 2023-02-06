import copy

import pytest

from tests_eats_products import conftest


PLACE_SLUG = 'slug'
PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': PLACE_SLUG}


@pytest.mark.parametrize('nmn_integration_version', ['v1'])
async def test_basic(
        taxi_config,
        taxi_eats_products,
        mockserver,
        load_json,
        # parametrize
        nmn_integration_version,
):
    place_id = 1
    brand_id = 1

    # >>> content of `mock_nomenclature_for_v2_menu_goods` mock,
    # exposed to validate json output
    context = conftest.NomenclatureMenuGoodsContext()

    @mockserver.json_handler('eats-nomenclature/v1/nomenclature')
    def _mock_nmn_nomenclature(request):
        result = context.handle_v1_nomenclature(request)
        assert _recursive_json_sort(
            _recursive_json_remove_none(result),
        ) == _recursive_json_sort(load_json('v1-nomenclature.json'))
        return result

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _mock_nmn_categories(request):
        result = context.handle_v1_place_categories(request)
        assert _recursive_json_sort(
            _recursive_json_remove_none(result),
        ) == _recursive_json_sort(load_json('v1-place-categories.json'))
        return result

    @mockserver.json_handler('eats-nomenclature/v1/places/categories')
    def _mock_nmn_places_categories(request):
        result = context.handle_v1_places_categories(request)
        assert _recursive_json_sort(
            _recursive_json_remove_none(result),
        ) == _recursive_json_sort(load_json('v1-places-categories.json'))
        return result

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _mock_nmn_products(request):
        result = context.handle_v1_products_info(request)
        assert _recursive_json_sort(
            _recursive_json_remove_none(result),
        ) == _recursive_json_sort(load_json('v1-products-info.json'))
        return result

    @mockserver.json_handler('eats-nomenclature/v1/place/products/info')
    def _mock_nmn_place_products(request):
        result = context.handle_v1_place_products_info(request)
        assert _recursive_json_sort(
            _recursive_json_remove_none(result),
        ) == _recursive_json_sort(load_json('v1-place-products-info.json'))
        return result

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/category_products/filtered',
    )
    def _mock_nmn_place_filtered(request):
        return {}

    context.set_globals(taxi_config, taxi_eats_products)
    context.set_mock_handlers(
        _mock_nmn_nomenclature,
        _mock_nmn_categories,
        _mock_nmn_places_categories,
        _mock_nmn_products,
        _mock_nmn_place_products,
        _mock_nmn_place_filtered,
    )

    # <<< `mock_nomenclature_for_v2_menu_goods`

    root_cat_5 = conftest.CategoryMenuGoods(
        public_id='5',
        name='Овощи',
        origin_id='category_id_5',
        sort_order=1,
        images=[('image_url_1', 1), ('image_url_2', 0)],
        is_available=False,
    )
    root_cat_6 = conftest.CategoryMenuGoods(
        public_id='6',
        name='Фрукты',
        origin_id='category_id_6',
        sort_order=2,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='1',
        name='Овощи и фрукты',
        origin_id='category_id_1',
        sort_order=3,
        images=[('image_url_1', 1), ('image_url_2', 0)],
    )
    root_cat_1.add_child_category(root_cat_5)
    root_cat_1.add_child_category(root_cat_6)

    product_1 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        name='Огурцы',
        origin_id='item_id_1',
        description='Описание Огурцы',
        images=[('url_1', 1), ('url_2', 2)],
        measure=(1, 'KGRM'),
        is_catch_weight=True,
        in_stock=10,
        price=4,
    )
    product_2 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        name='Помидоры',
        origin_id='item_id_2',
        description='Описание Помидоры',
        images=[('url_1', 1), ('url_2', 2)],
        measure=(1, 'KGRM'),
        is_catch_weight=True,
        in_stock=20,
        price=6,
    )
    product_3 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        name='Яблоки',
        origin_id='item_id_3',
        description='Описание Яблоки',
        images=[('url_1', 1), ('url_2', 2)],
        measure=(1, 'KGRM'),
        is_catch_weight=True,
        in_stock=50,
        price=3,
    )
    product_4 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
        name='Апельсины',
        origin_id='item_id_4',
        description='Описание Апельсины',
        images=[('url_1', 1), ('url_2', 2)],
        measure=(100, 'GRM'),
        is_catch_weight=True,
        in_stock=25,
        price=4,
    )
    product_5 = conftest.ProductMenuGoods(
        public_id='bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
        name='Бананы',
        origin_id='item_id_5',
        description='Описание Бананы',
        images=[('url_1', 1), ('url_2', 2)],
        measure=(500, 'GRM'),
        is_catch_weight=True,
        in_stock=30,
        price=3,
    )

    root_cat_6.add_product(product_3, sort_order=3)
    root_cat_6.add_product(product_4, sort_order=1)
    root_cat_6.add_product(product_5, sort_order=2)

    root_cat_5.add_product(product_1, sort_order=1)
    root_cat_5.add_product(product_2, sort_order=2)

    place = conftest.PlaceMenuGoods(
        place_id=place_id, slug=PLACE_SLUG, brand_id=brand_id,
    )
    place.add_root_category(root_cat_1)

    context.set_place(place)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['maxDepth'] = 200
    await context.invoke_menu_goods_basic(
        products_request, integration_version=nmn_integration_version,
    )


def _recursive_json_sort(json):
    if json:
        if isinstance(json, list):
            for sort_key in ['id', 'public_id', 'sort_order', 'url']:
                if sort_key in json[0]:
                    return sorted(
                        [_recursive_json_sort(value) for value in json],
                        key=lambda x: x.get(sort_key),
                    )
            return sorted([_recursive_json_sort(value) for value in json])
        if isinstance(json, dict):
            return {key: _recursive_json_sort(json[key]) for key in json}
    return json


def _recursive_json_remove_none(json):
    if json:
        if isinstance(json, list):
            for value in json:
                _recursive_json_remove_none(value)
            return json
        if isinstance(json, dict):
            keys_to_remove = []
            for key, value in json.items():
                if value is None:
                    keys_to_remove.append(key)
                else:
                    _recursive_json_remove_none(value)
            for key in keys_to_remove:
                json.pop(key)
            return json
    return json
