# pylint: disable=E0401
from grocery_mocks import grocery_products as g_products
from grocery_mocks import (  # pylint: disable=E0401
    grocery_menu as mock_grocery_menu,
)
import pytest

from testsuite.utils import ordered_object


PRODUCT_1 = {'id': 'product-1', 'type': 'good'}
PRODUCT_2 = {'id': 'category-2', 'type': 'subcategory'}
PRODUCT_3 = {'id': 'virtual-category-3', 'type': 'virtual_category'}
PRODUCT_4 = {'id': 'product-4', 'type': 'good'}
PRODUCT_5 = {'id': 'virtual-category-5', 'type': 'virtual_category'}
PRODUCT_6 = {'id': 'category-6', 'type': 'subcategory'}
PRODUCT_7 = {'id': 'meta-product-7', 'type': 'combo'}

PRODUCTS_ALL = [
    PRODUCT_1,
    PRODUCT_2,
    PRODUCT_3,
    PRODUCT_4,
    PRODUCT_5,
    PRODUCT_6,
    PRODUCT_7,
]

PRODUCTS_PRODUCT = [PRODUCT_1, PRODUCT_4]

PRODUCTS_CATEGORY = [PRODUCT_2, PRODUCT_6]

PRODUCTS_VIRTUAL_CATEGORY = [PRODUCT_3, PRODUCT_5]

PRODUCTS_COMBOS = [PRODUCT_7]

COMBO_ID = 'meta-product-7'
PRODUCT_GROUP1 = mock_grocery_menu.ProductGroup(True, 1, ['product-8'])
PRODUCT_GROUP2 = mock_grocery_menu.ProductGroup(True, 1, ['product-9'])
PRODUCT_GROUP3 = mock_grocery_menu.ProductGroup(True, 1, ['product-10'])
COMBO_PRODUCT = mock_grocery_menu.ComboProduct(
    'single_selection_combo',
    [COMBO_ID],
    [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
    'combo_revision_1',
)


@pytest.mark.parametrize(
    'filters,results',
    [
        (None, PRODUCTS_ALL),
        ('products', PRODUCTS_PRODUCT),
        ('categories', PRODUCTS_CATEGORY),
        ('virtual_categories', PRODUCTS_VIRTUAL_CATEGORY),
        ('combos', PRODUCTS_COMBOS),
    ],
)
async def test_filter_all(
        taxi_grocery_search,
        overlord_catalog,
        grocery_products,
        grocery_menu,
        filters,
        results,
):
    overlord_catalog.add_product_data(
        product_id=PRODUCT_1['id'], title='products',
    )
    overlord_catalog.add_category_data(
        category_id=PRODUCT_2['id'], title='products',
    )
    grocery_products.add_virtual_category(
        g_products.VirtualCategory(test_id='3', title_tanker_key='products'),
    )
    overlord_catalog.add_product_data(
        product_id=PRODUCT_4['id'], title='products',
    )
    grocery_products.add_virtual_category(
        g_products.VirtualCategory(test_id='5', title_tanker_key='products'),
    )
    overlord_catalog.add_category_data(
        category_id=PRODUCT_6['id'], title='products',
    )
    overlord_catalog.add_product_data(
        product_id=PRODUCT_7['id'], title='products',
    )
    grocery_menu.add_combo_product(COMBO_PRODUCT)

    if not filters:
        params = {'text': 'products'}
    else:
        params = {'text': 'products', 'allowed_items': filters}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == (sorted(item['id'] for item in results))


# при наличие фалага pigeon_data_enabled берет данные из кешей grocery-menu,
# иначе из кешей grocery-products
@pytest.mark.parametrize('pigeon_data_enabled', [True, False, None])
async def test_filter_virtual_categories_by_source(
        taxi_grocery_search, grocery_products, pigeon_data_enabled,
):
    pigeon_prefix = 'pigeon_'
    grocery_products.add_virtual_category(
        g_products.VirtualCategory(
            test_id='1',
            title_tanker_key='products',
            pigeon_id_prefix=pigeon_prefix,
        ),
    )

    params = {
        'text': 'products',
        'allowed_items': ['virtual_categories'],
        **(
            {'pigeon_data_enabled': pigeon_data_enabled}
            if pigeon_data_enabled is not None
            else {}
        ),
    }
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    response_id = 'virtual-category-1'
    if pigeon_data_enabled:
        response_id = pigeon_prefix + response_id

    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == [response_id]


# Находит все документы, у которых в названии есть искомое слово.
@pytest.mark.parametrize(
    'query,answer',
    [
        (
            'word_one',
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'product-2', 'type': 'good'},
                {'id': 'product-3', 'type': 'good'},
            ],
        ),
        (
            'word_two',
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'product-2', 'type': 'good'},
            ],
        ),
        ('word_three', [{'id': 'product-1', 'type': 'good'}]),
    ],
)
async def test_finds_all_products_containing_query_word(
        taxi_grocery_search, overlord_catalog, query, answer,
):
    overlord_catalog.add_product_data(
        product_id='product-1', title='word_one word_two word_three',
    )
    overlord_catalog.add_product_data(
        product_id='product-2', title='word_one word_two',
    )
    overlord_catalog.add_product_data(product_id='product-3', title='word_one')

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json()['search_results'], answer, [''])


