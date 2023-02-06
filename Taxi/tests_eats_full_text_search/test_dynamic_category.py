import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


DYN_REPEAT_CATEGORY_ID = 44004
DYN_REPEAT_CATEGORY_TITLE = 'Вы уже заказывали'
DYN_DISCOUNT_CATEGORY_ID = 44008
DYN_DISCOUNT_CATEGORY_TITLE = 'Скидки'
DYN_CASHBACK_CATEGORY_ID = 1000000
DYN_CASHBACK_CATEGORY_TITLE = 'Товары с кешбеком'

EATS_USER_ID = 'user_id=123'

EATS_PRODUCTS_DYNAMIC_CATEGORIES = {
    'popular': {'enabled': False, 'id': 0, 'name': 'Популярное'},
    'discount': {
        'id': DYN_DISCOUNT_CATEGORY_ID,
        'name': DYN_DISCOUNT_CATEGORY_TITLE,
    },
    'repeat': {
        'id': DYN_REPEAT_CATEGORY_ID,
        'name': DYN_REPEAT_CATEGORY_TITLE,
    },
    'cashback': {
        'id': DYN_CASHBACK_CATEGORY_ID,
        'name': DYN_CASHBACK_CATEGORY_TITLE,
    },
}


def fts_item_gen(place_slug):
    return {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
    }


def fts_goods_get_request_gen(category_id):
    return {
        'latitude': 0.0,
        'longitude': 0.0,
        'text': 'My Search Text',
        'category': category_id,
    }


def fts_goods_get_response_gen(category_id, category_title, is_category_found):
    items = [
        {
            'adult': True,
            'ancestors': [
                {
                    'available': True,
                    'gallery': [],
                    'id': 100,
                    'name': 'My Search Category',
                    'parentId': None,
                    'schedule': None,
                },
            ],
            'available': True,
            'description': 'Some item description',
            'id': 10,
            'inStock': None,
            'name': 'My Search Item',
            'optionGroups': [],
            'picture': None,
            'price': 100,
            'decimalPrice': '100',
            'promoPrice': None,
            'decimalPromoPrice': None,
            'promoTypes': [],
            'shippingType': 'delivery',
            'weight': None,
        },
    ]

    return {
        'meta': {},
        'payload': [
            {
                'scopeType': 'category',
                'scopeBoundary': category_id,
                'itemsType': {'title': category_title, 'type': 'category'},
                'items': [],
            },
            {
                'scopeType': 'category',
                'scopeBoundary': category_id,
                'itemsType': {'title': 'Товары', 'type': 'item'},
                'items': items if is_category_found else [],
            },
            {
                'scopeType': 'catalog',
                'scopeBoundary': None,
                'itemsType': {'title': 'Другие категории', 'type': 'category'},
                'items': [],
            },
            {
                'scopeType': 'catalog',
                'scopeBoundary': None,
                'itemsType': {
                    'title': 'Совпадения в других категориях',
                    'type': 'item',
                },
                'items': items if not is_category_found else [],
            },
        ],
    }


