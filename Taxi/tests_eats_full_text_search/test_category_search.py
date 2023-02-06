import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'

PLACE_SLUG = 'my_place_slug'


@pytest.mark.parametrize('handlers_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': PLACE_SLUG,
                'category': '200',
            },
            200,
            {
                'blocks': [
                    {
                        'title': 'My Base Category',
                        'type': 'categories',
                        'payload': [
                            {'id': '100', 'title': 'My Search Category'},
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
                                'option_groups': [],
                                'price': 100,
                                'decimal_price': '100',
                                'shipping_type': 'delivery',
                                'adult': True,
                            },
                        ],
                    },
                    {
                        'title': 'Другие категории',
                        'type': 'categories',
                        'payload': [],
                    },
                    {
                        'title': 'Совпадения в других категориях',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '50',
                                'public_id': 'N_50',
                                'title': 'Another Item',
                                'description': 'Another item description',
                                'option_groups': [],
                                'shipping_type': 'delivery',
                                'price': 100,
                                'decimal_price': '100',
                                'adult': True,
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
                'place_slug': PLACE_SLUG,
                'category': '100',
            },
            200,
            {
                'blocks': [
                    {
                        'title': 'My Search Category',
                        'type': 'categories',
                        'payload': [],
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
                                'option_groups': [],
                                'shipping_type': 'delivery',
                                'price': 100,
                                'decimal_price': '100',
                                'adult': True,
                            },
                        ],
                    },
                    {
                        'title': 'Другие категории',
                        'type': 'categories',
                        'payload': [
                            {'id': '200', 'title': 'My Base Category'},
                        ],
                    },
                    {
                        'title': 'Совпадения в других категориях',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '50',
                                'public_id': 'N_50',
                                'title': 'Another Item',
                                'description': 'Another item description',
                                'option_groups': [],
                                'shipping_type': 'delivery',
                                'price': 100,
                                'decimal_price': '100',
                                'adult': True,
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
async def test_category_search(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        fts_request,
        fts_status_code,
        fts_response,
        handlers_version,
):
    """
    Проверяем корректность работы поиска по категориями
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

    item = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': None, 'title': 'My Base Category'},
        ],
    }

    another_item = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'categories': [500],
        'nomenclature_item_id': 'N_50',
        'origin_id': 'N_50',
        'title': 'Another Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,
        'description': 'Another item description',
        'parent_categories': [
            {'id': 500, 'parent_id': 600, 'title': '500'},
            {'id': 600, 'parent_id': None, 'title': '600'},
        ],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    another_item_url = '/{}/items/{}'.format(
        another_item['place_id'], another_item['nomenclature_item_id'],
    )

    category = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'category_id': 100,
        'title': 'My Search Category',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': None, 'title': 'My Base Category'},
        ],
    }

    parent_category = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'category_id': 200,
        'title': 'My Base Category',
        'parent_categories': [
            {'id': 200, 'parent_id': None, 'title': 'My Base Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    parent_category_url = '/{}/categories/{}'.format(
        parent_category['place_id'], parent_category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        # если в text параметре нет самого текста запроса,
        # то это дополнительный
        # запрос за категорией, проверяем что в нем есть
        # slug и идентификатор категории
        assert fts_request['text'] in args['text'] or (
            str(fts_request['category']) in args['text']
            and str(PLACE_SLUG) in args['text']
        )
        return utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
                utils.gta_to_document(
                    another_item_url, utils.item_to_gta(another_item),
                ),
                utils.gta_to_document(
                    parent_category_url,
                    utils.category_to_gta(parent_category),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nmn_v2_place_assortment_details(request):
        return {
            'categories': [
                utils.to_nomenclature_category(category),
                utils.to_nomenclature_category(parent_category),
            ],
            'products': [
                utils.to_nomenclature_product(item),
                utils.to_nomenclature_product(another_item),
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return {
            'places_categories': [
                {
                    'categories': [
                        str(category['category_id'])
                        for category in [category, parent_category]
                    ],
                    'place_id': request.json['places_categories'][0][
                        'place_id'
                    ],
                },
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        item_id_to_category_id = {'N_10': '100', 'N_50': '500'}
        return {
            'products': [
                {
                    'id': item['nomenclature_item_id'],
                    'is_available': True,
                    'origin_id': item['origin_id'],
                    'parent_category_ids': [
                        item_id_to_category_id[item['nomenclature_item_id']],
                    ],
                    'price': item['price'],
                }
                for item in [item, another_item]
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': True,
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
                    'shipping_type': 'delivery',
                }
                for item in [item, another_item]
            ],
        }

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return {
            'categories': [
                {
                    'id': str(category['category_id']),
                    'child_ids': (
                        ['100'] if category['category_id'] == 200 else []
                    ),
                    'parent_id': (
                        '200' if category['category_id'] == 100 else None
                    ),
                    'name': category['title'],
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'products': [],
                }
                for category in [category, parent_category]
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
                'category': '200',
            },
            200,
            {
                'header': {
                    'text': (
                        'В категории "My Search Category" ничего не найдено'
                    ),
                },
                'blocks': [
                    {
                        'title': 'My Search Category',
                        'type': 'categories',
                        'payload': [],
                    },
                    {'title': 'Товары', 'type': 'items', 'payload': []},
                    {
                        'title': 'Другие категории',
                        'type': 'categories',
                        'payload': [],
                    },
                    {
                        'title': 'Совпадения в других категориях',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '10',
                                'public_id': 'N_10',
                                'title': 'My Search Item',
                                'description': 'Some item description',
                                'price': 100,
                                'decimal_price': '100',
                                'option_groups': [],
                                'shipping_type': 'delivery',
                                'adult': True,
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
async def test_unescaping(
        taxi_eats_full_text_search,
        mockserver,
        fts_request,
        fts_status_code,
        fts_response,
):
    """
    Проверяем что parent_category коррекно анэскейпится
    """

    item = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,  # delivery
        'description': 'Some item description',
        'parent_categories': (
            '[{'
            '\\"id\\":6322736,'
            '\\"parent_id\\":6322730,'
            '\\"title\\":\\"Консервы\\"'
            '},'
            '{'
            '\\"id\\":6322730,'
            '\\"parent_id\\":null,'
            '\\"title\\":\\"Бакалея\\"'
            '}]'
        ),
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    category = {
        'place_id': 1,
        'place_slug': PLACE_SLUG,
        'category_id': 200,
        'title': 'My Search Category',
        'parent_categories': [
            {'id': 200, 'parent_id': None, 'title': 'My Search Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert (
            fts_request['text'] in args['text']
            or str(fts_request['category']) in args['text']
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
    def _nomenclature(request):
        return {
            'categories': [],
            'products': [utils.to_nomenclature_product(item)],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