# Находит все документы, у которых в названии есть искомое слово.
@pytest.mark.parametrize(
    'query,answer',
    [
        ('word_one', [{'id': 'product-1', 'type': 'good'}]),
        (
            'word_two',
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'category-1', 'type': 'subcategory'},
                {'id': 'virtual-category-1', 'type': 'virtual_category'},
            ],
        ),
        (
            'word_three',
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'virtual-category-1', 'type': 'virtual_category'},
            ],
        ),
    ],
)
@pytest.mark.parametrize('pigeon_data_enabled', [True, False])
async def test_finds_products_and_categories_containing_query_word(
        taxi_grocery_search,
        overlord_catalog,
        grocery_products,
        query,
        answer,
        pigeon_data_enabled,
):
    overlord_catalog.add_product_data(
        product_id='product-1', title='word_one word_two word_three',
    )
    overlord_catalog.add_category_data(
        category_id='category-1', title='word_two',
    )
    grocery_products.add_virtual_category(
        g_products.VirtualCategory(
            test_id='1', title_tanker_key='word_two_word_three_key',
        ),
    )

    params = {'text': query, 'pigeon_data_enabled': pigeon_data_enabled}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json()['search_results'], answer, [''])


# Возвращает документы начиная с offset.
@pytest.mark.parametrize(
    'text,offset,limit,expected_results',
    [
        pytest.param(
            'word_two',
            0,
            2,
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'category-1', 'type': 'subcategory'},
                {'id': 'virtual-category-1', 'type': 'virtual_category'},
            ],
            id='limit < total count',
        ),
        pytest.param(
            'word_two',
            0,
            100,
            [
                {'id': 'product-1', 'type': 'good'},
                {'id': 'category-1', 'type': 'subcategory'},
                {'id': 'virtual-category-1', 'type': 'virtual_category'},
            ],
            id='limit > total count',
        ),
        pytest.param('word_two', 0, 0, [], id='corner case: limit = 0'),
        pytest.param(
            'word_two', 100, 2, [], id='corner case: offset > total count',
        ),
    ],
)
async def test_returns_from_offset(
        taxi_grocery_search,
        overlord_catalog,
        grocery_products,
        text,
        offset,
        limit,
        expected_results,
):
    overlord_catalog.add_product_data(
        product_id='product-1', title='word_one word_two word_three',
    )
    overlord_catalog.add_category_data(
        category_id='category-1', title='word_two',
    )
    grocery_products.add_virtual_category(
        g_products.VirtualCategory(
            test_id='1', title_tanker_key='word_two_word_three_key',
        ),
    )

    results = []
    cursor = offset

    while True:
        response = await taxi_grocery_search.get(
            '/internal/v1/search/v2/search',
            params={'text': text, 'offset': cursor, 'limit': limit},
        )
        assert response.status_code == 200
        search_results = response.json()['search_results']
        if not search_results:
            break
        results.extend(search_results)
        cursor = cursor + limit

    ordered_object.assert_eq(results, expected_results, [''])


