# pylint: disable=too-many-lines
import copy
import typing

import pytest

from tests_eats_products import conftest
from tests_eats_products import eats_upsell_recommendations as upsell
from tests_eats_products import experiments
from tests_eats_products import utils
from tests_eats_products.helpers import menu_product_response


HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'X-Eats-User': 'user_id=456',
}

PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

SLUG = 'slug'
BRAND_SLUG = 'brand1'

BASE_REQUEST_NO_SLUG_PUBLIC = {'product_public_id': PRODUCT_PUBLIC_ID}

BASE_REQUEST_BRAND_PUBLIC = {
    'brand_slug': BRAND_SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}

BASE_REQUEST_PUBLIC = {
    'place_slug': SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}

BASE_REQUEST_CORE = {'place_slug': SLUG, 'product_core_id': '1'}
BASE_REQUEST_BOTH = {**BASE_REQUEST_PUBLIC, **BASE_REQUEST_CORE}

RECOMMENDATIONS_TYPE = 'upsell_recommendations'
RECOMMENDATIONS_TITLE = 'Title'
SEPARATOR = 'separator'
GALLERY = 'gallery'
ENERGY_VALUES_TYPE = 'energy_values'
HEADER_TYPE = 'header'
DESCRIPTION_TYPE = 'description'
PRODUCT_DETAILS = 'product_details'
PRODUCT_NAME = 'product_name'
DESCRIPTION = 'description'

DESCRIPTION_WITH_BOLD = (
    '<b>Состав:</b> груша <br><b>Срок годности:</b> 30сут<br>'
)

DESCRIPTION_WITHOUT_BOLD = 'Состав: груша <br>Срок годности: 30сут<br>'

NON_EXISTENT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69bfff'
NON_EXISTENT_CORE_ID = '54321'

PRODUCT_PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
]

COLOR_SETTINGS = {
    'title_color': {'light': '#100000', 'dark': '#100001'},
    'subtitle_color': {'light': '#200000', 'dark': '#200002'},
}

STATIC_INFO_BATCH_SIZE = 50


@pytest.mark.parametrize(
    ['request_json'],
    ([BASE_REQUEST_PUBLIC], [BASE_REQUEST_CORE], [BASE_REQUEST_BOTH]),
)
@pytest.mark.parametrize('has_currency_in_db', [False, True])
@pytest.mark.parametrize(['has_promo_price'], ([False], [True]))
@pytest.mark.parametrize(['is_available'], ([True], [False]))
@pytest.mark.parametrize(['with_categories'], ([True], [False]))
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DETAILED_DATA_DESCRIPTIONS_ENABLED
async def test_menu_product_happy_path(
        mockserver,
        taxi_eats_products,
        load_json,
        request_json,
        has_promo_price,
        is_available,
        with_categories,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
        sql_set_place_currency,
        has_currency_in_db,
):
    add_default_product_mapping()
    expected_response = load_json('expected_response.json')

    if has_currency_in_db:
        sql_set_place_currency(code='BYN', sign='руб.')
        expected_response['place']['currency'] = {
            'code': 'BYN',
            'sign': 'руб.',
        }

    old_price = None
    price = 175.0
    if has_promo_price:
        old_price = 175
        price = 50

    if not is_available:
        expected_response['menu_item']['available'] = False

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        price=price,
        is_available=is_available,
        old_price=old_price,
        parent_category_ids=['3', '4'],
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        description_general=DESCRIPTION_WITH_BOLD,
        expiration_info_value=8,
        expiration_info_unit='д',
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_v1_product_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category('3', 'category 3', '2')
    mock_nomenclature_get_parent_context.add_category('4', 'category 4', '2')

    request = copy.deepcopy(request_json)
    request['with_categories'] = with_categories
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )
    response_json = resp.json()

    if with_categories:
        assert 'categories' in response_json
        categories = response_json['categories']
        assert {
            (category['id'], category['name']) for category in categories
        } == {('3', 'category 3'), ('4', 'category 4')}

        del response_json['categories']
    else:
        assert 'categories' not in response_json

    assert mock_nomenclature_get_parent_context.handler.times_called == (
        1 if with_categories else 0
    )

    if has_promo_price:
        has_discount = any(
            pt['type'] == 'price_discount'
            for pt in resp.json()['menu_item']['promoTypes']
        )
        assert has_discount

        for json_ in [response_json, expected_response]:
            for field in ('decimalPromoPrice', 'promoPrice'):
                json_['menu_item'].pop(field, None)
        response_json['menu_item']['promoTypes'] = []
    assert response_json == expected_response


