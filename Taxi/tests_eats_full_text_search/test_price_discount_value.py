from . import utils


PLACE_SLUG = 'my_place_slug'


async def test_price_discount_value(
        taxi_eats_full_text_search, mockserver, taxi_config,
):
    """
    Проверяем корректность выставления price_discount_value для поиска
    в магазине
    """

    fts_request = {
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'text': 'My Search Text',
        'place_slug': PLACE_SLUG,
        'category': '100',
    }

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

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
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
                    # 'in_stock': item['in_stock'],
                    'is_available': True,
                    'origin_id': item['origin_id'],
                    'parent_category_ids': ['1'],
                    'price': item['price'],
                    'old_price': 1000,
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

    assert response.status_code == 200

    item = response.json()['blocks'][3]['payload'][0]
    price_discount_value = 90
    assert item['price_discount_value'] == price_discount_value