# Находит все документы, у которых в названии есть слово, начинающееся с
# искомого.
@pytest.mark.parametrize(
    'query,answer',
    [
        ('word', ['product-1', 'product-2', 'product-3', 'product-4']),
        ('anoth', ['product-4']),
    ],
)
async def test_finds_all_products_containing_query_word_as_a_prefix(
        taxi_grocery_search, overlord_catalog, load_json, query, answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == sorted(answer)


# Находит документы по запросу с опечатками.
@pytest.mark.parametrize(
    'query,answer',
    [
        ('ward', ['product-1', 'product-2', 'product-3', 'product-4']),
        ('anth', ['product-4']),
    ],
)
async def test_finds_fuzzy_matches(
        taxi_grocery_search, overlord_catalog, load_json, query, answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == sorted(answer)


# Лучшие совпадения выше в поисковой выдече.
@pytest.mark.parametrize(
    'query,better_answer',
    [
        pytest.param('ward anth', 'product-4', id='two fuzzy prefix matches'),
        pytest.param('ward some', 'product-1', id='two prefix matches'),
        pytest.param('word', 'product-4', id='exact match'),
    ],
)
async def test_better_matches_are_ranked_higher(
        taxi_grocery_search, overlord_catalog, load_json, query, better_answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert response.json()['search_results'][0]['id'] == better_answer


# Ищет на русском.
@pytest.mark.parametrize(
    'query,better_answer',
    [
        pytest.param('АБЫР', 'product-russian', id='case insensitive'),
        pytest.param('матрЁшка', 'product-yo', id='Ё'),
    ],
)
async def test_russian(
        taxi_grocery_search, overlord_catalog, load_json, query, better_answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert response.json()['search_results'][0]['id'] == better_answer


# Особые символы игнорируются.
@pytest.mark.parametrize(
    'query,better_answer',
    [pytest.param('«« «« «« «АБЫР» »» »» »»', 'product-russian', id='quotes')],
)
async def test_special_symbols(
        taxi_grocery_search, overlord_catalog, load_json, query, better_answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert response.json()['search_results'][0]['id'] == better_answer


# проверяем замену символов из конфига
# GROCERY_SEARCH_SYMBOL_REPLACEMENT_RULES
async def test_search_replace_dot_symbol(
        taxi_grocery_search, overlord_catalog,
):
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'product-yo-description',
                'image_url_template': 'product-yo-image-url-template',
                'long_title': 'яндекс.станция',
                'product_id': 'yandex-station',
                'title': 'яндекс.станция',
            },
        ],
    )

    params = {'text': 'станция'}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert response.json()['search_results'] == [
        {'id': 'yandex-station', 'type': 'good'},
    ]


# При редакционном расстоянии, превышающим все слова индекса, находит все
# документы.
async def test_big_distance(taxi_grocery_search, overlord_catalog, load_json):
    products_data = load_json('overlord_catalog_products_data.json')
    overlord_catalog.add_products_data(new_products_data=products_data)

    params = {'text': 'qwerty', 'distance': 100500}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == sorted([item['product_id'] for item in products_data])


# Находит товар, даже если искомое слово есть только в описании его категорий.
@pytest.mark.parametrize(
    'query,answer',
    [
        pytest.param('categ', 'category-1', id='english category zone'),
        pytest.param('кате', 'category-2', id='russian category zone'),
    ],
)
async def test_finds_category(
        taxi_grocery_search, overlord_catalog, load_json, query, answer,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_links(
        new_products_links=load_json('overlord_catalog_products_links.json'),
    )
    overlord_catalog.add_categories_data(
        new_categories_data=load_json('overlord_catalog_categories_data.json'),
    )

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['search_results']] == [
        answer,
    ]


# С помощью конфига можно выставлять веса зон.
@pytest.mark.config(
    GROCERY_SEARCH_ZONE_WEIGHTS=[{'zone': 'product_title', 'weight': 100.0}],
)
async def test_configure_zone_weights(
        taxi_grocery_search, overlord_catalog, load_json,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': 'матр', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert response.json()['debug_info'] == [
        {
            'factors': 'weight: 50.00, exact_matches: 0',
            'id': 'product-yo',
            'text': 'Матрешки',
            'type': 'good',
        },
    ]


# С помощью конфига можно выставлять формулу вычисления
# итогового веса по зонам.
@pytest.mark.config(GROCERY_SEARCH_ZONE_FORMULA='sum')
@pytest.mark.config(
    GROCERY_SEARCH_ZONE_ENABLED=['product_title', 'product_tags'],
)
@pytest.mark.config(
    GROCERY_SEARCH_ZONE_WEIGHTS=[
        {'zone': 'product_title', 'weight': 1.0},
        {'zone': 'product_tags', 'weight': 1.0},
    ],
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_TAGS={
        'products-keyset': 'wms_items',
        'categories-keyset': 'wms_items',
        'product-suffix': '_synonyms',
        'category-suffix': '_synonyms',
        'delimiter': ',',
    },
)
@pytest.mark.translations(
    wms_items={'product-sum-weight_synonyms': {'ru': 'хлеб'}},
)
async def test_configure_zone_formula(
        taxi_grocery_search, overlord_catalog, load_json,
):
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'product-sum-weight-description',
                'image_url_template': 'product-sum-weight-image-url-template',
                'product_id': 'product-sum-weight',
                'title': 'хлеб',
                'long_title': 'хлеб',
            },
            {
                'description': 'product-no-sum-weight-description',
                'image_url_template': (
                    'product-no-sum-weight-image-url-template'
                ),
                'product_id': 'product-no-sum-weight',
                'title': 'хлеб',
                'long_title': 'хлеб',
            },
        ],
    )

    params = {'text': 'хле', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['search_results']] == [
        'product-sum-weight',
        'product-no-sum-weight',
    ]


