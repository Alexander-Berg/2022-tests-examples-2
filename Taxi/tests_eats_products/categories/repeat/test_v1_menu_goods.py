import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}

DEFAULT_PICTURE_URL = (
    'https://avatars.mds.yandex.net/get-eda'
    + '/3770794/4a5ca0af94788b6e40bec98ed38f58cc/{w}x{h}'
)


@experiments.repeat_category()
async def test_empty_nomenclature(
        taxi_eats_products,
        mockserver,
        load_json,
        add_place_products_mapping,
        mock_v1_nomenclature,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если /v1/nomenclature не вернула категории,
    # но также нужно вернуть категорию "Повторим",
    # то возвращается только категория "Повторим".
    mock_retail_categories_brand_orders_history.add_brand_product(
        brand_id=1, public_id='public_id_1', orders_count=1,
    )

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id='public_id_1',
            ),
        ],
    )
    mock_v1_nomenclature.set_response({'categories': []})

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return get_details_response(request, load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert mock_retail_categories_brand_orders_history.times_called == 1
    assert categories[0]['id'] == utils.REPEAT_CATEGORY_ID


@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_request_repeat_category(
        taxi_eats_products,
        mockserver,
        load_json,
        add_default_product_mapping,
        handlers_version,
        setup_nomenclature_handlers_v2,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если запрашивается категория "Повторим",
    # то возвращается только она.
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    if handlers_version == 'v2':
        setup_nomenclature_handlers_v2()
    else:

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature_products(request):
            return get_details_response(request, load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == utils.REPEAT_CATEGORY_ID


@experiments.repeat_category()
@pytest.mark.parametrize('nmn_integration_version', ['v1', 'v2'])
async def test_merge_responses(
        mock_nomenclature_for_v2_menu_goods,
        add_place_products_mapping,
        mock_retail_categories_brand_orders_history,
        nmn_integration_version,
):
    # Тест проверяет, что если нужно вернуть категорию "Повторим" и
    # ручки номенклатуры возвращают валидный ответ, то ручка возвращает
    # и категории из номенклатуры, и категорию "Повторим".
    add_place_products_mapping(
        [conftest.ProductMapping(origin_id='item_id_1', core_id=1)],
    )

    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat)
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='2', name='name', origin_id='category_origin_id',
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)

    mock_retail_categories_brand_orders_history.add_default_products()
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 3
    assert set(c['id'] for c in categories) == {1, 2, utils.REPEAT_CATEGORY_ID}
    assert mock_retail_categories_brand_orders_history.times_called == 1


@experiments.repeat_category()
async def test_not_authorized(taxi_eats_products, mock_v1_nomenclature):
    # Тест проверяет, что если пользователь не авторизован,
    # то категория "Повторим" не возвращается, даже если ее нужно вернуть
    # и она непосредственно запрашивается.
    headers = copy.deepcopy(PRODUCTS_HEADERS)
    headers['X-Eats-User'] = ''

    mock_v1_nomenclature.set_response({'categories': []})

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=PRODUCTS_BASE_REQUEST, headers=headers,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.repeat_category()
async def test_repeat_category_enabled(
        taxi_eats_products, taxi_config, mock_v1_nomenclature,
):
    # Тест проверяет, что параметр 'repeat_category_enabled' в конфиге
    # отключает возвращение категории "Повторим".

    settings = copy.deepcopy(
        taxi_config.get('EATS_PRODUCTS_DYNAMIC_CATEGORIES'),
    )
    settings['repeat']['enabled'] = False
    taxi_config.set(EATS_PRODUCTS_DYNAMIC_CATEGORIES=settings)

    mock_v1_nomenclature.set_response({'categories': []})

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.repeat_category('disabled')
async def test_experiment(taxi_eats_products, mock_v1_nomenclature):
    # Тест проверяет, что если эксперимент отключен,
    # то категория "Повторим" не возвращается.
    mock_v1_nomenclature.set_response({'categories': []})

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_sort_products2(
        taxi_eats_products,
        mockserver,
        load_json,
        handlers_version,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что товары возвращаются в отсортированном
    # порядке согласно числу покупок и их цене, а недоступные товары
    # отображаются в конце списка
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 2,
    )

    if handlers_version == 'v2':
        public_ids = [
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
        ]
        for public_id in public_ids:
            mock_nomenclature_static_info_context.add_product(public_id)

        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            price=999.0,
            is_available=True,
            in_stock=20,
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            price=999.0,
            is_available=False,
            in_stock=99,
            old_price=1000,
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            price=990.0,
            is_available=True,
            old_price=1000,
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            price=990.0,
            is_available=False,
            old_price=1000,
        )
    else:

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature_products(request):
            details_response = get_details_response(request, load_json)
            details_response['products'][1]['is_available'] = False
            return details_response

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products = [p['id'] for p in categories[0]['items']]
    assert products == [3, 1, 2, 7]


