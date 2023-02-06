import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
}

PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PUBLIC_ID_3 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'
PUBLIC_ID_4 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004'


def init_categories(mock_v1_nomenclature_context):
    apple = conftest.NomenclatureProduct(
        public_id=PUBLIC_ID_1, price=100, nom_id='item_id_1',
    )
    orange = conftest.NomenclatureProduct(
        public_id=PUBLIC_ID_3, price=100, nom_id='item_id_3',
    )
    potato = conftest.NomenclatureProduct(
        public_id=PUBLIC_ID_4, price=100, promo_price=80, nom_id='item_id_4',
    )

    category = conftest.NomenclatureCategory(
        'category_id_1', 'Овощи и фрукты', 1,
    )
    category.add_product(apple)
    category.add_product(orange)
    category.add_product(potato)
    mock_v1_nomenclature_context.add_category(category)


def init_details(
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
):
    mock_nomenclature_v2_details_context.add_product(PUBLIC_ID_1, price=100)
    mock_nomenclature_v2_details_context.add_product(PUBLIC_ID_3, price=100)
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_ID_4, price=100, promo_price=80,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID_1)
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_ID_1, price=100)
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID_3)
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_ID_3, price=100)
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID_4)
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_ID_4, price=80, old_price=100,
    )


def init_mapping(add_place_products_mapping):
    mapping = [
        conftest.ProductMapping(
            origin_id='item_id_1', core_id=1, public_id=PUBLIC_ID_1,
        ),
        conftest.ProductMapping(
            origin_id='item_id_3', core_id=3, public_id=PUBLIC_ID_3,
        ),
        conftest.ProductMapping(
            origin_id='item_id_4', core_id=4, public_id=PUBLIC_ID_4,
        ),
    ]

    add_place_products_mapping(mapping)


def init_discounts(mock_v2_match_discounts_context):
    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_ID_1, promo_product=True,
    )

    mock_v2_match_discounts_context.add_discount_product(
        PUBLIC_ID_3, 'absolute', 3.0,
    )


@pytest.mark.parametrize(
    'has_promo_product',
    [
        pytest.param(True, marks=[experiments.PROMO_PRODUCTS_TEXT_ENABLED]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_NONE]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_DISABLED]),
        pytest.param(False),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
        utils.dynamic_categories_config(discount_enabled=True)
    ),
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_promo_products_text_menu_goods(
        taxi_eats_products,
        mock_v2_match_discounts_context,
        mock_v1_nomenclature_context,
        add_place_products_mapping,
        has_promo_product,
        eats_order_stats,
):
    init_categories(mock_v1_nomenclature_context)
    init_mapping(add_place_products_mapping)
    init_discounts(mock_v2_match_discounts_context)

    request = {'shippingType': 'pickup', 'slug': 'slug', 'category': 1}

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request,
    )

    assert response.status_code == 200

    promo_types = {
        item['id']: item['promoTypes']
        for item in response.json()['payload']['categories'][0]['items']
    }

    if not has_promo_product:
        assert len(promo_types[1]) == 1
        return

    assert promo_types[1][0]['type'] == 'product_promo'
    assert promo_types[1][0]['text'] == '1+1'

    assert promo_types[3][0]['type'] == 'price_discount'
    assert promo_types[3][0]['text'] == '–3%'

    assert promo_types[4][0]['type'] == 'price_discount'
    assert promo_types[4][0]['text'] == '–20%'


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    'has_promo_product',
    [
        pytest.param(True, marks=[experiments.PROMO_PRODUCTS_TEXT_ENABLED]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_NONE]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_DISABLED]),
        pytest.param(False),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
        utils.dynamic_categories_config(discount_enabled=True)
    ),
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='redis_top_products_cache')
@experiments.products_scoring()
async def test_promo_products_text_get_categories(
        taxi_eats_products,
        mockserver,
        mock_v2_match_discounts_context,
        mock_v1_nomenclature_context,
        add_place_products_mapping,
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        has_promo_product,
        eats_order_stats,
):
    init_categories(mock_v1_nomenclature_context)
    init_mapping(add_place_products_mapping)
    init_discounts(mock_v2_match_discounts_context)
    init_details(
        mock_nomenclature_v2_details_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def mock_nomenclature_categories(request):
        return {
            'categories': [{'name': 'category 1', 'public_id': '1'}],
            'products': [],
        }

    mock_nomenclature_get_parent_context.add_category('1')

    request = {
        'slug': 'slug',
        'categories': [{'id': 1, 'min_items_count': 1, 'max_items_count': 5}],
    }
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=request, headers=HEADERS,
    )

    assert response.status_code == 200
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert mock_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert mock_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1

    promo_types = {
        item['id']: item['promoTypes']
        for item in response.json()['categories'][0]['items']
    }

    if not has_promo_product:
        assert len(promo_types[1]) == 1
        return

    assert promo_types[1][0]['type'] == 'product_promo'
    assert promo_types[1][0]['text'] == '1+1'

    assert promo_types[3][0]['type'] == 'price_discount'
    assert promo_types[3][0]['text'] == '–3%'

    assert promo_types[4][0]['type'] == 'price_discount'
    assert promo_types[4][0]['text'] == '–20%'


@pytest.mark.parametrize(
    'has_promo_product',
    [
        pytest.param(True, marks=[experiments.PROMO_PRODUCTS_TEXT_ENABLED]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_NONE]),
        pytest.param(False, marks=[experiments.PROMO_PRODUCTS_TEXT_DISABLED]),
        pytest.param(False),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=(
        utils.dynamic_categories_config(discount_enabled=True)
    ),
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_product_discount_applicator(
        taxi_eats_products,
        mock_v2_match_discounts_context,
        mock_v1_nomenclature_context,
        add_place_products_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        has_promo_product,
        eats_order_stats,
):
    init_categories(mock_v1_nomenclature_context)
    init_mapping(add_place_products_mapping)
    init_discounts(mock_v2_match_discounts_context)
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_ID_1, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID_1)
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_ID_3, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_ID_3)

    request = {'place_slug': 'slug', 'product_public_id': PUBLIC_ID_1}
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    if not has_promo_product:
        assert len(response.json()['menu_item']['promoTypes']) == 1
        return

    promo_types = response.json()['menu_item']['promoTypes']
    assert promo_types[0]['type'] == 'product_promo'
    assert promo_types[0]['text'] == '1+1'
