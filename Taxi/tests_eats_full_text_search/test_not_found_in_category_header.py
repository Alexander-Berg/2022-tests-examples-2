import pytest

from . import translations
from . import utils


SUPER_CATEGORY = 'Super Category'

REQUEST = {
    'location': {'latitude': 0.0, 'longitude': 0.0},
    'text': 'My Search Text',
    'place_slug': 'my_place_slug',
    'category': '500',
}

RESPONSE = {
    'header': {
        'text': 'В категории "{}" ничего не найдено'.format(SUPER_CATEGORY),
    },
    'blocks': [
        {'title': SUPER_CATEGORY, 'type': 'categories', 'payload': []},
        {'title': 'Товары', 'type': 'items', 'payload': []},
        {
            'title': 'Другие категории',
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
            'title': 'Совпадения в других категориях',
            'type': 'items',
            'payload': [
                {
                    'id': '10',
                    'public_id': 'N_10',
                    'title': 'My Search Item',
                    'description': 'Some item description',
                    'in_stock': 2,
                    'price': 100,
                    'decimal_price': '100',
                    'adult': False,
                    'weight': '100 г',
                    'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
                    'option_groups': [],
                    'shipping_type': 'all',
                },
            ],
        },
    ],
}


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response', ((REQUEST, 200, RESPONSE),),
)
@translations.DEFAULT
async def test_not_found_in_category_header(
        taxi_eats_full_text_search,
        mockserver,
        fts_request,
        fts_status_code,
        fts_response,
):
    """
    Проверяем, что если в категории в которой велся поиск
    ничео не найдено, формируется поле header с
    надписью "В категории {название категории} ничего не найден"
    (saas - eats_fts, nomenclature_handlers - v1)
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

    category_search = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 500,
        'title': SUPER_CATEGORY,
        'gallery': [{'url': 'URL'}],
        'parent_categories': [{'id': 500, 'title': SUPER_CATEGORY}],
    }

    category_search_url = '/{}/categories/{}'.format(
        category_search['place_id'], category_search['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
                utils.gta_to_document(
                    category_search_url,
                    utils.category_to_gta(category_search),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        assert request.query['slug'] == place_slug
        json = request.json
        categories = json['categories']
        assert len(categories) == 2
        products = json['products']
        assert len(products) == 1
        return {
            'categories': [
                utils.to_nomenclature_category(category),
                utils.to_nomenclature_category(category_search),
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response', ((REQUEST, 200, RESPONSE),),
)
@translations.DEFAULT
@pytest.mark.parametrize(
    'search_category_in_saas_response',
    [
        pytest.param(True, id='saas response contains search category'),
        pytest.param(
            False, id='saas response doesn\'t contain search category',
        ),
    ],
)
async def test_not_found_in_category_header_fts_nmn_v2(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        fts_request,
        fts_status_code,
        fts_response,
        search_category_in_saas_response,
):
    """
    Проверяем, что если в категории в которой велся поиск
    ничео не найдено, формируется поле header с
    надписью "В категории {название категории} ничего не найден"
    (saas - eats_fts, nomenclature_handlers - v2)
    """

    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'place_products_info_batch_size': 250,
                'place_categories_get_parents_batch_size': 50,
                'place_settings': {'__default__': {'handlers_version': 'v2'}},
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
        'price': 100,
        'weight': '100 г',
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

    category_search = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 500,
        'title': SUPER_CATEGORY,
        'gallery': [{'url': 'URL'}],
        'parent_categories': [{'id': 500, 'title': SUPER_CATEGORY}],
    }

    category_search_url = '/{}/categories/{}'.format(
        category_search['place_id'], category_search['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = [
            utils.gta_to_document(item_url, utils.item_to_gta(item)),
            utils.gta_to_document(
                category_url, utils.category_to_gta(category),
            ),
        ]
        if search_category_in_saas_response:
            response.append(
                utils.gta_to_document(
                    category_search_url,
                    utils.category_to_gta(category_search),
                ),
            )
        return utils.get_saas_response(response)

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
                    'id': product_id,
                    'in_stock': 2,
                    'is_available': True,
                    'origin_id': f'origin_id_{product_id}',
                    'parent_category_ids': ['1'],
                    'price': 100,
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': False,
                    'barcodes': [],
                    'description': {'general': 'Some item description'},
                    'id': product_id,
                    'images': [],
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': 'My Search Item',
                    'origin_id': f'origin_id_{product_id}',
                    'place_brand_id': '1',
                    'shipping_type': 'all',
                    'measure': {'value': 100, 'unit': 'GRM'},
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        category_to_name = {
            '1': category['title'],
            '500': category_search['title'],
        }
        return {
            'categories': [
                {
                    'id': category_id,
                    'child_ids': [],
                    'name': category_to_name[category_id],
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'products': [],
                }
                for category_id in request.json['category_ids']
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
    'fts_request,fts_status_code,fts_response', ((REQUEST, 200, RESPONSE),),
)
@pytest.mark.parametrize(
    'search_category_in_saas_response',
    [
        pytest.param(True, id='saas response contains search category'),
        pytest.param(
            False, id='saas response doesn\'t contain search category',
        ),
    ],
)
@translations.DEFAULT
async def test_retail_not_found_in_category_header(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        # parametrize
        fts_request,
        fts_status_code,
        fts_response,
        search_category_in_saas_response,
):
    """
    Проверяем, что если в категории в которой велся поиск
    ничео не найдено, формируется поле header с
    надписью "В категории {название категории} ничего не найден"
    (saas - eats_retail_search, nomenclature_handlers - v2)
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    place_id = 1
    place_slug = 'my_place_slug'

    item = {
        'place_id': place_id,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100,
        'adult': False,
        'weight': '100 г',
        'shipping_type': 0,
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
        'place_id': place_id,
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

    category_search = {
        'place_id': place_id,
        'place_slug': place_slug,
        'category_id': 500,
        'title': SUPER_CATEGORY,
        'gallery': [{'url': 'URL'}],
        'parent_categories': [{'id': 500, 'title': SUPER_CATEGORY}],
    }

    category_search_url = '/{}/categories/{}'.format(
        category_search['place_id'], category_search['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        kps = int(args['kps'])
        if kps == 1:
            response = [
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ]
            if search_category_in_saas_response:
                response.append(
                    utils.gta_to_document(
                        category_search_url,
                        utils.category_to_gta(category_search),
                    ),
                )
            return utils.get_saas_response(response)
        if kps == 2:
            return utils.get_saas_response(
                [
                    utils.gta_to_document(
                        item_url, utils.retail_item_to_gta(item),
                    ),
                ],
            )
        assert False, f'Should be unreachable'
        return None

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
                    'id': product_id,
                    'in_stock': 2,
                    'is_available': True,
                    'origin_id': f'origin_id_{product_id}',
                    'parent_category_ids': ['1'],
                    'price': 100,
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': False,
                    'barcodes': [],
                    'description': {'general': 'Some item description'},
                    'id': product_id,
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': 'My Search Item',
                    'origin_id': f'origin_id_{product_id}',
                    'place_brand_id': '1',
                    'shipping_type': 'all',
                    'measure': {'value': 100, 'unit': 'GRM'},
                    'images': [{'url': 'URL', 'sort_order': 0}],
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        category_to_name = {
            '1': category['title'],
            '500': category_search['title'],
        }
        return {
            'categories': [
                {
                    'id': category_id,
                    'child_ids': [],
                    'name': category_to_name[category_id],
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'products': [],
                }
                for category_id in request.json['category_ids']
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
