import copy

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

DEFAULT_REQUEST = {'slug': 'slug'}
CATEGORY_REQUEST = {**DEFAULT_REQUEST, 'category_uid': '1'}

CASHBACK_CATEGORY_ID = str(utils.CASHBACK_CATEGORY_ID)
DISCOUNT_CATEGORY_ID = str(utils.DISCOUNT_CATEGORY_ID)
REPEAT_CATEGORY_ID = str(utils.REPEAT_CATEGORY_ID)
REPEAT_THIS_BRAND_ID = str(utils.REPEAT_THIS_BRAND_ID)
REPEAT_OTHER_BRANDS_ID = str(utils.REPEAT_OTHER_BRANDS_ID)
EATER_ID = '12345'
PRODUCTS_HEADERS = {'X-Eats-User': f'user_id={EATER_ID}'}
PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
]
SKU_ID = 'sku_id_1'


@experiments.communications(
    main_shop_informers_enabled=True, main_shop_stories_enabled=True,
)
async def test_menu_goods_informers_stories_shop_main_page(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение информеров и сториз на главной магазина,
    то ответе будут информеры и стори из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )

    story = utils.make_communications_story('1')
    informers = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert set(request.json['types']) == set(['informers', 'stories'])
        assert request.json['screen'] == 'shop_main_page'
        return {'payload': {'stories': [story], 'informers': informers}}

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=DEFAULT_REQUEST,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    assert response.json()['payload']['communications'] == {
        'informers': informers,
        'story': story,
    }


@pytest.mark.parametrize(
    'status_code', [400, 429, 500, 'timeout', 'network_error', 'bad_format'],
)
@experiments.communications(
    main_shop_informers_enabled=True, main_shop_stories_enabled=True,
)
async def test_menu_goods_informers_stories_shop_main_bad_response(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
        status_code,
):
    """
    Если в конфиге включено получение информеров и сториз на главной магазина,
    но eats-communications вернуло какой-то плохой ответ, то ручка вернет 200
    без коммуникаций
    """
    sql_add_brand()
    sql_add_place()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_screen_communications(request):
        if status_code == 'timeout':
            raise mockserver.TimeoutError()
        if status_code == 'network_error':
            raise mockserver.NetworkError()
        elif status_code == 'bad_format':
            return {'payload': {'bad_format': 'bad_format'}}
        return mockserver.make_response(status=status_code)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=DEFAULT_REQUEST,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    assert mock_screen_communications.times_called == 1
    assert 'communications' not in payload
    assert 'communications' not in payload['categories'][0]


