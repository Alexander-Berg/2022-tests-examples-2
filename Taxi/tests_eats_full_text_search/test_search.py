import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


@pytest.mark.parametrize('handlers_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            200,
            {
                'blocks': [
                    {
                        'title': 'Категории',
                        'type': 'categories',
                        'payload': [
                            {
                                'id': '100',
                                'title': 'My Search Category',
                                'gallery': [{'url': 'URL'}],
                            },
                        ],
                    },
                    {
                        'title': 'Товары',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '10',
                                'public_id': 'N_10',
                                'title': 'My Search Item',
                                'description': 'Some item description',
                                'in_stock': 2,
                                'price': 100,
                                'decimal_price': '100.99',
                                'adult': False,
                                'weight': '100 г',
                                'gallery': [
                                    {'url': 'URL', 'scale': 'aspect_fit'},
                                ],
                                'option_groups': [],
                                'shipping_type': 'all',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            200,
            {
                'blocks': [
                    {
                        'title': 'Категории',
                        'type': 'categories',
                        'payload': [
                            {
                                'id': '100',
                                'title': 'My Search Category',
                                'gallery': [{'url': 'URL'}],
                            },
                        ],
                    },
                    {
                        'title': 'Товары',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '10',
                                'public_id': 'N_10',
                                'title': 'My Search Item',
                                'in_stock': 2,
                                'price': 100,
                                'decimal_price': '100.99',
                                'adult': False,
                                'weight': '100 г',
                                'gallery': [
                                    {'url': 'URL', 'scale': 'aspect_fit'},
                                ],
                                'description': 'Some item description',
                                'option_groups': [],
                                'shipping_type': 'all',
                            },
                        ],
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
async def test_search(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        fts_request,
        fts_status_code,
        fts_response,
        handlers_version,
):
    """
    Проверяем, что сервис пробрасывает запросы до saas
    и формирует ответ на основе ответа saas.
    """

    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'place_products_info_batch_size': 250,
                'place_categories_get_parents_batch_size': 50,
                'place_settings': {
                    '__default__': {'handlers_version': handlers_version},
                },
            },
        },
    )

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100.99,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': None, 'title': 'Base Category'},
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
            {'id': 200, 'parent_id': None, 'title': 'Base Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
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
        request_category = fts_request.get('category')
        # если в text параметре нет самого текста запроса,
        # то это дополнительный
        # запрос за категорией, проверяем что в нем есть
        # slug и идентификатор категории
        assert fts_request['text'] in args['text'] or (
            request_category
            and str(request_category) in args['text']
            and str(place_slug) in args['text']
        )
        return utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nmn_place_ass_details(request):
        assert request.query['slug'] == place_slug
        json = request.json
        categories = json['categories']
        assert len(categories) == 1
        assert categories[0] == str(category['category_id'])
        products = json['products']
        assert len(products) == 1
        assert products[0] == item['nomenclature_item_id']
        return {
            'categories': [utils.to_nomenclature_category(category)],
            'products': [utils.to_nomenclature_product(item)],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return {
            'places_categories': [
                {
                    'categories': [
                        str(category_id)
                        for category_id in request.json['places_categories'][
                            0
                        ]['categories']
                    ],
                    'place_id': request.json['places_categories'][0][
                        'place_id'
                    ],
                },
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return {
            'products': [
                {
                    'id': item['nomenclature_item_id'],
                    'in_stock': item['in_stock'],
                    'is_available': True,
                    'origin_id': item['origin_id'],
                    'parent_category_ids': ['1'],
                    'price': item['price'],
                },
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': item['adult'],
                    'barcodes': [],
                    'description': {'general': item['description']},
                    'id': item['nomenclature_item_id'],
                    'images': [],
                    'is_catch_weight': True,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': item['title'],
                    'origin_id': item['origin_id'],
                    'place_brand_id': '1',
                    'shipping_type': 'all',
                    'measure': {'value': 100, 'unit': 'GRM'},
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return {
            'categories': [
                {
                    'id': '1',
                    'child_ids': [],
                    'name': 'category_1',
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'products': [],
                },
            ],
        }

    request_id = 'request_id'
    headers = utils.get_headers()
    headers['x-request-id'] = request_id

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=headers,
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
    response_request_id = response.headers.get('x-request-id')
    assert response_request_id is not None
    assert response_request_id == request_id


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@pytest.mark.parametrize(
    'log_enabled, log_times_called',
    [
        pytest.param(False, 0, id='log disabled'),
        pytest.param(True, 1, id='log enabled'),
    ],
)
@translations.DEFAULT
async def test_search_log_response(
        taxi_eats_full_text_search,
        taxi_config,
        mockserver,
        testpoint,
        log_enabled,
        log_times_called,
):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_LOGGING_SETTINGS': {
                'enable': log_enabled,
                'ratio': 1,
            },
        },
    )

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100.99,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': None, 'title': 'Base Category'},
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
            {'id': 200, 'parent_id': None, 'title': 'Base Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [utils.to_nomenclature_category(category)],
            'products': [utils.to_nomenclature_product(item)],
        }

    @testpoint('v1_search_yt_log_response')
    def log_response(data):
        pass

    request_id = 'request_id'
    headers = utils.get_headers()
    headers['x-request-id'] = request_id

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'my_place_slug',
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert log_response.times_called == log_times_called


async def test_search_unknown_place(taxi_eats_full_text_search):
    """
    Проверяет, что сервис отвечает 400,
    если передан неизвестный плейс
    """

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'unknown_slug',
        },
        headers=utils.get_headers(),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'UNKNOWN_PLACE',
        'message': 'Menu search possible only in a known shop or restaurant',
    }


@pytest.mark.parametrize(
    'tbs', (pytest.param(None, id='no_tbs'), pytest.param(300, id='with_tbs')),
)
async def test_tbs_param(
        taxi_eats_full_text_search, taxi_config, mockserver, tbs,
):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS': {
                'service': SAAS_SERVICE,
                'prefix': SAAS_PREFIX,
                'misspell': SAAS_MISSPELL,
                'tbs': tbs,
            },
        },
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas_search_proxy(request):
        if tbs:
            assert request.query['pron'] == f'tbs{tbs}'
        else:
            assert 'pron' not in request.query
        return utils.get_saas_response(docs=[])

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    assert response.status_code == 200
    assert saas_search_proxy.times_called > 0
