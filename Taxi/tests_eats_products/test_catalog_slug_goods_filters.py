import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {
    'slug': 'slug',
    'shippingType': 'pickup',
    'maxDepth': 3,
}

UI_STRINGS = {
    'name': 'Бренд',
    'popular': 'Популярное',
    'all': 'Все',
    'done': 'Готово',
    'reset': 'Сбросить',
    'show': 'Показать',
}

EXPECTED_FILTERS = {
    101: [
        {
            'is_applied': False,
            'query': 'brand',
            'type': 'multiselect',
            'top_values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B3',
                    'query': '48bbb09c878309b30ad66679913b4751',
                    'goods_count': '3',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '2',
                    'is_available': True,
                },
            ],
            'values': [
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '2',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'name': 'B2',
                    'query': '8c735097522dbc0cde888b6d430f0afe',
                    'goods_count': '1',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B3',
                    'query': '48bbb09c878309b30ad66679913b4751',
                    'goods_count': '3',
                    'is_available': True,
                },
            ],
            'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 1'},
        },
    ],
    102: [
        {
            'is_applied': False,
            'query': 'brand',
            'type': 'multiselect',
            'top_values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B3',
                    'query': '48bbb09c878309b30ad66679913b4751',
                    'goods_count': '3',
                    'is_available': True,
                },
            ],
            'values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B3',
                    'query': '48bbb09c878309b30ad66679913b4751',
                    'goods_count': '3',
                    'is_available': True,
                },
            ],
            'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
        },
    ],
    103: [
        {
            'is_applied': False,
            'query': 'brand',
            'type': 'multiselect',
            'top_values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '2',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B2',
                    'query': '8c735097522dbc0cde888b6d430f0afe',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '2',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B2',
                    'query': '8c735097522dbc0cde888b6d430f0afe',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
        },
    ],
    104: [
        {
            'is_applied': False,
            'query': 'brand',
            'type': 'multiselect',
            'top_values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
        },
    ],
}


def get_nomenclature_response(load_json, category_indices):
    nomenclature_response = load_json(
        f'nomenclature-category-{category_indices[0]}.json',
    )
    for category_id in category_indices[1:]:
        category = load_json(f'nomenclature-category-{category_id}.json')[
            'categories'
        ]
        nomenclature_response['categories'] += category
    return nomenclature_response


PARAMETRIZE_INTEGRATION_VERSION = pytest.mark.parametrize(
    'nmn_integration_version', ['v1', 'v2'],
)


@PARAMETRIZE_INTEGRATION_VERSION
async def test_filters_exp_disabled(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    for cat in categories:
        assert 'filters' not in cat


@PARAMETRIZE_INTEGRATION_VERSION
@experiments.filters_settings()
async def test_no_filters_on_top_level(
        mock_nomenclature_for_v2_menu_goods, nmn_integration_version,
):
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    cat_2 = conftest.CategoryMenuGoods(
        public_id='2', name='name', origin_id='origin_id',
    )
    root_cat.add_child_category(cat_2)
    cat_3 = conftest.CategoryMenuGoods(
        public_id='3', name='name', origin_id='origin_id',
    )
    root_cat.add_child_category(cat_3)
    cat_4 = conftest.CategoryMenuGoods(
        public_id='4', name='name', origin_id='origin_id',
    )
    cat_3.add_child_category(cat_4)
    place.add_root_category(root_cat)
    mock_nomenclature_context.set_place(place)

    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST, integration_version=nmn_integration_version,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    for cat in categories:
        assert 'filters' not in cat


@experiments.filters_settings()
async def test_get_filters(taxi_eats_products, mockserver, load_json):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return get_nomenclature_response(load_json, [1, 2, 3, 4, 5])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    filters = {c['id']: c['filters'] for c in categories if 'filters' in c}
    assert filters == EXPECTED_FILTERS


@pytest.mark.experiments3(filename='filters_settings_experiment_strict.json')
async def test_get_filters_strict(taxi_eats_products, mockserver, load_json):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 6

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return get_nomenclature_response(load_json, [6, 7, 8])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    filters = {c['id']: c['filters'] for c in categories if 'filters' in c}
    assert filters == {}


B2_BLAKE = '8c735097522dbc0cde888b6d430f0afe'  # blake2(B2)


@pytest.mark.parametrize(
    ('filters', 'expected_items'),
    (
        (
            {'brand': [B2_BLAKE]},
            {101: [], 103: ['public_id_9']},  # 101 is the parent of 103
        ),
        ({'brand': []}, {}),
    ),
)
@experiments.filters_settings()
async def test_filter_by_brand_hierarchy(
        taxi_eats_products,
        mockserver,
        load_json,
        filters,
        expected_items,
        add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_8', core_id=8, public_id='public_id_8',
            ),
            conftest.ProductMapping(
                origin_id='item_id_9', core_id=9, public_id='public_id_9',
            ),
        ],
    )
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['filters'] = filters

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return get_nomenclature_response(load_json, [1, 2, 3, 4, 5])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    goods_in_cats = {
        c['id']: [i['public_id'] for i in c['items']] for c in categories
    }
    assert goods_in_cats == expected_items


