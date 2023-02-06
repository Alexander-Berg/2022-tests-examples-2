# pylint: disable=too-many-lines
import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

EATER_ID = '12345'
PRODUCTS_HEADERS = {
    'X-Eats-User': f'user_id={EATER_ID}',
    'X-AppMetrica-DeviceId': 'device_id',
}


REPEAT_CATEGORIES_CONFIG = {
    'discount': {
        'enabled': False,
        'id': utils.DISCOUNT_CATEGORY_ID,
        'name': 'Скидки',
    },
    'popular': {
        'enabled': False,
        'id': utils.POPULAR_CATEGORY_ID,
        'name': 'Популярное',
    },
    'repeat': {
        'enabled': True,
        'id': utils.REPEAT_CATEGORY_ID,
        'name': 'Вы уже заказывали',
    },
    'repeat_this_brand': {
        'enabled': True,
        'id': utils.REPEAT_THIS_BRAND_ID,
        'name': 'В этом магазине',
    },
    'repeat_other_brands': {
        'enabled': True,
        'id': utils.REPEAT_OTHER_BRANDS_ID,
        'name': 'В других магазинах',
    },
}

EATS_PRODUCTS_CONFIG = {'enable_cross_brand_order_history_storage': True}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
]

SKU_IDS = ['1', '2', '3']

SKU_TO_PUBLIC_IDS = {
    str(utils.PLACE_ID): {
        SKU_IDS[0]: [PUBLIC_IDS[0], PUBLIC_IDS[2]],
        SKU_IDS[1]: [PUBLIC_IDS[1], PUBLIC_IDS[3]],
    },
}


@pytest.fixture(name='mock_retail_categories_brand_products')
def _mock_retail_categories_brand_products(
        mock_retail_categories_brand_orders_history,
):
    mock_retail_categories_brand_orders_history.add_brand_product(
        brand_id=1, public_id=PUBLIC_IDS[0], orders_count=1,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        brand_id=1, public_id=PUBLIC_IDS[1], orders_count=2,
    )
    return mock_retail_categories_brand_orders_history


def make_menu_request(category_id=None):
    return {'shippingType': 'pickup', 'slug': 'slug', 'category': category_id}


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_all_categories(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        add_default_product_mapping,
        load_json,
        mock_retail_categories_brand_products,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается
    # вместе с подкатегориями
    add_default_product_mapping()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', '1', 1),
    )

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[1], 3, SKU_IDS[1],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_v1_nomenclature_context.handler.times_called == 1
    assert response.json() == load_json('all_categories_response.json')
    assert mock_retail_categories_brand_products.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.config(EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG)
@pytest.mark.parametrize(
    'category', ['repeat_this_brand', 'repeat_other_brands', None],
)
@experiments.repeat_category('v2')
async def test_repeat_category_v2_subcategory_config_missing(
        taxi_eats_products,
        add_default_product_mapping,
        taxi_config,
        category,
        mock_retail_categories_brand_products,
):
    # Проверяется, что если отсутствует конфиг для любой из подкатегорий:
    # repeat_this_brand или repeat_other_brands,
    # то происходит фолбек на категорию "Вы заказывали" версии 1
    settings = copy.deepcopy(
        taxi_config.get('EATS_PRODUCTS_DYNAMIC_CATEGORIES'),
    )
    settings['repeat']['enabled'] = True
    if category:
        settings[category] = {
            'enabled': True,
            'id': 1000001,
            'name': 'Подкатегория',
        }
    taxi_config.set(EATS_PRODUCTS_DYNAMIC_CATEGORIES=settings)

    add_default_product_mapping()
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    assert mock_retail_categories_brand_products.times_called == 1


@pytest.mark.parametrize(
    'category',
    [
        pytest.param(
            'repeat_this_brand',
            marks=pytest.mark.config(
                EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
            ),
        ),
        pytest.param(
            'repeat_other_brands',
            marks=pytest.mark.config(
                EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
            ),
        ),
        pytest.param(None, id='cross_brand_storage_disabled'),
    ],
)
@experiments.repeat_category('v2')
async def test_repeat_category_v2_configs_disabled(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        add_default_product_mapping,
        taxi_config,
        category,
        mock_retail_categories_brand_products,
):
    # Проверяется, что если отключена любая из подкатегорий или
    # enable_cross_brand_order_history_storage, то происходит фолбек на v1
    settings = copy.deepcopy(REPEAT_CATEGORIES_CONFIG)
    if category:
        settings[category]['enabled'] = False
    taxi_config.set(EATS_PRODUCTS_DYNAMIC_CATEGORIES=settings)

    add_default_product_mapping()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', '1', 1),
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    categories = response.json()['payload']['categories']
    assert len(categories) == 2
    assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    assert categories[1]['uid'] == '1'
    assert mock_retail_categories_brand_products.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_request_timeout(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_retail_categories_brand_products,
):
    # Проверяется, что в случае таймаута ручки номенклатуры
    # и при запросе в eats-retail-categories
    # возвращается []
    add_default_product_mapping()

    @mockserver.json_handler(utils.Handlers.CROSS_BRAND_ORDERS_HISTORY)
    def mock_cross_brand_orders_history(request):
        raise mockserver.NetworkError()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )
    assert mock_cross_brand_orders_history.times_called == 1

    assert response.status_code == 200
    assert response.json()['payload']['categories'] == []

    assert mock_retail_categories_brand_products.times_called == 1


