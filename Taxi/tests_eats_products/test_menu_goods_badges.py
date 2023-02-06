import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {
    'shippingType': 'pickup',
    'slug': 'slug',
    'category': 1,
}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
]


@pytest.mark.parametrize(
    'use_discount_applicator',
    [
        pytest.param(
            True,
            marks=[
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
                experiments.CASHBACK_DISCOUNTS_ENABLED,
            ],
        ),
        False,
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
async def test_menu_goods_badges_discounts(
        taxi_eats_products,
        add_default_product_mapping,
        mock_v1_nomenclature_context,
        mock_v2_match_discounts_context,
        use_discount_applicator,
):
    # Тест проверяет простановку нужных цветов для товаров с ценовой скидкой
    add_default_product_mapping()

    product_10_percent_discount = conftest.NomenclatureProduct(
        public_id=PUBLIC_IDS[0], price=100, nom_id='item_id_3',
    )

    product_promo = conftest.NomenclatureProduct(
        public_id=PUBLIC_IDS[1], price=100, nom_id='item_id_3',
    )

    if use_discount_applicator:
        mock_v2_match_discounts_context.add_discount_product(
            PUBLIC_IDS[0], 'fraction', 10,
        )
        mock_v2_match_discounts_context.add_discount_product(
            PUBLIC_IDS[1], promo_product=True,
        )
    else:
        product_10_percent_discount.promo_price = 90

    fruits = conftest.NomenclatureCategory('category_id_1', 'Фрукты', 1)
    fruits.add_product(product_10_percent_discount)
    fruits.add_product(product_promo)
    mock_v1_nomenclature_context.add_category(fruits)

    response = await utils.get_goods_response(
        taxi_eats_products, PRODUCTS_BASE_REQUEST,
    )
    assert response.status_code == 200

    resp_item_0 = response.json()['payload']['categories'][0]['items'][0]
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(resp_item_0, expected)

    if not use_discount_applicator:
        return

    resp_item_1 = response.json()['payload']['categories'][0]['items'][1]
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['promo_badges'],
    )
    utils.compare_badges(resp_item_1, expected)


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
@experiments.discount_category()
@experiments.products_scoring()
async def test_menu_goods_badges_dynamic_discounts(
        taxi_eats_products,
        setup_nomenclature_handlers_v2,
        add_default_product_mapping,
        cache_add_discount_product,
):
    # выставление цвета в бейдже для динамической категории скидок
    add_default_product_mapping()
    cache_add_discount_product('item_id_1')

    products_request = PRODUCTS_BASE_REQUEST.copy()
    products_request['category'] = utils.DISCOUNT_CATEGORY_ID

    setup_nomenclature_handlers_v2()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=utils.PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    categories = response.json()['payload']['categories']
    assert len(categories) == 1

    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )

    for category in categories:
        assert category
        assert category['items']
        for item in category['items']:
            utils.compare_badges(item, expected)


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
    ),
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_menu_goods_badges_dynamic_repeat(
        taxi_eats_products,
        add_default_product_mapping,
        handlers_version,
        setup_nomenclature_handlers_v2,
        mock_nomenclature_v2_details_context,
        mock_retail_categories_brand_orders_history,
):
    # выставление цвета в бейдже для динамической категории "вы заказывали"
    add_default_product_mapping()
    products_request = PRODUCTS_BASE_REQUEST.copy()
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    if handlers_version == 'v2':
        setup_nomenclature_handlers_v2()
    else:
        mock_nomenclature_v2_details_context.add_product(
            PUBLIC_IDS[0], promo_price=90,
        )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=utils.PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1

    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(categories[0]['items'][0], expected)


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        popular_enabled=True,
    ),
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@experiments.products_scoring()
async def test_menu_goods_badges_dynamic_popular(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_v2_details_context,
):
    # выставление цвета в бейдже для динамической категории "популярное"
    add_default_product_mapping()
    products_request = PRODUCTS_BASE_REQUEST.copy()
    products_request['category'] = utils.POPULAR_CATEGORY_ID

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[0], promo_price=90,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=utils.PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1

    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(categories[0]['items'][0], expected)


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        popular_enabled=True, cashback_enabled=True,
    ),
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.products_scoring()
async def test_menu_goods_badges_dynamic_cashback(
        taxi_eats_products,
        mock_v2_fetch_discounts_context,
        add_default_product_mapping,
        mock_nomenclature_v2_details_context,
):
    # выставление цвета в бейдже для динамической категории "кешбек"
    add_default_product_mapping()
    products_request = PRODUCTS_BASE_REQUEST.copy()
    products_request['category'] = utils.CASHBACK_CATEGORY_ID

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[0], promo_price=90,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=utils.PRODUCTS_HEADERS,
    )

    assert response.status_code == 200

    categories = response.json()['payload']['categories']
    assert len(categories) == 1

    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(categories[0]['items'][0], expected)