# Находит товары по длинному описанию.
async def test_finds_products_by_long_title(
        taxi_grocery_search, overlord_catalog, load_json,
):
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'product-1-description',
                'image_url_template': 'product-1-image-url-template',
                'product_id': 'product-1',
                'title': 'хлеб',
                'long_title': 'белый',
            },
        ],
    )

    params = {'text': 'белый', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['search_results']] == [
        'product-1',
    ]


# Находит локализованные товары
@pytest.mark.config(
    GROCERY_SEARCH_SUPPORTED_LOCALES=['ru', 'en', 'he'],
    GROCERY_LOCALIZATION_CATEGORIES_KEYSET='wms_items',
    GROCERY_LOCALIZATION_PRODUCT_TITLE={
        'keyset': 'wms_items',
        'suffix': '_title',
    },
    GROCERY_LOCALIZATION_PRODUCT_LONG_TITLE={
        'keyset': 'wms_items',
        'suffix': '_long_title',
    },
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION_SUFFIX='_description',
    GROCERY_LOCALIZATION_CATEGORY_TITLE_SUFFIX='_title',
)
@pytest.mark.parametrize(
    'query,answer',
    [
        pytest.param('Маца', 'localized-product', id='fallback product title'),
        pytest.param('Мatzo', 'localized-product', id='en product title'),
        pytest.param('מצו', 'localized-product', id='he product title'),
        pytest.param(
            'Блокбастер',
            'localized-product',
            id='fallback product long title',
        ),
        pytest.param(
            'Blockbuster', 'localized-product', id='en product long title',
        ),
        pytest.param(
            'בלוקבאסטר', 'localized-product', id='he product long title',
        ),
        pytest.param(
            'Полезно',
            'localized-product-category',
            id='fallback category title',
        ),
        pytest.param(
            'Healthy', 'localized-product-category', id='en category title',
        ),
        pytest.param(
            'בריא', 'localized-product-category', id='he category title',
        ),
    ],
)
async def test_finds_localized_products(
        taxi_grocery_search, overlord_catalog, load_json, query, answer,
):
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'localized product description',
                'image_url_template': 'localized-product-image-url-template',
                'long_title': 'localized product long title',
                'product_id': 'localized-product',
                'title': 'localized product title',
            },
        ],
    )
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': 'localized-product-category',
                'description': 'localized product category description',
                'image_url_template': (
                    'localized-product-category-image-url-template'
                ),
                'title': 'localized product category title',
            },
        ],
    )
    overlord_catalog.add_products_links(
        new_products_links=[
            {
                'categories_ids': ['localized-product-category'],
                'product_id': 'localized-product',
            },
        ],
    )

    params = {'text': query, 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['search_results']] == [
        answer,
    ]