@pytest.mark.parametrize(
    'expected_result',
    [
        pytest.param(
            {
                101: [],
                103: ['public_id_8', 'public_id_9'],
                104: ['public_id_1'],
            },
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_BRAND_CLEANSING={
                        'substitutions': [{'from': 'B1', 'to': 'B2'}],
                    },
                ),
            ],
            id='substitute B1 -> B2',
        ),
        pytest.param({101: [], 103: ['public_id_9']}, id='no substitutions'),
    ],
)
@experiments.filters_settings()
async def test_filter_brand_cleansing(
        taxi_eats_products,
        mockserver,
        load_json,
        expected_result,
        add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id='public_id_1',
            ),
            conftest.ProductMapping(
                origin_id='item_id_8', core_id=8, public_id='public_id_8',
            ),
            conftest.ProductMapping(
                origin_id='item_id_9', core_id=9, public_id='public_id_9',
            ),
        ],
    )
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['filters'] = {'brand': [B2_BLAKE]}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return get_nomenclature_response(load_json, [1, 2, 3, 4, 5])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']
    goods_in_cats = {
        c['id']: [i['public_id'] for i in c['items']] for c in categories
    }
    assert goods_in_cats == expected_result


@experiments.filters_settings()
async def test_filter_by_brand_applied(
        taxi_eats_products, mockserver, load_json,
):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1
    products_request['filters'] = {'brand': [B2_BLAKE]}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return get_nomenclature_response(load_json, [1, 2, 3, 4, 5])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    resp_json = response.json()['payload']
    categories = resp_json['categories']

    for cat in categories:
        for filter_ in cat['filters']:
            assert filter_['is_applied']
            for value in filter_['values']:
                if value['query'] == B2_BLAKE:
                    assert value['is_applied']
                else:
                    assert not value['is_applied']

            assert filter_['top_values'][0]['query'] == B2_BLAKE

            for value in filter_['top_values']:
                if value['query'] == B2_BLAKE:
                    assert value['is_applied']
                else:
                    assert not value['is_applied']


@pytest.mark.parametrize(
    'expected_filters_on_root_category',
    [
        pytest.param(
            [
                {
                    'is_applied': False,
                    'query': 'brand',
                    'type': 'multiselect',
                    'top_values': [
                        {
                            'is_applied': False,
                            'top_index': 0,
                            'name': 'B2',
                            'query': '8c735097522dbc0cde888b6d430f0afe',
                            'goods_count': '1',
                            'is_available': True,
                        },
                    ],
                    'values': [
                        {
                            'is_applied': False,
                            'top_index': 0,
                            'name': 'B2',
                            'query': '8c735097522dbc0cde888b6d430f0afe',
                            'goods_count': '1',
                            'is_available': True,
                        },
                    ],
                    'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
                },
            ],
            id='no substitutions',
        ),
        pytest.param(
            [
                {
                    'is_applied': False,
                    'query': 'brand',
                    'type': 'multiselect',
                    'top_values': [
                        {
                            'is_applied': False,
                            'top_index': 0,
                            'name': 'B2',
                            'query': '8c735097522dbc0cde888b6d430f0afe',
                            'goods_count': '2',
                            'is_available': True,
                        },
                    ],
                    'values': [
                        {
                            'is_applied': False,
                            'top_index': 0,
                            'name': 'B2',
                            'query': '8c735097522dbc0cde888b6d430f0afe',
                            'goods_count': '2',
                            'is_available': True,
                        },
                    ],
                    'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
                },
            ],
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_BRAND_CLEANSING={
                        'substitutions': [{'from': '123', 'to': 'B2'}],
                    },
                ),
            ),
            id='substitute only digits -> NOT only digits',
        ),
    ],
)
@experiments.filters_settings()
async def test_brands_consist_of_digits(
        taxi_eats_products,
        mockserver,
        load_json,
        expected_filters_on_root_category,
):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        response = get_nomenclature_response(load_json, [1, 3])
        # changed item_id_8`s brand from brand = 'B1'
        # to brand consisting of only digits ('123')
        response['categories'][1]['items'][0]['brand'] = '123'
        return response

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    filters = {c['id']: c['filters'] for c in categories if 'filters' in c}
    assert filters[101] == expected_filters_on_root_category