@pytest.mark.parametrize(
    'with_recommendations',
    [
        pytest.param(
            True,
            id='with recommendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_ENABLED,
        ),
        pytest.param(
            False,
            id='without recommendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_DISABLED,
        ),
    ],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_product_discount_applicator(
        taxi_eats_products,
        mock_v2_match_discounts_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        eats_order_stats,
        mock_eats_tags,
        with_recommendations,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
):
    """
        Проверяется выставление скидок и кешбека
        для menu/product
    """
    add_default_product_mapping()
    mock_v2_match_discounts_context.add_cashback_product(
        PRODUCT_PUBLIC_ID, 'absolute', 4.0,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PRODUCT_PUBLIC_ID, 'absolute', 3.0,
    )
    mock_v2_match_discounts_context.set_use_tags(True)

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    if with_recommendations:
        mock_upsell_recommendations.add_recommendations(
            upsell.DEFAULT_RECOMMENDATIONS,
        )

        mock_nomenclature_dynamic_info_context.add_product(
            upsell.PUBLIC_IDS[0], price=100, is_available=True, old_price=None,
        )
        mock_nomenclature_static_info_context.add_product(upsell.PUBLIC_IDS[0])

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert (
        mock_nomenclature_dynamic_info_context.handler.times_called == 2
        if with_recommendations
        else 1
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    has_cashback = any(
        pt['type'] == 'cashback'
        for pt in resp.json()['menu_item']['promoTypes']
    )
    assert has_cashback

    has_discount = any(
        pt['type'] == 'price_discount'
        for pt in resp.json()['menu_item']['promoTypes']
    )
    assert has_discount


@pytest.mark.parametrize('description', ('', '   ', '\t'))
async def test_menu_product_empty_description(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        description,
):
    """
    Если нет информации о товаре, блок "О товаре" не показывается.
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=description,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    # Нет ни хедера, ни описание, так как оно пустое
    detailed_data = resp.json()['detailed_data']

    assert [1 for part in detailed_data if part['type'] == GALLERY]
    assert not [
        1 for part in detailed_data if part['type'] == DESCRIPTION_TYPE
    ]
    assert not [1 for part in detailed_data if part['type'] == HEADER_TYPE]


@pytest.mark.parametrize(
    'has_additional_fields',
    [
        pytest.param(
            True, marks=experiments.DETAILED_DATA_DESCRIPTIONS_ENABLED,
        ),
        pytest.param(
            False, marks=experiments.DETAILED_DATA_DESCRIPTIONS_DISABLED,
        ),
    ],
)
@pytest.mark.parametrize(
    'name_and_about_product_widgets_enabled',
    [
        pytest.param(True, marks=experiments.product_card_widgets(True)),
        pytest.param(False, marks=experiments.product_card_widgets(False)),
    ],
)
async def test_menu_product_detailed_data_descriptions(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        has_additional_fields,
        name_and_about_product_widgets_enabled,
):
    """
    Тест проверяет блок с информацией о товаре.
    has_additional_fields - включает эксп для доп полей в описании
    карточки товара.
    name_and_about_product_widgets_enabled - включает виджеты
    для отображения имени и "Подробнее о товаре"
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )

    expected = [
        {'title': 'Состав', 'text': 'Картофель'},
        {'title': 'Срок годности', 'text': '8 д'},
        {'title': 'Условия хранения', 'text': 'От +5С до +25С'},
        {'title': 'Производитель', 'text': 'Pringles'},
        {'title': 'Страна', 'text': 'Россия'},
        {'title': 'Бренд', 'text': 'Бренд'},
        {'title': 'Сорт винограда', 'text': 'Сорт винограда'},
        {'title': 'Вкус', 'text': 'Вкус'},
        {'title': 'Аромат', 'text': 'Аромат'},
        {'title': 'Пейринг', 'text': 'Пейринг'},
        {'title': 'Описание', 'text': DESCRIPTION_WITH_BOLD},
    ]

    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        description_general=DESCRIPTION_WITH_BOLD,
        expiration_info_value=8,
        expiration_info_unit='д',
        composition='Картофель',
        storage_requirements='От +5С до +25С',
        vendor_name='Pringles',
        vendor_country='Россия',
        brand='Бренд',
        alco_grape_cultivar='Сорт винограда',
        alco_flavour='Вкус',
        alco_aroma='Аромат',
        alco_pairing='Пейринг',
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    detailed_data = resp.json()['detailed_data']
    if name_and_about_product_widgets_enabled:
        descriptions = detailed_data[2]['payload']['product_descriptions']
        assert detailed_data[2]['title'] == 'Подробнее о товаре'
        assert detailed_data[2]['type'] == PRODUCT_DETAILS
    else:
        descriptions = detailed_data[2]['payload']['descriptions']

    if has_additional_fields:
        assert descriptions == expected
    else:
        assert descriptions[0]['text'] == DESCRIPTION_WITH_BOLD
        assert len(descriptions) == 1


@pytest.mark.parametrize(['has_promo_price'], ([False], [True]))
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
async def test_menu_product_discount_applicator_without_discount(
        taxi_eats_products,
        has_promo_price,
        mock_v2_match_discounts_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        eats_order_stats,
        mock_eats_tags,
):
    add_default_product_mapping()
    old_price = None
    price = 175.0
    if has_promo_price:
        old_price = price
        price /= 2

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=price, is_available=True, old_price=old_price,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=DESCRIPTION_WITH_BOLD,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    has_discount = any(
        pt['type'] == 'price_discount'
        for pt in resp.json()['menu_item']['promoTypes']
    )
    assert has_discount == has_promo_price


async def test_menu_product_no_id(taxi_eats_products):
    request = BASE_REQUEST_PUBLIC.copy()
    request.pop('product_public_id')

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    assert resp.status_code == 400


@pytest.mark.parametrize('v1_place_products_info_has_error', (True, False))
async def test_menu_product_nomenclature_error(
        taxi_eats_products,
        v1_place_products_info_has_error,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
):
    if v1_place_products_info_has_error:
        mock_nomenclature_dynamic_info_context.set_status(status_code=500)
    else:
        mock_nomenclature_static_info_context.set_status(status_code=500)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 500


async def test_menu_product_v1_place_products_info_timeout(
        mockserver, taxi_eats_products, mock_nomenclature_static_info_context,
):
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACE_PRODUCTS_INFO)
    def _mock_v1_place_products(request):
        raise mockserver.TimeoutError()

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 500