# С помощью конфига можно выставить максимальный размер слова, для которого
# не будет производиться нечёткий поиск.
@pytest.mark.parametrize(
    'query,prefix_length,answer',
    [
        # По одной букве находим вообще всё
        (
            'а',
            0,
            [
                'product-1',
                'product-2',
                'product-3',
                'product-4',
                'product-russian',
                'product-yo',
            ],
        ),
        # По одной букве находим только то, что начинается с этой буквы
        ('а', 1, ['product-russian']),
        # По двум буквам находим всё, что начинается с первой буквы
        ('wq', 1, ['product-1', 'product-2', 'product-3', 'product-4']),
        # Префикс не найден в индексе
        ('wq', 2, []),
    ],
)
async def test_zero_distance_config(
        taxi_grocery_search,
        taxi_config,
        overlord_catalog,
        load_json,
        query,
        prefix_length,
        answer,
):
    taxi_config.set(GROCERY_SEARCH_ZERO_DISTANCE_PREFIX_LENGTH=prefix_length)

    products_data = load_json('overlord_catalog_products_data.json')
    overlord_catalog.add_products_data(new_products_data=products_data)

    params = {'text': query}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert sorted(
        item['id'] for item in response.json()['search_results']
    ) == sorted(answer)


# Находит товары по расширениям
@pytest.mark.parametrize(
    'product_extensions,category_extensions,expected_results',
    [
        pytest.param([], [], [], id='no extensions'),
        pytest.param(
            [{'product_id': 'product-1', 'extension': 'товар'}],
            [],
            ['product-1'],
            id='product extensions',
        ),
        pytest.param(
            [],
            [{'category_id': 'category-1', 'extension': 'товар'}],
            ['category-1'],
            id='category extensions',
        ),
    ],
)
async def test_finds_products_by_extensions(
        taxi_grocery_search,
        taxi_config,
        overlord_catalog,
        product_extensions,
        category_extensions,
        expected_results,
):
    taxi_config.set(
        GROCERY_SEARCH_PRODUCT_TITLE_EXTENSIONS=product_extensions,
        GROCERY_SEARCH_CATEGORY_TITLE_EXTENSIONS=category_extensions,
    )

    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'product description',
                'image_url_template': 'product-image-url-template',
                'long_title': 'product long title',
                'product_id': 'product-1',
                'title': 'product title',
            },
        ],
    )
    overlord_catalog.add_categories_data(
        new_categories_data=[
            {
                'category_id': 'category-1',
                'description': 'category description',
                'image_url_template': 'category-image-url-template',
                'title': 'category title',
            },
        ],
    )
    overlord_catalog.add_products_links(
        new_products_links=[
            {'categories_ids': ['category-1'], 'product_id': 'product-1'},
        ],
    )

    params = {'text': 'товар', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [
        item['id'] for item in response.json()['search_results']
    ] == expected_results


# Находит документы по тэгу
@pytest.mark.config(
    GROCERY_SEARCH_ZONE_ENABLED=['product_title', 'product_tags'],
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_TAGS={
        'products-keyset': 'wms_items',
        'categories-keyset': 'wms_items',
        'product-suffix': '_synonyms',
        'category-suffix': '_synonyms',
        'delimiter': ',',
    },
)
@pytest.mark.translations(wms_items={'product-1_synonyms': {'ru': 'abc,qwe'}})
async def test_finds_products_by_tag(
        taxi_grocery_search, overlord_catalog, load_json,
):
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )

    params = {'text': 'qwe'}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['search_results']] == [
        'product-1',
    ]


