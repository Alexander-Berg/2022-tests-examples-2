import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


@pytest.mark.parametrize(
    'request_text,request_category,fts_status_code,fts_response',
    (
        (
            'My Search Text',
            None,
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Категории',
                            'type': 'category',
                        },
                        'items': [
                            {
                                'id': 100,
                                'name': 'My Search Category',
                                'parentId': 200,
                                'schedule': None,
                                'gallery': [{'url': 'URL'}],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                            {
                                'id': 200,
                                'name': 'My Base Category',
                                'parentId': 300,
                                'schedule': None,
                                'gallery': [],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': 50,
                                'decimalPromoPrice': '50',
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': 200,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            'My Search Text',
            200,
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '200',
                        'itemsType': {
                            'title': 'My Base Category',
                            'type': 'category',
                        },
                        'items': [
                            {
                                'id': 100,
                                'name': 'My Search Category',
                                'parentId': 200,
                                'schedule': None,
                                'gallery': [{'url': 'URL'}],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '200',
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': 50,
                                'decimalPromoPrice': '50',
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': 200,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Другие категории',
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Совпадения в других категориях',
                            'type': 'item',
                        },
                        'items': [],
                    },
                ],
            },
        ),
        (
            'My Search Text',
            100,
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '100',
                        'itemsType': {
                            'title': 'My Search Category',
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '100',
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': 50,
                                'decimalPromoPrice': '50',
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': 200,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Другие категории',
                            'type': 'category',
                        },
                        'items': [
                            {
                                'id': 200,
                                'name': 'My Base Category',
                                'parentId': 300,
                                'schedule': None,
                                'gallery': [],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Совпадения в других категориях',
                            'type': 'item',
                        },
                        'items': [],
                    },
                ],
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@translations.DEFAULT
async def test_legacy_response(
        taxi_eats_full_text_search,
        mockserver,
        request_text,
        request_category,
        fts_status_code,
        fts_response,
):
    """
    Проверяем, что сервис пробрасывает запросы до saas
    и формирует ответ на основе ответа saas.
    """

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100,
        'promo_price': 50,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    category = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 100,
        'title': 'My Search Category',
        'gallery': [{'url': 'URL'}],
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    parent_category = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 200,
        'title': 'My Base Category',
        'parent_categories': [
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    parent_category_url = '/{}/categories/{}'.format(
        parent_category['place_id'], parent_category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_SERVICE
        assert int(args['kps']) == SAAS_PREFIX
        assert args['msp'] == SAAS_MISSPELL
        assert args['gta'] == '_AllDocInfos'
        assert args['ms'] == 'proto'
        assert args['hr'] == 'json'
        assert (
            request_text in args['text']
            or request_category
            and str(request_category) in args['text']
        )
        x = utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
                utils.gta_to_document(
                    parent_category_url,
                    utils.category_to_gta(parent_category),
                ),
            ],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        assert request.query['slug'] == place_slug
        json = request.json
        categories = json['categories']
        assert len(categories) == 2
        products = json['products']
        assert len(products) == 1
        assert products[0] == item['nomenclature_item_id']
        return {
            'categories': [
                utils.to_nomenclature_category(category),
                utils.to_nomenclature_category(parent_category),
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    params = {'text': request_text}

    if request_category:
        params['category'] = request_category

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