@pytest.mark.parametrize(
    'base_request',
    [
        pytest.param(BASE_REQUEST_NO_SLUG_PUBLIC, id='without any slug'),
        pytest.param(BASE_REQUEST_BRAND_PUBLIC, id='without place slug'),
    ],
)
async def test_menu_product_no_slug(taxi_eats_products, base_request):
    """
        Проверяет код ошибки, если не задан плейс слаг или задан бренд слаг,
        но не включено использование обобщённой ручки
    """
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=base_request, headers=HEADERS,
    )
    assert resp.status_code == 400


async def test_menu_product_v1_products_info_timeout(
        mockserver, taxi_eats_products, mock_nomenclature_dynamic_info_context,
):
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS_INFO)
    def _mock_v1_place_products(request):
        raise mockserver.TimeoutError()

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 500


@pytest.mark.parametrize('v1_place_products_info_has_error', (True, False))
async def test_menu_product_nomenclature_404_code(
        taxi_eats_products,
        v1_place_products_info_has_error,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
):
    # Тест проверяет, что если
    # /eats-nomenclature/v1/place/products/info или
    # /eats-nomenclature/v1/products/info
    # возвращает 404, то ручка тоже возвращает 404
    if v1_place_products_info_has_error:
        mock_nomenclature_dynamic_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_static_info_context.set_status(status_code=404)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'place_not_found'


async def test_menu_product_place_not_found(taxi_eats_products):
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json={
            'place_slug': 'wrong_slug',
            'product_public_id': PRODUCT_PUBLIC_ID,
        },
        headers=HEADERS,
    )
    assert resp.status_code == 404


async def test_menu_product_no_mapping(taxi_eats_products):
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json={'place_slug': SLUG, 'product_core_id': NON_EXISTENT_CORE_ID},
        headers=HEADERS,
    )
    assert resp.status_code == 404
    assert resp.json() == {
        'code': 'mapping_not_found',
        'message': 'MappingNotFound',
    }


@pytest.mark.parametrize(
    ['is_available', 'expected_recommendations'],
    [(True, True), (False, False)],
)
@pytest.mark.parametrize(
    'has_recommendations_title',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        {'recommendations_title': 'Title'}
                    ),
                )
            ),
            id='with recommendations_title',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        {'recommendations_title': None}
                    ),
                )
            ),
            id='without recommendations_title',
        ),
    ],
)
@pytest.mark.parametrize(
    'with_categories',
    [
        pytest.param(True, id='with categories'),
        pytest.param(False, id='without categories'),
    ],
)
@pytest.mark.parametrize(
    'with_recommendations',
    [
        pytest.param(
            True,
            id='with recommendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_ENABLED,
        ),
        pytest.param(
            False,
            id='without recommendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_DISABLED,
        ),
    ],
)
@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_recommendations(
        taxi_eats_products,
        mockserver,
        load_json,
        has_recommendations_title,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
        is_available,
        expected_recommendations,
        with_categories,
        with_recommendations,
):
    add_default_product_mapping()

    for public_id in [*PRODUCT_PUBLIC_IDS, PRODUCT_PUBLIC_ID]:
        mock_nomenclature_dynamic_info_context.add_product(
            public_id,
            price=100,
            is_available=is_available,
            in_stock=None if is_available else 0,
            parent_category_ids=['3', '4'],
        )
        mock_nomenclature_static_info_context.add_product(
            public_id, description_general=DESCRIPTION_WITH_BOLD,
        )

    mock_upsell_recommendations.add_recommendations(
        upsell.DEFAULT_RECOMMENDATIONS,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_v1_product_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category('3', 'category 3', '2')
    mock_nomenclature_get_parent_context.add_category('4', 'category 4', '2')

    request = copy.deepcopy(BASE_REQUEST_PUBLIC)
    request['with_categories'] = with_categories
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    response_json = resp.json()

    if with_categories:
        assert 'categories' in response_json
        categories = response_json['categories']
        assert {
            (category['id'], category['name']) for category in categories
        } == {('3', 'category 3'), ('4', 'category 4')}
    else:
        assert 'categories' not in response_json

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert (
        mock_nomenclature_dynamic_info_context.handler.times_called == 2
        if with_categories or with_recommendations
        else 1
    )

    detailed_data = response_json['detailed_data']
    if not expected_recommendations or not with_recommendations:
        # Единственный товар не доступен => блока с рекомендациями быть
        # не должно
        for item in detailed_data:
            assert item['type'] != RECOMMENDATIONS_TYPE
        return

    payload = detailed_data[4]['payload']
    recommendations_type = detailed_data[4]['type']
    separator = detailed_data[3]
    recommendations = payload['recommendations']
    expected_recommendations = load_json('expected_recommendations.json')

    assert len(recommendations) == 1
    recommendations[0]['items'].sort(key=lambda x: x.get('id'))
    assert recommendations[0]['items'] == expected_recommendations['items']
    if has_recommendations_title:
        assert recommendations[0]['title'] == RECOMMENDATIONS_TITLE
    else:
        assert 'title' not in recommendations[0]
    assert recommendations_type == RECOMMENDATIONS_TYPE
    assert separator['type'] == SEPARATOR


@pytest.mark.config(
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
        'v1_products_info_batch_size': STATIC_INFO_BATCH_SIZE,
    },
)
@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_large_number_of_recommendations(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_upsell_recommendations,
        mock_nomenclature_get_parent_context,
):
    # Тест проверяет что в случае если рекомендуемых товаров больше чем размер
    # батча в ручке получения статической информации, то данные будут получены
    # для всех товаров за несколько батч-запросов

    batch_count = 3
    items_count = STATIC_INFO_BATCH_SIZE * batch_count
    recommendations = []
    ids_mapping = []

    for i in range(1, items_count + 1):
        origin_id = str(i)
        core_id = 100 + i
        public_id = f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b{i:03d}'

        ids_mapping.append(
            conftest.ProductMapping(origin_id, core_id, public_id),
        )

        # Первый товар - запрашиваемый в ручке, его не должно быть в
        # рекомендациях
        if i != 1:
            recommendations.append(
                upsell.Recommendation(public_id, upsell.Source.Advert),
            )

        mock_nomenclature_dynamic_info_context.add_product(
            id_=public_id, origin_id=origin_id, is_available=True, in_stock=1,
        )

        mock_nomenclature_static_info_context.add_product(
            public_id, description_general=DESCRIPTION_WITH_BOLD,
        )

    add_place_products_mapping(ids_mapping)
    mock_upsell_recommendations.add_recommendations(recommendations)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json={'place_slug': SLUG, 'product_public_id': PRODUCT_PUBLIC_ID},
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert (
        mock_nomenclature_static_info_context.handler.times_called
        == batch_count
    )

    detailed_data = response.json()['detailed_data']

    payload = detailed_data[4]['payload']
    recommendations = payload['recommendations']

    assert len(recommendations) == 1
    # Рекомендаций на одну меньше чем количество сгенерированных элементов.
    # Это потому что один из сгенерированных - запрашиваемый товар.
    assert len(recommendations[0]['items']) == items_count - 1


