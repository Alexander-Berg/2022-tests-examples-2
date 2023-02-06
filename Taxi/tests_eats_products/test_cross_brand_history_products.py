import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

EATER_ID = '123'
HEADERS = {'X-Eats-User': f'user_id={EATER_ID}'}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
]

SKU_IDS = ['1', '2', '3', '4', '5']

THIS_PLACE_ID = str(utils.PLACE_ID)
OTHER_PLACE_ID = '2'

HAS_HISTORY_BRANDS = ['set', f'has_history:{EATER_ID}:brands', '1']
HAS_CROSS_BRANDS_HISTORY = ['set', f'has_history:{EATER_ID}:cross_brands', '1']


PRICE_DISCOUNT = {
    'id': 25,
    'name': 'Скидка для магазинов.',
    'pictureUri': (
        'https://avatars.mds.yandex.net/get-eda/1370147/5b73e9ea19587/80x80'
    ),
    'text': '–50%',
    'badgeColor': [
        {'theme': 'light', 'value': '#100002'},
        {'theme': 'dark', 'value': '#100003'},
    ],
    'textColor': [
        {'theme': 'light', 'value': '#100000'},
        {'theme': 'dark', 'value': '#100001'},
    ],
    'type': 'price_discount',
}

CHEAPER_HERE = {
    'id': 0,
    'name': 'Здесь дешевле',
    'badgeColor': [
        {'theme': 'light', 'value': '#00013'},
        {'theme': 'dark', 'value': '#00014'},
    ],
    'textColor': [
        {'theme': 'light', 'value': '#00011'},
        {'theme': 'dark', 'value': '#00012'},
    ],
    'type': 'product_promo',
}

MIN_PRODUCT_PRICE = 100


@experiments.cross_brand_history()
async def test_cross_brand_products_404_place_not_found(taxi_eats_products):
    # Проверяется, что если выбранный магазн не найден, вернется 404
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['unknown_shop'],
            'selected_place': {
                'place_slug': 'unknown_shop',
                'brand_name': '1',
            },
        },
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'place_not_found',
        'message': 'Selected place not found in cache',
    }


async def test_cross_brand_products_404_config_not_found(taxi_eats_products):
    # Проверяется, что при отстутствии конфига верентся 404
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug'],
            'selected_place': {'place_slug': 'slug', 'brand_name': '1'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'other',
        'message': 'Cross brand history config not found',
    }


@experiments.cross_brand_history()
async def test_cross_brand_products_404_places_not_found(taxi_eats_products):
    # Проверяется, что если запрошенных магазинов нет в кэше, вернется 404
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['unknown_shop1', 'unknown_shop2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': '1'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'place_not_found',
        'message': 'No places found in cache from available_places_slugs',
    }


