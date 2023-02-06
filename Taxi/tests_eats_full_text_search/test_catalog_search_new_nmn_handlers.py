from . import catalog
from . import utils


async def test_catalog_search_sort_order(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        load_json,
        taxi_config,
):
    """
    Проверяем выдачу поиска с главной, когда одновременно есть плейсы,
    переключенные на старые ручки, и плейсы, переключенные на новые ручки
    номенклатуры
    """

    set_config(taxi_config, {1: 'v2', 2: 'v2', 3: 'v1', 4: 'v1'})

    places = []
    for idx in range(1, 5):
        places.append(
            catalog.Place(
                id=idx, slug=f'slug_{idx}', business=catalog.Business.Shop,
            ),
        )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        group = []
        place_to_items = {
            1: [1, 3, 4, 5],
            2: [1, 2, 3, 4],
            3: [3, 6, 7, 8],
            4: [9],
        }
        for place_id, items in place_to_items.items():
            place_response = load_json('saas_response_place.json')
            place_data = place_response['Document'][0]['ArchiveInfo']
            title = f'Place {place_id}'
            place_data['Title'] = title
            place_data['Url'] = f'/slug_{place_id}'
            place_data['GtaRelatedAttribute'] += [
                {'Key': 'title', 'Value': title},
                {'Key': 's_place_slug', 'Value': f'slug_{place_id}'},
                {'Key': 'i_pid', 'Value': str(place_id)},
            ]
            group.append(place_response)
            for item_id in items:
                item_response = load_json('saas_response_item.json')
                item_data = item_response['Document'][0]['ArchiveInfo']
                title = f'Item {item_id}'
                item_data['Title'] = title
                item_data['Url'] = f'/slug_{place_id}/items/N_{item_id}'
                item_data['GtaRelatedAttribute'] += [
                    {'Key': 'i_pid', 'Value': f'{place_id}'},
                    {
                        'Key': 's_core_id_nom_cat',
                        'Value': f"""[{{"core_item_id":{item_id},
                                      "nomenclature_category_id":"841"}}]""",
                    },
                    {'Key': 's_nom_item_id', 'Value': f'N_{item_id}'},
                    {'Key': 's_place_slug', 'Value': f'slug_{place_id}'},
                    {'Key': 's_origin_id', 'Value': f'O_{item_id}'},
                    {'Key': 'title', 'Value': title},
                ]
                group.append(item_response)

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [2, 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nmn_place_ass_details(request):
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [
                build_item(product_id)
                for product_id in request.json['products']
            ],
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
                    'id': product_id,
                    'in_stock': 1,
                    'is_available': True,
                    'origin_id': f'origin_id_{product_id}',
                    'parent_category_ids': ['1'],
                    'price': 10.0,
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': True,
                    'barcodes': [],
                    'description': {'general': 'description'},
                    'id': product_id,
                    'images': [],
                    'is_catch_weight': True,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': f'title {product_id}',
                    'origin_id': f'origin_id_{product_id}',
                    'place_brand_id': '1',
                    'shipping_type': 'all',
                }
                for product_id in request.json['product_ids']
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

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert response.status == 200
    assert response.json() == load_json('response.json')


def set_config(taxi_config, place_to_handlers_version):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'place_products_info_batch_size': 250,
                'place_categories_get_parents_batch_size': 50,
                'place_settings': {
                    str(id): {'handlers_version': version}
                    for id, version in place_to_handlers_version.items()
                },
            },
            'EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS': {
                'enable_umlaas_eats': False,
            },
        },
    )


def build_item(product_id):
    return {
        'product_id': product_id,
        'name': f'title {product_id}',
        'description': 'description',
        'adult': True,
        'images': [],
        'shipping_type': 'all',
        'price': 10.0,
        'in_stock': 1,
    }