@pytest.mark.parametrize('max_products', [1, 2, 10])
@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_max_products(
        taxi_eats_products,
        mockserver,
        load_json,
        taxi_config,
        max_products,
        handlers_version,
        setup_nomenclature_handlers_v2,
        add_default_product_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что возвращается не более max_products товаров,
    # где max_products задается в конфиге.
    add_default_product_mapping()
    settings = copy.deepcopy(taxi_config.get('EATS_PRODUCTS_SETTINGS'))
    settings['max_products'] = max_products
    taxi_config.set(EATS_PRODUCTS_SETTINGS=settings)

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()

    if handlers_version == 'v2':
        setup_nomenclature_handlers_v2()
    else:

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature_products(request):
            return get_details_response(request, load_json)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    products_len = len(categories[0]['items'])
    assert products_len == min(products_len, max_products)


@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_content2(
        taxi_eats_products,
        mockserver,
        load_json,
        handlers_version,
        setup_nomenclature_handlers_v2,
        add_default_product_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет полное содержимое ответа ручки.
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    if handlers_version == 'v2':
        setup_nomenclature_handlers_v2()
    else:

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature_products(request):
            return get_details_response(request, load_json)

    mock_retail_categories_brand_orders_history.add_default_products()
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 2,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    categories = response.json()['payload']['categories']
    assert {1, 2, 3, 7} == {p['id'] for p in categories[0]['items']}


@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
async def test_no_nomenclature_products(
        taxi_eats_products,
        mockserver,
        handlers_version,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если ручка номеклатуры /v2/assortment/details
    # или v1/products/info и v1/products/info
    # вернули пустой ответ сервис отдаёт пустую категорию повторим
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    if handlers_version == 'v1':

        @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
        def _mock_eats_nomenclature_products(request):
            return {'products': [], 'categories': []}

    mock_retail_categories_brand_orders_history.add_default_products()

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert not categories


@experiments.repeat_category()
@pytest.mark.parametrize('nmn_integration_version', ['v1', 'v2'])
async def test_no_products_on_top_repeat_category(
        add_place_products_mapping,
        mock_nomenclature_for_v2_menu_goods,
        mock_retail_categories_brand_orders_history,
        nmn_integration_version,
):
    # Тест проверяет, что категория «Повторим» не содержит
    # товары, если запрашивается корень магазина
    add_place_products_mapping(
        [conftest.ProductMapping(origin_id='item_id_1', core_id=1)],
    )

    mock_retail_categories_brand_orders_history.add_default_products()
    mock_nomenclature_context = mock_nomenclature_for_v2_menu_goods
    root_cat = conftest.CategoryMenuGoods(
        public_id='1', name='name', origin_id='category_origin_id',
    )
    place = conftest.PlaceMenuGoods(
        place_id=utils.PLACE_ID,
        slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
    )
    place.add_root_category(root_cat)
    root_cat_1 = conftest.CategoryMenuGoods(
        public_id='2', name='name', origin_id='category_origin_id',
    )
    place.add_root_category(root_cat_1)
    mock_nomenclature_context.set_place(place)
    response = await mock_nomenclature_context.invoke_menu_goods_basic(
        PRODUCTS_BASE_REQUEST,
        integration_version=nmn_integration_version,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    category_id = utils.REPEAT_CATEGORY_ID
    assert category_id in categories
    assert not categories[category_id]['items']


def get_details_response(request, load_json):
    request_json = request.json
    response_json = load_json('v2_place_assortment_details_response.json')

    response_json['products'] = [
        product
        for product in response_json['products']
        if product['product_id'] in set(request_json['products'])
    ]

    return response_json


@experiments.repeat_category()
async def test_repeat_categories_show_in_empty(
        taxi_eats_products,
        mockserver,
        load_json,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что для категории "Вы заказывали" поле show_in пустое
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200
    assert 'show_in' in response.json()['payload']['categories'][0]
    assert not response.json()['payload']['categories'][0]['show_in']


@experiments.repeat_category()
@utils.PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION
@pytest.mark.parametrize('v1_place_products_info_has_error', (True, False))
async def test_repeat_categories_nomenclature_v2_place_404_code(
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        add_default_product_mapping,
        handlers_version,
        v1_place_products_info_has_error,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если
    # /eats-nomenclature/v2/place/assortment/details или
    # /eats-nomenclature/v1/place/products/info или
    # /eats-nomenclature/v1/products/info
    # возвращает 404, то ручка тоже возвращает 404
    add_default_product_mapping()
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.add_default_products()
    if handlers_version == 'v2':
        if v1_place_products_info_has_error:
            mock_nomenclature_dynamic_info_context.set_status(status_code=404)
        else:
            mock_nomenclature_static_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_v2_details_context.set_status(status_code=404)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 404
    assert mock_retail_categories_brand_orders_history.times_called == 1


@experiments.repeat_category()
async def test_repeat_category_ordershistory_network_error(
        taxi_eats_products,
        mock_nomenclature_v2_details_context,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что в случае если запрашивается категория "Повторим" и
    # произошла ошибка при запросе ordershistory, то ошибка пробросится
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.REPEAT_CATEGORY_ID

    mock_retail_categories_brand_orders_history.network_error = True

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 500
    assert mock_nomenclature_v2_details_context.handler.times_called == 0


@experiments.repeat_category()
async def test_all_categories_ordershistory_network_error(
        taxi_eats_products,
        mock_v1_nomenclature_context,
        mock_retail_categories_brand_orders_history,
):
    # Тест проверяет, что если запрашиваются все категории и произошла ошибка
    # при запросе ordershistory, то запрос не вернёт категорию "Повторим" и
    # в остальном выполнится корректно
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', '1', 1),
    )
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_2', '2', 2),
    )
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_3', '3', 3),
    )

    mock_retail_categories_brand_orders_history.network_error = True

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 3
    assert set(c['id'] for c in categories) == {1, 2, 3}