@pytest.mark.parametrize(
    (),
    [
        pytest.param(
            marks=experiments.UPSELL_RECOMMENDATIONS_ENABLED,
            id='upsell error',
        ),
        pytest.param(
            marks=experiments.UPSELL_RECOMMENDATIONS_DISABLED, id='exp off',
        ),
    ],
)
async def test_menu_product_recommendations_absent(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)
    mock_upsell_recommendations.set_raise_error(True)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    detailed_data = resp.json()['detailed_data']
    gallery = [part for part in detailed_data if part['type'] == 'gallery']
    assert gallery
    recommendations = [
        i for i in detailed_data if i['type'] == RECOMMENDATIONS_TYPE
    ]
    assert not recommendations


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_recommendations_empty_nomenclature_response(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_upsell_recommendations,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    mock_upsell_recommendations.add_recommendations(
        upsell.DEFAULT_RECOMMENDATIONS,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    detailed_data = resp.json()['detailed_data']
    assert resp.status_code == 200
    assert mock_upsell_recommendations.times_called == 1

    gallery = [part for part in detailed_data if part['type'] == GALLERY]
    assert gallery
    recommendations = [
        i for i in detailed_data if i['type'] == RECOMMENDATIONS_TYPE
    ]
    assert not recommendations


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_empty_upsell_response(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_upsell_recommendations,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    detailed_data = resp.json()['detailed_data']
    assert resp.status_code == 200
    assert mock_upsell_recommendations.times_called == 1

    gallery = [part for part in detailed_data if part['type'] == GALLERY]
    assert gallery

    recommendations = [
        i for i in detailed_data if i['type'] == RECOMMENDATIONS_TYPE
    ]
    assert not recommendations


@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
async def test_menu_product_product_categories_empty_response(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
):
    """
    При пустом ответе от ручки get_parent, получаем 200 в статусе
    и отсутствие категорий в ответе
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)
    request = BASE_REQUEST_PUBLIC.copy()
    request['with_categories'] = True
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    assert resp.status_code == 200
    assert 'categories' not in resp.json()


@pytest.mark.parametrize(
    'response_code', [400, 404, 429, 500, 'timeout_error', 'network_error'],
)
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
async def test_menu_product_product_categories_bad_response(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
        response_code,
):
    """
        При плохих ответах от ручки get_parent, получаем 200 в статусе
        и отсутствие категорий в ответе
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    if response_code == 'timeout_error':
        mock_nomenclature_get_parent_context.set_timeout_error(True)
    elif response_code == 'network_error':
        mock_nomenclature_get_parent_context.set_network_error(True)
    else:
        mock_nomenclature_get_parent_context.set_status(response_code)

    request = BASE_REQUEST_PUBLIC.copy()
    request['with_categories'] = True
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    assert resp.status_code == 200
    assert 'categories' not in resp.json()


@pytest.mark.parametrize(
    'delete_bold',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        {'tags_to_delete': ['<b>', '</b>']}
                    ),
                )
            ),
            id='need to delete bold',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        {'delete_bold': False}
                    ),
                )
            ),
            id='dont delete bold',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        {'delete_bold': None}
                    ),
                )
            ),
            id='empty delete_bold',
        ),
    ],
)
async def test_menu_product_delete_bold_from_descriptions(
        taxi_eats_products,
        delete_bold,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=DESCRIPTION_WITH_BOLD,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert resp.json()['menu_item']['description'] == DESCRIPTION_WITH_BOLD

    descriptions = resp.json()['detailed_data'][2]['payload']['descriptions']
    if delete_bold:
        assert descriptions[0]['text'] == DESCRIPTION_WITHOUT_BOLD
    else:
        assert descriptions[0]['text'] == DESCRIPTION_WITH_BOLD


@pytest.mark.parametrize(
    'has_energy_value, nomenclature_response, expected_energy_values',
    [
        pytest.param(
            True,
            {
                'fats': '11.0',
                'proteins': '17.0',
                'carbohydrates': '1.5',
                'calories_value': '170.0',
                'calories_unit': 'ккал',
            },
            {
                'energy_values': [
                    {'name': 'жиры', 'value': '11 г'},
                    {'name': 'белки', 'value': '17 г'},
                    {'name': 'углеводы', 'value': '1.5 г'},
                    {'name': 'ккал', 'value': '170'},
                ],
            },
            id='have all the PCF',
        ),
        pytest.param(
            False,
            {
                'fats': '11.0',
                'calories_value': '170.0',
                'calories_unit': 'ккал',
            },
            {
                'energy_values': [
                    {'name': 'жиры', 'value': '11 г'},
                    {'name': 'белки', 'value': '—'},
                    {'name': 'углеводы', 'value': '—'},
                    {'name': 'ккал', 'value': '170'},
                ],
            },
            id='some PCF are missing',
        ),
    ],
)
@experiments.ENERGY_VALUES_ENABLED
async def test_menu_product_energy_values_exist(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        nomenclature_response,
        expected_energy_values,
        add_default_product_mapping,
        has_energy_value,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )

    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        carbohydrates=nomenclature_response.get('carbohydrates', None),
        proteins=nomenclature_response.get('proteins', None),
        fats=nomenclature_response.get('fats', None),
        calories_value=nomenclature_response.get('calories_value', None),
        calories_unit=nomenclature_response.get('calories_unit', None),
        description_general=DESCRIPTION_WITH_BOLD,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1

    detailed_data = resp.json()['detailed_data']

    if has_energy_value:
        assert detailed_data[3]['type'] == SEPARATOR
        assert detailed_data[4]['type'] == HEADER_TYPE
        assert detailed_data[5]['payload'] == expected_energy_values
        assert detailed_data[5]['type'] == ENERGY_VALUES_TYPE
    else:
        assert len(detailed_data) == 3


@pytest.mark.parametrize(
    'energy_values_enabled, energy_values',
    [
        pytest.param(
            True,
            {},
            marks=experiments.ENERGY_VALUES_ENABLED,
            id='without PCF',
        ),
        pytest.param(
            False,
            {
                'fats': '11.0',
                'proteins': '17.0',
                'carbohydrates': '1.5',
                'calories_value': '170.0',
                'calories_unit': 'ккал',
            },
            marks=experiments.ENERGY_VALUES_DISABLED,
            id='exp off',
        ),
    ],
)
async def test_menu_product_energy_values_absent(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        energy_values_enabled,
        energy_values,
        add_default_product_mapping,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )

    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        carbohydrates=energy_values.get('carbohydrates', None),
        proteins=energy_values.get('proteins', None),
        fats=energy_values.get('fats', None),
        calories_value=energy_values.get('calories_value', None),
        calories_unit=energy_values.get('calories_unit', None),
        description_general=DESCRIPTION_WITH_BOLD,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    detailed_data = resp.json()['detailed_data']

    assert [data['type'] for data in detailed_data] == [
        GALLERY,
        HEADER_TYPE,
        DESCRIPTION_TYPE,
    ]

    assert len(detailed_data) == 3


@experiments.ENERGY_VALUES_ENABLED
@experiments.UPSELL_RECOMMENDATIONS_ENABLED
@pytest.mark.parametrize(
    'is_upsell_above_descriptions',
    [
        pytest.param(
            False, marks=experiments.is_upsell_above_descriptions(False),
        ),
        pytest.param(
            True, marks=experiments.is_upsell_above_descriptions(True),
        ),
        pytest.param(False, id='without exp'),
    ],
)
async def test_menu_product_energy_values_and_recommendations_exist(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
        is_upsell_above_descriptions,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        carbohydrates='1.5',
        proteins='17.0',
        fats='11.0',
        calories_value='170.0',
        calories_unit='ккал',
        description_general=DESCRIPTION_WITH_BOLD,
    )

    mock_upsell_recommendations.add_recommendations(
        upsell.DEFAULT_RECOMMENDATIONS,
    )

    for public_id in PRODUCT_PUBLIC_IDS:
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=100, is_available=True, old_price=None,
        )
        mock_nomenclature_static_info_context.add_product(public_id)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
    assert mock_upsell_recommendations.times_called == 1

    detailed_data = resp.json()['detailed_data']

    if is_upsell_above_descriptions:
        expected_order = [
            GALLERY,
            HEADER_TYPE,
            ENERGY_VALUES_TYPE,
            # energy_values before recommendations
            SEPARATOR,
            RECOMMENDATIONS_TYPE,
            SEPARATOR,
            # upsell above descriptions
            HEADER_TYPE,
            DESCRIPTION,
        ]
    else:
        expected_order = [
            GALLERY,
            HEADER_TYPE,
            DESCRIPTION,
            SEPARATOR,
            HEADER_TYPE,
            ENERGY_VALUES_TYPE,
            # energy_values before recommendations
            SEPARATOR,
            RECOMMENDATIONS_TYPE,
        ]

    response_order = []
    for item in detailed_data:
        response_order.append(item['type'])

    assert expected_order == response_order


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_parent_categories_for_upsell(
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        taxi_eats_products,
        mockserver,
        add_default_product_mapping,
):
    """
    Тест проверяет, что передаются в сервис eats-upsell
    все родительские категории, а не только прямой родитель
    """

    @mockserver.json_handler(utils.Handlers.UPSELL_RECOMMENDATIONS)
    def recommendations(request):
        item = request.json['item']
        assert 'public_category_ids' in item
        assert len(item['public_category_ids']) > 1
        assert sorted(item['public_category_ids']) == sorted(
            ['nearest_parent', 'middle_parent', 'top_parent'],
        )

    mock_nomenclature_get_parent_context.add_category(
        'nearest_parent', 'foo1', 'middle_parent',
    )
    mock_nomenclature_get_parent_context.add_category(
        'middle_parent', 'foo2', 'top_parent',
    )
    mock_nomenclature_get_parent_context.add_category(
        'top_parent', 'foo3', None,
    )
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        price=100,
        is_available=True,
        old_price=None,
        parent_category_ids=['nearest_parent'],
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=DESCRIPTION_WITH_BOLD,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert response.status_code == 200
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
    assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert recommendations.times_called == 1


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
async def test_menu_product_upsell_recommendations_has_categories(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
):
    """
    Тест проверяет, что в ручку рекомендаций дополнительно отправляются
    категории товара, к которому должны что-то порекомендовать.
    """

    # NOTE(udalovmax): Родительские категории товара, которые должны
    # быть переданы на вход в ручку рекомендаций.
    categories = ['1', '2', '3']

    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        price=100,
        is_available=True,
        old_price=None,
        parent_category_ids=categories,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=DESCRIPTION_WITH_BOLD,
    )

    mock_upsell_recommendations.add_recommendations(
        upsell.DEFAULT_RECOMMENDATIONS,
    )

    # NOTE(udalovmax): Устанавливаем проверку, что категории в запросе должны
    # соответствовать родительским категориям товара.
    mock_upsell_recommendations.set_expected_item_categories(categories)

    for public_id in PRODUCT_PUBLIC_IDS:
        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=100, is_available=True, old_price=None,
        )
        mock_nomenclature_static_info_context.add_product(public_id)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert response.status_code == 200
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
    assert mock_upsell_recommendations.times_called == 1