@pytest.mark.parametrize(
    'brand',
    [
        pytest.param('B1', id='no spaces'),
        pytest.param('  B1  ', id='with spaces'),
    ],
)
@experiments.filters_settings()
async def test_trimming_brands(
        taxi_eats_products, mockserver, load_json, brand,
):
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 1

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        response = get_nomenclature_response(load_json, [1, 3])
        response['categories'][1]['items'][0]['brand'] = brand
        return response

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    assert response.status_code == 200

    expected_filter = [
        {
            'is_applied': False,
            'query': 'brand',
            'type': 'multiselect',
            'top_values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '1',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B2',
                    'query': '8c735097522dbc0cde888b6d430f0afe',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'values': [
                {
                    'is_applied': False,
                    'top_index': 0,
                    'name': 'B1',
                    'query': '8cba3d5400f67d313d2744f0f3e52a7a',
                    'goods_count': '1',
                    'is_available': True,
                },
                {
                    'is_applied': False,
                    'top_index': 1,
                    'name': 'B2',
                    'query': '8c735097522dbc0cde888b6d430f0afe',
                    'goods_count': '1',
                    'is_available': True,
                },
            ],
            'ui_strings': {**UI_STRINGS, 'show_all': 'Еще 0'},
        },
    ]
    categories = response.json()['payload']['categories']
    filters = {c['id']: c['filters'] for c in categories if 'filters' in c}
    assert filters[101] == expected_filter


PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PUBLIC_ID_2 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'


@pytest.mark.parametrize(
    'expected_items',
    [
        pytest.param(set([PUBLIC_ID_1, PUBLIC_ID_2])),
        pytest.param(
            set([PUBLIC_ID_2]),
            marks=pytest.mark.config(
                EATS_PRODUCTS_SETTINGS={
                    'hide_product_public_ids': [PUBLIC_ID_1],
                },
            ),
        ),
    ],
)
async def test_menu_goods_hide_product_public_ids(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        add_place_products_mapping,
        expected_items,
):
    """
    Тест проверяет, что в ручке menu/goods скрываются товары по конфигу
    EATS_PRODUCTS_SETTINGS.hide_product_public_ids
    """
    core_id_1 = 1
    core_id_2 = 2
    origin_1 = 'item_id_1'
    origin_2 = 'item_id_2'
    mapping = [
        conftest.ProductMapping(
            origin_id=origin_1, core_id=core_id_1, public_id=PUBLIC_ID_1,
        ),
        conftest.ProductMapping(
            origin_id=origin_2, core_id=core_id_2, public_id=PUBLIC_ID_2,
        ),
    ]
    add_place_products_mapping(mapping)
    category = conftest.NomenclatureCategory(
        'category_id_1', 'Фрукты', public_id=1,
    )
    category.add_product(
        conftest.NomenclatureProduct(
            PUBLIC_ID_1, price=100, nom_id='item_id_1',
        ),
    )
    category.add_product(
        conftest.NomenclatureProduct(
            PUBLIC_ID_2, price=100, nom_id='item_id_2',
        ),
    )
    mock_v1_nomenclature_context.add_category(category)

    request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    request['category'] = 1
    request['slug'] = 'slug'
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request,
    )
    assert response.status_code == 200

    items = {
        item['public_id']
        for item in response.json()['payload']['categories'][0]['items']
    }
    assert items == expected_items