@experiments.communications(
    categories_informers_enabled=True, categories_stories_enabled=True,
)
async def test_menu_goods_informers_stories_categories(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        mock_v1_nomenclature_context,
):
    """
    Если в конфиге включено получение сториз и информеров в категориях,
    то ответе в категориях будут сториз и информеры из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    # категория с 1 информером
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )
    # категория с 2 информерами
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory(
            'category_id_2', 'Фрукты', public_id=2, parent_id='1',
        ),
    )

    story_1 = utils.make_communications_story('1')
    story_2 = utils.make_communications_story('2')
    informers_1 = [utils.make_text_image_informer('1')]
    informers_2 = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert set(request.json['types']) == set(['informers', 'stories'])
        assert request.json['screen'] == 'shop_category'

        return {
            'payload': [
                {
                    'category_id': '1',
                    'payload': {
                        'stories': [story_1],
                        'informers': informers_1,
                    },
                },
                {
                    'category_id': '2',
                    'payload': {
                        'stories': [story_2],
                        'informers': informers_2,
                    },
                },
            ],
        }

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=CATEGORY_REQUEST,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 2
    assert categories[0]['communications'] == {
        'informers': informers_1,
        'story': story_1,
    }
    assert categories[1]['communications'] == {
        'informers': informers_2,
        'story': story_2,
    }


@pytest.mark.parametrize(
    ['stories_enabled', 'informers_enabled'],
    [
        pytest.param(
            False,
            False,
            id='all disabled',
            marks=experiments.communications(),
        ),
        pytest.param(
            True,
            False,
            id='only stories',
            marks=experiments.communications(categories_stories_enabled=True),
        ),
        pytest.param(
            False,
            True,
            id='only informers',
            marks=experiments.communications(
                categories_informers_enabled=True,
            ),
        ),
        pytest.param(
            True,
            True,
            id='stories and informers',
            marks=experiments.communications(
                categories_stories_enabled=True,
                categories_informers_enabled=True,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'category_id',
    [CASHBACK_CATEGORY_ID, DISCOUNT_CATEGORY_ID, REPEAT_CATEGORY_ID],
)
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.discount_category()
@experiments.repeat_category(version='v1')
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        cashback_enabled=True, discount_enabled=True, repeat_enabled=True,
    ),
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
        {
            'get_cashback_category_version': 'v2',
            'repeat_category_handlers_version': 'v2',
        }
    ),
)
async def test_menu_goods_informers_stories_dynamic_categories(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        cache_add_discount_product,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_v2_match_discounts_context,
        mock_retail_categories_brand_orders_history,
        category_id,
        stories_enabled,
        informers_enabled,
):
    """
    Если в конфиге включено получение сториз и/или информеров в категориях,
    то в ответе динамических категорий (Скидки, Кешбек, Вы заказывали)
    будут эти коммуникации
    """
    sql_add_brand()
    sql_add_place()
    cache_add_discount_product('item_id_1')
    add_default_product_mapping()

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])

    expected_communications = {'informers': []}
    expected_types = []
    if stories_enabled:
        stories = [
            utils.make_communications_story('2'),
            utils.make_communications_story('3'),
        ]
        expected_communications['story'] = stories[0]
        expected_types.append('stories')
    else:
        stories = []
    if informers_enabled:
        informers = [
            utils.make_text_image_informer('5'),
            utils.make_background_informer('6'),
        ]
        expected_communications['informers'] = informers
        expected_types.append('informers')
    else:
        informers = []

    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.BRAND_ID, PUBLIC_IDS[0], 1,
    )

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert set(request.json['types']) == set(expected_types)
        assert request.json['screen'] == 'shop_category'
        assert request.json['categories'] == [{'category_id': category_id}]
        return {
            'payload': [
                {
                    'category_id': category_id,
                    'payload': {'stories': stories, 'informers': informers},
                },
            ],
        }

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['category_uid'] = category_id

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers=PRODUCTS_HEADERS,
    )
    has_communications = stories_enabled or informers_enabled
    assert mock_eats_communications.times_called == (
        1 if has_communications else 0
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    if has_communications:
        assert categories[0]['communications'] == expected_communications
    else:
        assert 'communications' not in categories[0]


@pytest.mark.parametrize(
    'category_id',
    ['1', CASHBACK_CATEGORY_ID, DISCOUNT_CATEGORY_ID, REPEAT_CATEGORY_ID],
)
@pytest.mark.parametrize('status', [400, 429, 500, 'timeout', 'bad_format'])
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@experiments.CASHBACK_CATEGORY_ENABLED
@experiments.discount_category()
@experiments.repeat_category(version='v1')
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        cashback_enabled=True, discount_enabled=True, repeat_enabled=True,
    ),
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
        {
            'get_cashback_category_version': 'v2',
            'repeat_category_handlers_version': 'v2',
        }
    ),
)
@experiments.communications(
    main_shop_stories_enabled=True,
    categories_stories_enabled=True,
    main_shop_informers_enabled=True,
    categories_informers_enabled=True,
)
async def test_menu_goods_informers_stories_categories_bad_response(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        cache_add_discount_product,
        mock_v1_nomenclature_context,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_v2_match_discounts_context,
        mock_retail_categories_brand_orders_history,
        status,
        category_id,
):
    """
    Если в конфиге включено получение информеров в категориях магазина, но
    eats-communications вернуло какой-то плохой ответ,
    то ручка вернет 200 без сториз
    """
    sql_add_brand()
    sql_add_place()
    cache_add_discount_product('item_id_1')
    add_default_product_mapping()
    mock_v1_nomenclature_context.add_category(
        conftest.NomenclatureCategory('category_id_1', 'Фрукты', public_id=1),
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[0], value_type='absolute', value=5,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])

    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.BRAND_ID, PUBLIC_IDS[0], 1,
    )

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_communications_categories(request):
        if status == 'timeout':
            raise mockserver.TimeoutError()
        elif status == 'bad_format':
            return {'payload': {'bad_payload': 'bad_payload'}}
        return mockserver.make_response(status=status)

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['category_uid'] = category_id

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=CATEGORY_REQUEST,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    assert mock_communications_categories.times_called == 1
    assert 'communications' not in payload
    assert 'communications' not in payload['categories'][0]


@pytest.mark.parametrize(
    'requested_category, result_categories, has_cross_brand_product',
    [
        pytest.param(
            REPEAT_THIS_BRAND_ID,
            {REPEAT_THIS_BRAND_ID},
            True,
            id='requested repeat this brand',
        ),
        pytest.param(
            REPEAT_OTHER_BRANDS_ID,
            {REPEAT_OTHER_BRANDS_ID},
            True,
            id='requested repeat other brands',
        ),
        pytest.param(
            REPEAT_CATEGORY_ID,
            {REPEAT_CATEGORY_ID, REPEAT_THIS_BRAND_ID, REPEAT_OTHER_BRANDS_ID},
            True,
            id='requested repeat with both subcategories',
        ),
        pytest.param(
            REPEAT_CATEGORY_ID,
            {REPEAT_CATEGORY_ID},
            False,
            id='requested repeat, no subcategories',
        ),
    ],
)
@experiments.repeat_category(version='v2')
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        repeat_enabled=True,
        repeat_this_brand_enabled=True,
        repeat_other_brands_enabled=True,
    ),
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
        {'repeat_category_handlers_version': 'v2'}
    ),
)
@experiments.communications(
    categories_stories_enabled=True, categories_informers_enabled=True,
)
async def test_menu_goods_informers_stories_repeat_category_v2(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        make_public_by_sku_id_response,
        requested_category,
        result_categories,
        mock_retail_categories_cross_brand_orders,
        mock_retail_categories_brand_orders_history,
        has_cross_brand_product,
):
    """
    Если в конфиге включено получение информеров и сториз в категориях,
    то ответе динамической катгории Мои покупки будут эти коммуникации
    """
    sql_add_brand()
    sql_add_place()
    add_default_product_mapping()

    for public_id in PUBLIC_IDS:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    if has_cross_brand_product:
        mock_retail_categories_cross_brand_orders.add_product(
            utils.PLACE_ID, PUBLIC_IDS[1], 1, SKU_ID,
        )
    mock_retail_categories_brand_orders_history.add_brand_product(
        utils.BRAND_ID, PUBLIC_IDS[0], 1,
    )

    stories = [
        utils.make_communications_story('2'),
        utils.make_communications_story('3'),
    ]
    informers = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(
            request, {str(utils.PLACE_ID): {SKU_ID: [PUBLIC_IDS[1]]}},
        )

    @mockserver.json_handler(utils.Handlers.CATEGORIES_COMMUNICATIONS)
    def mock_eats_communications(request):
        def sort_by_id(categories):
            sorted(categories, key=lambda item: item['category_id'])

        assert set(request.json['types']) == set(['stories', 'informers'])
        assert request.json['screen'] == 'shop_category'
        expected_categories = []
        payload = []
        for category in result_categories:
            expected_categories.append({'category_id': category})
            payload.append(
                {
                    'category_id': category,
                    'payload': {'stories': stories, 'informers': informers},
                },
            )
        assert sort_by_id(request.json['categories']) == sort_by_id(
            expected_categories,
        )
        return {'payload': payload}

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['category_uid'] = requested_category

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request, headers=PRODUCTS_HEADERS,
    )
    assert mock_eats_communications.times_called == 1
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == len(result_categories)
    for category in categories:
        assert category['communications'] == {
            'story': stories[0],
            'informers': informers,
        }