@experiments.cross_brand_history()
@pytest.mark.parametrize('headers', [{}, {'X-Eats-User': 'user_id='}])
async def test_cross_brand_products_401_no_eater_id(
        taxi_eats_products, headers,
):
    # Проверяется, что ручку нельзя вызвать без авторизации пользователя
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug'],
            'selected_place': {'place_slug': 'slug', 'brand_name': '1'},
        },
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@experiments.cross_brand_history()
async def test_cross_brand_products_empty_response(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    """
    Проверяется, что при отсутствии товаров в ответе retail-categories
    вернется пустой ответ
    """
    public_ids = PUBLIC_IDS[:2]
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_ids[0],
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=public_ids[1],
            ),
        ],
    )
    for public_id in public_ids:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug'],
            'selected_place': {'place_slug': 'slug', 'brand_name': '1'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'categories': []}
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.parametrize(
    ['selected_slug', 'expected_response'],
    [
        ('slug', 'expected_slug_response.json'),
        ('slug2', 'expected_slug2_response.json'),
    ],
)
@experiments.cross_brand_history()
async def test_cross_brand_products_both_categories(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_place_products_mapping,
        load_json,
        make_public_by_sku_id_response,
        mockserver,
        selected_slug,
        expected_response,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что будут возвращены подкатегории "Только в этом магазине"
    # и "Не только в этом магазине" с товарами с распределением
    # по подкатегориям и недоступных товаров нет в ответе
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)

    mapping = []
    for i in range(4):
        origin_id = f'item_id_{i}'
        core_id = i + 1
        mapping.append(
            conftest.ProductMapping(origin_id, core_id, PUBLIC_IDS[i]),
        )
    add_place_products_mapping(mapping, utils.PLACE_ID, 1)
    mapping = [
        conftest.ProductMapping('item_id_5', 5, PUBLIC_IDS[4]),
        conftest.ProductMapping('item_id_6', 6, PUBLIC_IDS[5]),
        conftest.ProductMapping('item_id_7', 7, PUBLIC_IDS[6]),
    ]
    add_place_products_mapping(mapping, 2, 2)
    is_available = [True, True, False, True, True, False, True]
    # SKU_IDS[3] недоступен в магазине slug2 ->
    # в магазине slug товар попадет в категорию "Только здесь"
    # SKU_IDS[1] есть в обоих магазинах -> товары с PUBLIC_IDS[1]
    # и PUBLIC_IDS[6] будут категории "Не только здесь"
    for i in range(7):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], is_available=is_available[i],
        )

    place_sku_to_public_ids = {
        THIS_PLACE_ID: {
            SKU_IDS[0]: [PUBLIC_IDS[0]],
            SKU_IDS[1]: [PUBLIC_IDS[1]],
            SKU_IDS[2]: [PUBLIC_IDS[2]],
            SKU_IDS[3]: [PUBLIC_IDS[3]],
        },
        OTHER_PLACE_ID: {
            SKU_IDS[1]: [PUBLIC_IDS[4]],
            SKU_IDS[3]: [PUBLIC_IDS[5]],
            SKU_IDS[4]: [PUBLIC_IDS[6]],
        },
    }

    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[0], 1,
    )

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[1], 5, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[2], 1, SKU_IDS[2],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[3], 5, SKU_IDS[3],
    )

    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), PUBLIC_IDS[4], 5, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), PUBLIC_IDS[5], 5, SKU_IDS[3],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), PUBLIC_IDS[6], 1, SKU_IDS[4],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {
                'place_slug': selected_slug,
                'brand_name': 'Ашан',
            },
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@experiments.cross_brand_history()
@pytest.mark.parametrize('handler_404', ['dynamic', 'static'])
async def test_cross_brand_products_404_nomenclature(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        handler_404,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что если ручки номенклатуры вернули 404,
    # то и в ответе будет 404
    public_id = PUBLIC_IDS[0]

    add_default_product_mapping()
    if handler_404 == 'static':
        mock_nomenclature_static_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_static_info_context.add_product(public_id)
    if handler_404 == 'dynamic':
        mock_nomenclature_dynamic_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': '1'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'names',
    [
        pytest.param(
            ['Только здесь', 'Не только в Ашан'],
            marks=experiments.cross_brand_history(
                this_brand_category_name='Только здесь',
                other_brands_category_name='Не только в {brand}',
            ),
        ),
        pytest.param(
            ['Только в Ашан', 'Не только здесь'],
            marks=experiments.cross_brand_history(
                this_brand_category_name='Только в {brand}',
                other_brands_category_name='Не только здесь',
            ),
        ),
    ],
)
async def test_cross_brand_products_categories_names(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        mockserver,
        names,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что подкатегории будут иметь верные имена
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)

    public_ids = PUBLIC_IDS[:2]
    add_default_product_mapping()
    for public_id in public_ids:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    place_sku_to_public_ids = {
        THIS_PLACE_ID: {
            SKU_IDS[0]: [public_ids[0]],
            SKU_IDS[1]: [public_ids[1]],
        },
        OTHER_PLACE_ID: {SKU_IDS[1]: [public_ids[1]]},
    }

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), public_ids[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), public_ids[1], 5, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), public_ids[1], 5, SKU_IDS[1],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': 'Ашан'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 2
    assert [category['title'] for category in categories] == names
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.parametrize(
    ['expected_category_title', 'skus'],
    [
        pytest.param(
            'Только в Ашан', {SKU_IDS[1]: [PUBLIC_IDS[4]]}, id='only_here',
        ),
        pytest.param(
            'Не только в Ашан', {SKU_IDS[0]: [PUBLIC_IDS[4]]}, id='elsewhere',
        ),
    ],
)
@experiments.cross_brand_history()
async def test_cross_brand_products_only_one_category(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        mockserver,
        expected_category_title,
        skus,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что будет возвращена только одна из категорий
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)

    add_default_product_mapping()
    for public_id in PUBLIC_IDS:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    place_sku_to_public_ids = {
        THIS_PLACE_ID: {SKU_IDS[0]: [PUBLIC_IDS[0]]},
        OTHER_PLACE_ID: skus,
    }

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    mock_retail_categories_cross_brand_orders.add_product(
        int(OTHER_PLACE_ID), PUBLIC_IDS[4], 2, list(skus.keys())[0],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': 'Ашан'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 1
    assert categories[0]['title'] == expected_category_title

    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@experiments.cross_brand_history()
async def test_cross_brand_products_mixed_with_brand(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        mockserver,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что товары из брендовой истории заказа
    # замешиваются с кросс брендовыми
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)

    add_default_product_mapping()
    for public_id in PUBLIC_IDS:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    place_sku_to_public_ids = {
        THIS_PLACE_ID: {SKU_IDS[0]: [PUBLIC_IDS[0]]},
        OTHER_PLACE_ID: {SKU_IDS[0]: [PUBLIC_IDS[4]]},
    }

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    mock_retail_categories_brand_orders_history.add_brand_product(
        1, PUBLIC_IDS[1], 2,
    )

    mock_retail_categories_cross_brand_orders.add_product(
        int(THIS_PLACE_ID), PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2'],
            'selected_place': {'place_slug': 'slug', 'brand_name': 'Ашан'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['categories']
    assert len(categories) == 2
    assert [product['id'] for product in categories[0]['products']] == [2]
    assert [product['id'] for product in categories[1]['products']] == [1]
    assert mock_retail_categories_brand_orders_history.times_called == 1


@pytest.mark.parametrize(
    'promo_cheaper_here_enabled',
    [
        pytest.param(
            False,
            marks=experiments.cross_brand_history(),
            id='promo_cheaper_here_disabled',
        ),
        pytest.param(
            True,
            marks=experiments.cross_brand_history(
                promo_cheaper_here={
                    'name': 'Здесь дешевле',
                    'promo_badges': {
                        'text': [
                            {'theme': 'light', 'value': '#00011'},
                            {'theme': 'dark', 'value': '#00012'},
                        ],
                        'background': [
                            {'theme': 'light', 'value': '#00013'},
                            {'theme': 'dark', 'value': '#00014'},
                        ],
                    },
                },
            ),
            id='promo_cheaper_here_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'price_discount_enabled',
    [
        pytest.param(False, id='price_discount_disabled'),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
                    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
                ),
            ],
            id='price_discount_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'prices, is_set_promo_cheaper_here',
    [
        pytest.param([MIN_PRODUCT_PRICE, 200, 150], True),
        pytest.param([200, MIN_PRODUCT_PRICE, 150], True),
        pytest.param([MIN_PRODUCT_PRICE, MIN_PRODUCT_PRICE, 200], True),
        pytest.param(
            [MIN_PRODUCT_PRICE, MIN_PRODUCT_PRICE, MIN_PRODUCT_PRICE], False,
        ),
    ],
)
async def test_cross_brand_products_promo_cheaper_here(
        taxi_eats_products,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        mockserver,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
        promo_cheaper_here_enabled,
        prices,
        is_set_promo_cheaper_here,
        price_discount_enabled,
):
    """
        Проверяется выставление промо "Здесь дешевле"
        для товаров с cross-brand
    """
    sql_add_brand(brand_id=2, brand_slug='brand2')
    sql_add_place(place_id=2, place_slug='slug2', brand_id=2)

    sql_add_brand(brand_id=3, brand_slug='brand3')
    sql_add_place(place_id=3, place_slug='slug3', brand_id=3)

    product_1 = PUBLIC_IDS[0]
    product_2 = PUBLIC_IDS[1]
    product_3 = PUBLIC_IDS[2]

    add_default_product_mapping()

    mock_nomenclature_static_info_context.add_product(product_1)
    mock_nomenclature_dynamic_info_context.add_product(
        product_1,
        price=prices[0],
        old_price=(prices[0] * 2 if price_discount_enabled else None),
    )

    mock_nomenclature_static_info_context.add_product(product_2)
    mock_nomenclature_dynamic_info_context.add_product(
        product_2,
        price=prices[1],
        old_price=(prices[1] * 2 if price_discount_enabled else None),
    )

    mock_nomenclature_static_info_context.add_product(product_3)
    mock_nomenclature_dynamic_info_context.add_product(
        product_3,
        price=prices[2],
        old_price=(prices[2] * 2 if price_discount_enabled else None),
    )

    third_place_id = '3'
    place_sku_to_public_ids = {
        THIS_PLACE_ID: {SKU_IDS[0]: [product_1]},
        OTHER_PLACE_ID: {SKU_IDS[0]: [product_2]},
        third_place_id: {SKU_IDS[0]: [product_3]},
    }

    mock_retail_categories_cross_brand_orders.add_product(
        place_id=int(THIS_PLACE_ID),
        public_id=product_1,
        orders_count=2,
        sku_id=SKU_IDS[0],
    )

    mock_retail_categories_cross_brand_orders.add_product(
        place_id=int(THIS_PLACE_ID),
        public_id=product_2,
        orders_count=2,
        sku_id=SKU_IDS[0],
    )

    mock_retail_categories_cross_brand_orders.add_product(
        place_id=int(THIS_PLACE_ID),
        public_id=product_3,
        orders_count=1,
        sku_id=SKU_IDS[0],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PRODUCTS,
        json={
            'available_places_slugs': ['slug', 'slug2', 'slug3'],
            'selected_place': {'place_slug': 'slug', 'brand_name': 'Ашан'},
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    products = response.json()['categories'][0]['products']

    assert len(products) == 3
    for product in products:
        expected = []
        if price_discount_enabled:
            expected.append(PRICE_DISCOUNT)

        if (
                promo_cheaper_here_enabled
                and is_set_promo_cheaper_here
                and product['price']
                == (
                    MIN_PRODUCT_PRICE * 2
                    if price_discount_enabled
                    else MIN_PRODUCT_PRICE
                )
        ):
            expected.append(CHEAPER_HERE)

        assert product['promoTypes'] == expected