@pytest.mark.parametrize(
    'code_sign, has_currency_in_db',
    [
        pytest.param(
            {'code': 'BYN', 'sign': 'Br'},
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS=(
                        {'1': {'code': 'BYN', 'sign': 'Br'}}
                    ),
                )
            ),
            id='with currency',
        ),
        pytest.param(
            {'code': 'USD', 'sign': '$'},
            False,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS={
                        '__default__': {'code': 'USD', 'sign': '$'},
                    },
                )
            ),
            id='changed default currency',
        ),
        pytest.param(
            {'code': 'BYN', 'sign': 'Br'},
            True,
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_CURRENCY_SETTINGS=(
                        {'1': {'code': 'USD', 'sign': '$'}}
                    ),
                )
            ),
            id='with currency db',
        ),
        pytest.param(
            {'code': 'USD', 'sign': '$'},
            True,
            id='changed default currency db',
        ),
        pytest.param(
            {'code': 'RUB', 'sign': '₽'}, False, id='default currency',
        ),
    ],
)
async def test_menu_product_currency(
        taxi_eats_products,
        code_sign,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        sql_set_place_currency,
        has_currency_in_db,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    if has_currency_in_db:
        sql_set_place_currency(code=code_sign['code'], sign=code_sign['sign'])

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    place_currency = resp.json()['place']['currency']
    assert place_currency['code'] == code_sign['code']
    assert place_currency['sign'] == code_sign['sign']


@utils.PARAMETRIZE_WEIGHT_DATA_ROUNDING
@experiments.weight_data()
async def test_menu_product_weight_data_rounding(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        should_round_prices,
):
    add_default_product_mapping()

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=101,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, measure={'unit': 'KGRM', 'value': 3},
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert response.status_code == 200
    item = response.json()['menu_item']
    assert item['weight_data'] == {
        'price_per_kg': '34' if should_round_prices else '33.67',
        'promo_price_per_kg': '34' if should_round_prices else '33.33',
        'quantim_value_g': 3000,
    }


@experiments.weight_data()
async def test_menu_product_weight_data(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
):
    add_default_product_mapping()

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=150,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, measure={'unit': 'GRM', 'value': 250},
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert response.status_code == 200
    item = response.json()['menu_item']
    assert item['weight_data'] == {
        'price_per_kg': '600',
        'promo_price_per_kg': '400',
        'quantim_value_g': 250,
    }


@experiments.weight_data()
@experiments.ENERGY_VALUES_ENABLED
@pytest.mark.config(
    EATS_PRODUCTS_COLOR_SETTINGS_FOR_PRODUCT_CARD=COLOR_SETTINGS,
)
@pytest.mark.parametrize(
    'name_and_about_product_widgets_enabled',
    [
        pytest.param(True, marks=experiments.product_card_widgets(True)),
        pytest.param(False, marks=experiments.product_card_widgets(False)),
    ],
)
async def test_menu_product_card_widgets(
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        name_and_about_product_widgets_enabled,
):
    """
    Тест проверяет, что если включен эксп по отображению
    названия товара и веса в виджете, то эти поля есть в
    ответе ручки.
    """
    add_default_product_mapping()

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=150,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        name='test_name',
        measure={'unit': 'GRM', 'value': 250},
        carbohydrates='1.5',
        proteins='17.0',
        fats='11.0',
        calories_value='170.0',
        calories_unit='ккал',
        description_general=DESCRIPTION_WITH_BOLD,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert response.status_code == 200

    detailed_data = response.json()['detailed_data']
    if name_and_about_product_widgets_enabled:
        title = detailed_data[1]['payload']['title']
        subtitle = detailed_data[1]['payload']['subtitle']
        assert title['value'] == 'test_name'
        assert title['color'] == COLOR_SETTINGS['title_color']
        assert subtitle['value'] == '250 г'
        assert subtitle['color'] == COLOR_SETTINGS['subtitle_color']
        expected_order = [
            GALLERY,
            PRODUCT_NAME,
            HEADER_TYPE,
            ENERGY_VALUES_TYPE,
            PRODUCT_DETAILS,
        ]
    else:
        expected_order = [
            GALLERY,
            HEADER_TYPE,
            DESCRIPTION,
            SEPARATOR,
            HEADER_TYPE,
            ENERGY_VALUES_TYPE,
        ]

    assert [item['type'] for item in detailed_data] == expected_order


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
        {'placeholder_url': 'https://avatars.mdst.yandex.net/placeholder_url'}
    ),
)
async def test_menu_product_picture_placeholder(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
):
    """
    Тест проверяет, что если в ответе номенклатуры не пришли картинки,
    то возьмется плейсхолдер из конфига.
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, images=[],
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    detailed_data = resp.json()['detailed_data']
    pictures = detailed_data[0]['payload']['pictures'][0]

    assert (
        pictures['url']
        == 'https://avatars.mdst.yandex.net/placeholder_url/{w}x{h}'
    )
    assert pictures['scale'] == 'aspect_fit'


@pytest.mark.parametrize(
    'menu_request',
    [
        pytest.param(
            {'place_slug': '&', 'product_core_id': '0'}, id='wrong_slug_1',
        ),
        pytest.param(
            {'place_slug': 'ghjijhj_2&', 'product_core_id': '0'},
            id='wrong_slug_2',
        ),
        pytest.param(
            {'place_slug': 'ghjijhj_2 ', 'product_core_id': '0'},
            id='wrong_slug_3',
        ),
        pytest.param(
            {'place_slug': 'ghjijhj_2о', 'product_core_id': '0'},
            id='wrong_slug_4',
        ),
        pytest.param(
            {'place_slug': '', 'product_core_id': '0'}, id='wrong_slug_5',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_core_id': ''},
            id='wrong_core_id_1',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_core_id': '--'},
            id='wrong_core_id_2',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_core_id': 'abc'},
            id='wrong_core_id_3',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_core_id': '%'},
            id='wrong_core_id_4',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_core_id': '0-'},
            id='wrong_core_id_4',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_public_id': ''},
            id='wrong_public_id_1',
        ),
        pytest.param(
            {'place_slug': 'slug', 'product_public_id': '!'},
            id='wrong_public_id_2',
        ),
        pytest.param(
            {
                'place_slug': 'slug',
                'product_public_id': (
                    '93272d8b-6b72-46af-af88-4c6b4631175c"980233%40'
                ),
            },
            id='wrong_public_id_3',
        ),
    ],
)
async def test_get_product_wrong_request(taxi_eats_products, menu_request):
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=menu_request,
    )
    assert response.status_code == 400


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
@pytest.mark.parametrize(
    'upsell_recommendations ',
    [
        pytest.param([], id='no recommendations'),
        pytest.param(
            [
                upsell.Recommendation(
                    public_id='1', source=upsell.Source.Complement,
                ),
            ],
            id='single recommendation',
        ),
        pytest.param(
            [
                upsell.Recommendation(
                    public_id='1', source=upsell.Source.Complement,
                ),
                upsell.Recommendation(
                    public_id='2', source=upsell.Source.Complement,
                ),
                upsell.Recommendation(
                    public_id='3', source=upsell.Source.Complement,
                ),
            ],
            id='only complements',
        ),
        pytest.param(
            [
                upsell.Recommendation(
                    public_id='3', source=upsell.Source.Advert,
                ),
                upsell.Recommendation(
                    public_id='1', source=upsell.Source.Advert,
                ),
                upsell.Recommendation(
                    public_id='2', source=upsell.Source.Advert,
                ),
            ],
            id='only adverts',
        ),
        pytest.param(
            [
                upsell.Recommendation(
                    public_id='6', source=upsell.Source.Complement,
                ),
                upsell.Recommendation(
                    public_id='1', source=upsell.Source.Advert,
                ),
                upsell.Recommendation(
                    public_id='3', source=upsell.Source.Complement,
                ),
                upsell.Recommendation(
                    public_id='5', source=upsell.Source.Advert,
                ),
                upsell.Recommendation(
                    public_id='2', source=upsell.Source.Complement,
                ),
                upsell.Recommendation(
                    public_id='4', source=upsell.Source.Advert,
                ),
            ],
            id='mixed recommendations in weird order',
        ),
    ],
)
async def test_menu_products_preserve_upsell_recommendations_order(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_upsell_recommendations,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
        upsell_recommendations: typing.List[upsell.Recommendation],
):
    """
    EDACAT-2508: тест проверяет, что в рекомендациях будет сохранен
    оригинальный порядок товаров таким, как его вернул eats-upsell.
    """

    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general=DESCRIPTION_WITH_BOLD,
    )

    mock_upsell_recommendations.add_recommendations(upsell_recommendations)

    ids_mapping: typing.List[conftest.ProductMapping] = []

    for upsell_recommendation in upsell_recommendations:
        public_id = upsell_recommendation.public_id

        mock_nomenclature_dynamic_info_context.add_product(
            public_id, price=100, is_available=True, old_price=None,
        )
        mock_nomenclature_static_info_context.add_product(
            public_id, description_general=DESCRIPTION_WITH_BOLD,
        )

        ids_mapping.append(
            conftest.ProductMapping(
                origin_id=public_id,
                core_id=len(ids_mapping) + 1,
                public_id=public_id,
            ),
        )

    add_place_products_mapping(ids_mapping)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        headers=HEADERS,
        json={'place_slug': SLUG, 'product_public_id': PRODUCT_PUBLIC_ID},
    )
    assert response.status_code == 200

    detailed_data = response.json()['detailed_data']
    assert detailed_data

    recommendations = menu_product_response.find_recommendations(detailed_data)
    actual_recommendations = menu_product_response.merge_recommendations(
        recommendations,
    )

    assert upsell_recommendations == actual_recommendations


DEFAULT_WARNING_KEY = 'slug.alcohol.warning_text'
WARNING_KEY = 'slug.alcohol.test_warning_text'
SERVICE_ALCOHOL_CONFIG = 'eats-catalog'

TRANSLATIONS = {
    SERVICE_ALCOHOL_CONFIG: {
        WARNING_KEY: {'ru': WARNING_KEY},
        DEFAULT_WARNING_KEY: {'ru': DEFAULT_WARNING_KEY},
    },
}

BRAND_ID_1 = '1'
BRAND_ID_2 = '2'


def make_warning_config(key: str = '', value: str = ''):
    return {
        key: value,
        'rules': '',
        'licenses': '',
        'rules_with_storage_info': {
            'full': {'title': 'test_some_title', 'text': 'test_some_text'},
        },
        'storage_time': 1,
    }


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize('is_alcohol', [True, False])
@pytest.mark.parametrize(
    ['config_expected'],
    [
        pytest.param(
            WARNING_KEY,
            id='with_warning_in_config',
            marks=pytest.mark.config(
                EATS_RETAIL_ALCOHOL_SHOPS={
                    BRAND_ID_1: make_warning_config('warning', WARNING_KEY),
                },
            ),
        ),
        pytest.param(
            DEFAULT_WARNING_KEY,
            id='without_warning_in_config',
            marks=pytest.mark.config(
                EATS_RETAIL_ALCOHOL_SHOPS={BRAND_ID_1: make_warning_config()},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'name_and_about_product_widgets_enabled',
    [
        pytest.param(True, marks=experiments.product_card_widgets(True)),
        pytest.param(False, marks=experiments.product_card_widgets(False)),
    ],
)
async def test_menu_product_note_alcohol_warning(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        is_alcohol,
        config_expected,
        name_and_about_product_widgets_enabled,
):
    """
    если товар алкогольный (флаг is_alcohol), то в detailed_data, после gallery
    будет добавлен Note с предупреждением о вреде алкоголя
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        description_general=DESCRIPTION_WITH_BOLD,
        is_alcohol=is_alcohol,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert resp.status_code == 200

    items = resp.json()['detailed_data']
    assert items

    if is_alcohol:
        assert items[1]['type'] == 'note'
        note = items[1]['payload']
        expected_warning_description = TRANSLATIONS[SERVICE_ALCOHOL_CONFIG][
            config_expected
        ]['ru']
        assert note['text'] == expected_warning_description

        expected_order = [GALLERY, 'note']
        if name_and_about_product_widgets_enabled:
            expected_order.extend([PRODUCT_NAME, PRODUCT_DETAILS])
        else:
            expected_order.extend([HEADER_TYPE, DESCRIPTION])
    else:
        for item in items:
            assert item['type'] != 'note'

        expected_order = [GALLERY]
        if name_and_about_product_widgets_enabled:
            expected_order.extend([PRODUCT_NAME, PRODUCT_DETAILS])
        else:
            expected_order.extend([HEADER_TYPE, DESCRIPTION])

    assert [item['type'] for item in items] == expected_order


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize('is_alcohol', [True, False])
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            id='without_warning_in_config',
            marks=pytest.mark.config(
                EATS_RETAIL_ALCOHOL_SHOPS={
                    BRAND_ID_2: make_warning_config('warning', WARNING_KEY),
                },
            ),
        ),
        pytest.param(id='without_config'),
    ],
)
async def test_menu_product_note_alcohol_warning_wo_brand(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        is_alcohol,
):
    """
    если товар алкогольный (флаг is_alcohol), и бренда нет в конфигах
    для этого продуккта, то в detailed_data не добавляем Note
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID,
        description_general=DESCRIPTION_WITH_BOLD,
        is_alcohol=is_alcohol,
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )

    assert resp.status_code == 200

    items = resp.json()['detailed_data']
    assert items
    for item in items:
        assert item['type'] != 'note'