@pytest.mark.parametrize('response_code', [404, 500])
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_bad_response(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_retail_categories_brand_products,
        mock_retail_categories_cross_brand_orders,
        response_code,
):
    # Проверяется, что при ответе из eats-retail-categories
    # 404 и 500 возвращается [].
    add_default_product_mapping()

    response = mockserver.make_response('error', status=response_code)

    mock_retail_categories_cross_brand_orders.set_status(
        status_code=response_code,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['categories'] == []
    assert mock_retail_categories_cross_brand_orders.times_called == 1


@pytest.mark.parametrize('headers', [{}, {'X-Eats-User': 'user_id='}])
async def test_repeat_category_v2_no_eater_id(
        taxi_eats_products, headers, mock_retail_categories_cross_brand_orders,
):
    # Проверяется, без авторизации пользователя не будет обращения к
    # eats-retail-categories
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=make_menu_request(), headers=headers,
    )
    assert response.status_code == 200
    assert mock_retail_categories_cross_brand_orders.times_called == 0


@pytest.mark.parametrize(
    'has_repeat_category, has_brand_products, has_cross_brand_products',
    [
        pytest.param(True, True, False, id='no_cross_brand_history'),
        pytest.param(True, False, True, id='no_brand_history'),
        pytest.param(False, False, False, id='no_history'),
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_cross_brand_empty(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        mock_retail_categories_brand_orders_history,
        add_default_product_mapping,
        has_repeat_category,
        has_brand_products,
        mock_retail_categories_cross_brand_orders,
        has_cross_brand_products,
):
    # Проверяется, что если нет товаров в брендовой или кроссбрендовой
    # истории то вернется только родительская категория
    # Если нет товаров в обеих, то даже родительская категория не возвращается
    add_default_product_mapping()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', '1', 1),
    )

    if has_brand_products:
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id=1, public_id=PUBLIC_IDS[0], orders_count=1,
        )
        mock_retail_categories_brand_orders_history.add_brand_product(
            brand_id=1, public_id=PUBLIC_IDS[1], orders_count=2,
        )
    if has_cross_brand_products:
        mock_retail_categories_cross_brand_orders.add_product(
            utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
        )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_v1_nomenclature_context.handler.times_called == 1
    categories = response.json()['payload']['categories']
    if has_repeat_category:
        assert len(categories) == 2
        assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    else:
        assert len(categories) == 1
        assert categories[0]['uid'] == '1'
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_all_with_products(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        make_public_by_sku_id_response,
        load_json,
        mock_retail_categories_brand_products,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается
    # вместе с подкатегориями и товарами в них
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[i])

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[1], 3, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[2], 1, SKU_IDS[0],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(utils.REPEAT_CATEGORY_ID),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1

    assert response.json() == load_json(
        'all_categories_with_products_response.json',
    )
    assert mock_retail_categories_brand_products.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.parametrize(
    ['requested_category', 'expected_index', 'sku_handler_times_called'],
    [(utils.REPEAT_THIS_BRAND_ID, 1, 0), (utils.REPEAT_OTHER_BRANDS_ID, 2, 1)],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_request_subcategories(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        load_json,
        make_public_by_sku_id_response,
        requested_category,
        expected_index,
        sku_handler_times_called,
        mock_retail_categories_brand_products,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что подкатегории "В этом магазине" и "В других магазинах"
    # возвращаются с товарами
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[i])

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[1], 3, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[2], 1, SKU_IDS[0],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(requested_category),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1

    expected_json = load_json('all_categories_with_products_response.json')
    expected_categories = expected_json['payload']['categories']
    categories = response.json()['payload']['categories']

    assert len(categories) == 1
    assert categories[0] == expected_categories[expected_index]
    assert mock_retail_categories_brand_products.times_called == 1
    assert (
        mock_retail_categories_cross_brand_orders.handler.times_called
        == sku_handler_times_called
    )


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_all_with_this_brand_products(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        load_json,
        mock_retail_categories_brand_products,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается без подкатегорий,
    # так как у пользователя нет кросс-брендовых товаров
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[i])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(utils.REPEAT_CATEGORY_ID),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    expected_json = load_json('all_categories_with_products_response.json')
    expected_categories = expected_json['payload']['categories']
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    assert categories[0]['items'] == expected_categories[1]['items']
    assert mock_retail_categories_brand_products.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_all_with_other_brands_products(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        make_public_by_sku_id_response,
        mock_nomenclature_dynamic_info_context,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается без подкатегорий,
    # так как у пользователя нет товаров в этом бренде
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], price=100 + i,
        )

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[1], 3, SKU_IDS[1],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[2], 1, SKU_IDS[0],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(utils.REPEAT_CATEGORY_ID),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_public_id_by_sku_id.times_called == 0

    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    item_ids = []
    for item in categories[0]['items']:
        item_ids.append(item['public_id'])
    assert item_ids == [PUBLIC_IDS[1], PUBLIC_IDS[0], PUBLIC_IDS[2]]
    assert mock_retail_categories_brand_orders_history.times_called == 1

    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_all_with_the_same_products(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        make_public_by_sku_id_response,
        load_json,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается без подкатегорий,
    # так как у пользователя товары в кроссбрендовой истории совпадают с
    # товарами в текущем бренде
    # Так же проверяется, что недоступные товары пристуствуют в ответе
    add_default_product_mapping()
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[1])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], is_available=False,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(
            request,
            {
                str(utils.PLACE_ID): {
                    SKU_IDS[0]: [PUBLIC_IDS[0]],
                    SKU_IDS[1]: [PUBLIC_IDS[1]],
                },
            },
        )

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[1], 3, SKU_IDS[1],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(utils.REPEAT_CATEGORY_ID),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_public_id_by_sku_id.times_called == 0

    categories = response.json()['payload']['categories']
    expected_json = load_json('all_categories_with_products_response.json')
    expected_categories = expected_json['payload']['categories']
    expected_items = expected_categories[1]['items'][::-1]
    expected_items[1]['available'] = False
    assert len(categories) == 1
    assert categories[0]['uid'] == str(utils.REPEAT_CATEGORY_ID)
    assert categories[0]['items'] == expected_items
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@pytest.mark.parametrize('handler', ['static_info', 'dynamic_info'])
@pytest.mark.parametrize(
    'category',
    [
        utils.REPEAT_CATEGORY_ID,
        utils.REPEAT_THIS_BRAND_ID,
        utils.REPEAT_OTHER_BRANDS_ID,
    ],
)
async def test_repeat_category_v2_all_nomenclature_404_response(
        taxi_eats_products,
        mockserver,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        handler,
        category,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется ответ 404 в случае ответа 404 в ручках
    # /eats-nomenclature/v1/place/products/info или
    # /eats-nomenclature/v1/products/info
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], price=100 + i,
        )

    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.BRAND_ID, PUBLIC_IDS[0], 1,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.BRAND_ID, PUBLIC_IDS[1], 2,
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[2], 2, SKU_IDS[0],
    )
    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[3], 3, SKU_IDS[1],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    if handler == 'dynamic_info':
        mock_nomenclature_dynamic_info_context.set_status(status_code=404)
    elif handler == 'static_info':
        mock_nomenclature_static_info_context.set_status(status_code=404)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(category),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 404
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert mock_nomenclature_dynamic_info_context.times_called == 1
    assert mock_nomenclature_static_info_context.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES={
        'discount': {
            'enabled': False,
            'id': utils.DISCOUNT_CATEGORY_ID,
            'name': 'Скидки',
        },
        'popular': {
            'enabled': False,
            'id': utils.POPULAR_CATEGORY_ID,
            'name': 'Популярное',
        },
        'repeat': {
            'enabled': True,
            'id': utils.REPEAT_CATEGORY_ID,
            'name': 'Вы уже заказывали',
        },
        'repeat_this_brand': {
            'enabled': False,
            'id': utils.REPEAT_THIS_BRAND_ID,
            'name': 'В этом магазине',
        },
    },
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@pytest.mark.parametrize(
    'category',
    [
        utils.REPEAT_CATEGORY_ID,
        utils.REPEAT_THIS_BRAND_ID,
        utils.REPEAT_OTHER_BRANDS_ID,
    ],
)
async def test_repeat_category_v2_categories_disabled(
        taxi_eats_products,
        mockserver,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        category,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что если в конфиге отсутствую или отключены подкатегории
    # возвращается ответ 200
    add_default_product_mapping()
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], price=100 + i,
        )

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(category),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    if category == utils.REPEAT_CATEGORY_ID:
        assert len(categories) == 1
        assert categories[0]['id'] == utils.REPEAT_CATEGORY_ID
    else:
        assert categories == []
    assert mock_retail_categories_brand_orders_history.times_called == (
        1 if category == utils.REPEAT_CATEGORY_ID else 0
    )