# Отфильтровывает документы, найденные по не полностью совпадающему префиксу.
@pytest.mark.parametrize(
    'query, filter_not_equally_matched_prefixes, answer',
    [('wrd', False, [{'id': 'product-1', 'type': 'good'}]), ('wrd', True, [])],
)
async def test_filters_found_by_not_equally_matched_prefix(
        taxi_grocery_search,
        overlord_catalog,
        query,
        filter_not_equally_matched_prefixes,
        answer,
):
    overlord_catalog.add_product_data(product_id='product-1', title='word_one')

    params = {
        'text': query,
        'filter_not_equally_matched_prefixes': (
            filter_not_equally_matched_prefixes
        ),
    }
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json()['search_results'], answer, [''])


# Проверяет, что в индекс не попадают исключенные слова.
@pytest.mark.parametrize(
    'words_black_list,expected_results',
    [
        pytest.param([], ['product-1'], id='not in black list'),
        pytest.param(['без'], [], id='in black list'),
    ],
)
async def test_filter_words_in_index_by_blacklist(
        taxi_grocery_search,
        taxi_config,
        overlord_catalog,
        words_black_list,
        expected_results,
):
    taxi_config.set(GROCERY_SEARCH_WORDS_BLACK_LIST=words_black_list)

    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': (
                    'Молоко без лактозы, 1л. Производитель: "Молочный рай"'
                ),
                'image_url_template': 'image-url-template',
                'long_title': 'Молоко без лактозы, 1л',
                'product_id': 'product-1',
                'title': 'Молоко без лактозы',
            },
        ],
    )

    params = {'text': 'без', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [
        item['id'] for item in response.json()['search_results']
    ] == expected_results


# Проверяет, что из запроса фильтруются исключенные слова.
@pytest.mark.parametrize(
    'words_black_list,expected_results',
    [
        pytest.param([], ['product-1'], id='not in black list'),
        pytest.param(['и'], [], id='in black list'),
    ],
)
async def test_filter_words_in_query_by_blacklist(
        taxi_grocery_search,
        taxi_config,
        overlord_catalog,
        words_black_list,
        expected_results,
):
    taxi_config.set(GROCERY_SEARCH_WORDS_BLACK_LIST=words_black_list)

    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'Икра, 1 кг. Производитель: "Осетр рядом"',
                'image_url_template': 'image-url-template',
                'long_title': 'Икра, 1 кг',
                'product_id': 'product-1',
                'title': 'Икра',
            },
        ],
    )

    params = {'text': 'и', 'debug': True}
    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search', params=params,
    )
    assert response.status_code == 200
    assert [
        item['id'] for item in response.json()['search_results']
    ] == expected_results


async def test_find_combo(taxi_grocery_search, overlord_catalog, grocery_menu):
    overlord_catalog.add_product_data(
        product_id=PRODUCT_7['id'], title='combo',
    )
    grocery_menu.add_combo_product(COMBO_PRODUCT)

    response = await taxi_grocery_search.get(
        '/internal/v1/search/v2/search',
        params={'text': 'combo', 'allowed_items': 'combos'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == 1
    assert response_json['search_results'][0]['id'] == COMBO_ID
    assert response_json['search_results'][0]['type'] == 'combo'