@pytest.mark.parametrize(
    'fts_request, fts_status_code, fts_response, products_response',
    [
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                True,
            ),
            'products_discount_category.json',
            id='discount category',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_REPEAT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_REPEAT_CATEGORY_ID), DYN_REPEAT_CATEGORY_TITLE, True,
            ),
            'products_discount_category.json',
            id='repeat category',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_CASHBACK_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_CASHBACK_CATEGORY_ID),
                DYN_CASHBACK_CATEGORY_TITLE,
                True,
            ),
            'products_discount_category.json',
            id='cashback category',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                False,
            ),
            {},
            id='empty response from products',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                False,
            ),
            {'categories': []},
            id='category not found in products',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                False,
            ),
            400,
            id='bad request to products',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                False,
            ),
            404,
            id='place not found in products',
        ),
        pytest.param(
            fts_goods_get_request_gen(DYN_DISCOUNT_CATEGORY_ID),
            200,
            fts_goods_get_response_gen(
                str(DYN_DISCOUNT_CATEGORY_ID),
                DYN_DISCOUNT_CATEGORY_TITLE,
                False,
            ),
            500,
            id='error in products',
        ),
    ],
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=EATS_PRODUCTS_DYNAMIC_CATEGORIES,
)
@translations.DEFAULT
async def test_dynamic_category_goods_get(
        taxi_eats_full_text_search,
        mockserver,
        fts_request,
        fts_status_code,
        fts_response,
        products_response,
        load_json,
):
    """
    Тест проверяет, что товар из динамической категории
    находится и попадает в правильный блок.
    """

    place_slug = 'my_place_slug'

    item = fts_item_gen(place_slug)

    item_url = '/{}/items/{}'.format(
        item['place_slug'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    @mockserver.json_handler(
        '/eats-products/api/v1/for-search/place/dynamic_categories',
    )
    def _products(request):
        if isinstance(products_response, int):
            return mockserver.make_response(status=products_response)
        if (
                isinstance(products_response, str)
                and products_response.find('.json') != -1
        ):
            return load_json(products_response)
        return products_response

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{}'.format(place_slug), params=fts_request,
    )

    assert _products.times_called == 1
    assert _nomenclature.times_called == 1
    assert response.status_code == fts_status_code
    assert response.json() == fts_response


def fts_search_post_request_gen(category_id):
    return {
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'text': 'My Search Text',
        'place_slug': 'my_place_slug',
        'category': category_id,
    }


def fts_search_post_response_gen(category_title, is_category_found):
    payload = [
        {
            'adult': True,
            'description': 'Some item description',
            'id': '10',
            'public_id': 'N_10',
            'option_groups': [],
            'price': 100,
            'decimal_price': '100',
            'shipping_type': 'delivery',
            'title': 'My Search Item',
        },
    ]

    response = {
        'blocks': [
            {'payload': [], 'title': category_title, 'type': 'categories'},
            {
                'payload': payload if is_category_found else [],
                'title': 'Товары',
                'type': 'items',
            },
            {'payload': [], 'title': 'Другие категории', 'type': 'categories'},
            {
                'payload': payload if not is_category_found else [],
                'title': 'Совпадения в других категориях',
                'type': 'items',
            },
        ],
    }

    if not is_category_found:
        response['header'] = {
            'text': 'В категории "' + category_title + '" ничего не найдено',
        }

    return response


@pytest.mark.parametrize(
    'fts_request, fts_status_code, fts_response, products_response',
    [
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, True),
            'products_discount_category.json',
            id='discount category',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_REPEAT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_REPEAT_CATEGORY_TITLE, True),
            'products_discount_category.json',
            id='repeat category',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_CASHBACK_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_CASHBACK_CATEGORY_TITLE, True),
            'products_discount_category.json',
            id='cashback category',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, False),
            {},
            id='empty response from products',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, False),
            {'categories': []},
            id='category not found in products',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, False),
            400,
            id='bad request to products',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, False),
            404,
            id='place not found in products',
        ),
        pytest.param(
            fts_search_post_request_gen(str(DYN_DISCOUNT_CATEGORY_ID)),
            200,
            fts_search_post_response_gen(DYN_DISCOUNT_CATEGORY_TITLE, False),
            500,
            id='error in products',
        ),
    ],
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@translations.DEFAULT
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=EATS_PRODUCTS_DYNAMIC_CATEGORIES,
)
async def test_dynamic_category_search(
        taxi_eats_full_text_search,
        mockserver,
        fts_request,
        fts_status_code,
        fts_response,
        products_response,
        load_json,
):
    """
    Тест проверяет, что товар из динамической категории
    находится и попадает в правильный блок.
    """

    place_slug = 'my_place_slug'

    item = fts_item_gen(place_slug)

    item_url = '/{}/items/{}'.format(
        item['place_slug'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    @mockserver.json_handler(
        '/eats-products/api/v1/for-search/place/dynamic_categories',
    )
    def _products(request):
        assert 'X-Eats-User' in request.headers
        assert request.headers['X-Eats-User'] == EATS_USER_ID
        if isinstance(products_response, int):
            return mockserver.make_response(status=products_response)
        if (
                isinstance(products_response, str)
                and products_response.find('.json') != -1
        ):
            return load_json(products_response)
        return products_response

    headers = utils.get_headers()
    headers['X-Eats-User'] = EATS_USER_ID
    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=headers,
    )

    assert _products.times_called == 1
    assert _nomenclature.times_called == 1
    assert response.status_code == fts_status_code
    assert response.json() == fts_response