@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_repeat_config_disabled(
        taxi_eats_products, add_default_product_mapping,
):
    # Проверяется, что если в конфиге отключена категория, то
    # возвращается пустой ответ 200
    add_default_product_mapping()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(utils.REPEAT_CATEGORY_ID),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['payload']['categories'] == []


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@pytest.mark.parametrize(
    'category',
    [
        utils.REPEAT_CATEGORY_ID,
        utils.REPEAT_THIS_BRAND_ID,
        utils.REPEAT_OTHER_BRANDS_ID,
    ],
)
async def test_repeat_category_v2_no_core_mapping(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
        category,
):
    # Проверяется, что если базе нет core_id для товаров, то
    # при в ответе не будет товаров
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', public_id=PUBLIC_IDS[0],
            ),
        ],
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])

    mock_retail_categories_brand_orders_history.add_default_products()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(category),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    if category == utils.REPEAT_CATEGORY_ID:
        assert categories == []
    else:
        assert len(categories) == 1
        assert categories[0]['id'] == category
        assert categories[0]['items'] == []


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
@pytest.mark.parametrize(
    'category',
    [
        utils.REPEAT_CATEGORY_ID,
        utils.REPEAT_THIS_BRAND_ID,
        utils.REPEAT_OTHER_BRANDS_ID,
    ],
)
async def test_repeat_category_v2_no_ordered_products(
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        make_public_by_sku_id_response,
        category,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что если у пользователя нет товаров ни в брендовой истории,
    # ни в кросс брендовой, то вернется пустая запрошенная категория
    add_default_product_mapping()
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=make_menu_request(category),
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']

    if category == utils.REPEAT_CATEGORY_ID:
        assert categories == []
    else:
        assert len(categories) == 1
        assert categories[0]['id'] == category


@pytest.mark.parametrize(
    ['max_depth', 'has_subcategories'], [(None, True), (1, False), (2, True)],
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_max_depth(
        taxi_eats_products,
        mockserver,
        mock_v1_nomenclature_context,
        add_default_product_mapping,
        make_public_by_sku_id_response,
        max_depth,
        has_subcategories,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что категория "Мои покупки" возвращается
    # вместе с подкатегориями только, если maxDepth не задано
    # или maxDepth>1
    add_default_product_mapping()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', '1', 1),
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, SKU_TO_PUBLIC_IDS)

    request = make_menu_request()
    request['maxDepth'] = max_depth

    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    mock_retail_categories_cross_brand_orders.add_product(
        utils.PLACE_ID, PUBLIC_IDS[0], 2, SKU_IDS[0],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()

    categories = response.json()['payload']['categories']
    assert categories

    if has_subcategories:
        assert mock_public_id_by_sku_id.times_called == 0
        assert [category['id'] for category in categories][:3] == [
            utils.REPEAT_CATEGORY_ID,
            utils.REPEAT_THIS_BRAND_ID,
            utils.REPEAT_OTHER_BRANDS_ID,
        ]
    else:
        assert [category['id'] for category in categories] == [
            utils.REPEAT_CATEGORY_ID,
            1,
        ]

    assert mock_retail_categories_cross_brand_orders.handler.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=REPEAT_CATEGORIES_CONFIG,
    EATS_PRODUCTS_SETTINGS=EATS_PRODUCTS_CONFIG,
)
@pytest.mark.parametrize('max_depth', [None, 1, 2])
@experiments.repeat_category('v2', 'Мои покупки')
async def test_repeat_category_v2_no_categories(
        taxi_eats_products,
        add_default_product_mapping,
        max_depth,
        mock_retail_categories_brand_orders_history,
        mock_retail_categories_cross_brand_orders,
):
    # Проверяется, что если у пользователя нет товаров ни в брендовой истории,
    # ни в кросс брендовой, и сделать запрос без категории (то категория
    # "Мои покупки" не вернется в ответе
    add_default_product_mapping()

    request = make_menu_request()
    request['maxDepth'] = max_depth

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']

    assert categories == []
