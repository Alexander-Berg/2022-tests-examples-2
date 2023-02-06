import pytest

from . import catalog
from . import experiments
from . import translations
from . import utils


ELASTIC_INDEX = 'menu_items'
PLATFORM = 'ios_app'
VERSION = '5.15.0'

EATS_FTS_SELECTOR = pytest.mark.experiments3(
    name='eats_fts_selector',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'default': 'all',
                'selectors': [
                    {
                        'slug': 'all',
                        'text': 'Все',
                        'businesses': ['restaurant', 'shop', 'store'],
                    },
                    {
                        'slug': 'restaurant',
                        'text': 'Рестораны',
                        'businesses': ['restaurant', 'store'],
                    },
                    {
                        'slug': 'shop',
                        'text': 'Магазины',
                        'businesses': ['shop', 'store'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

RESTAURANT_EMPTY_RESPONSE = {
    'header': {'text': 'Увы, ничего не найдено'},
    'blocks': [
        {
            'title': '',
            'type': 'selector',
            'payload': {
                'current': 'restaurant',
                'list': [
                    {'slug': 'all', 'text': 'Все'},
                    {'slug': 'restaurant', 'text': 'Рестораны'},
                    {'slug': 'shop', 'text': 'Магазины'},
                ],
            },
        },
        {'title': '', 'type': 'places', 'payload': []},
    ],
}

HIGH_PRIORITY_BRAND = 2
BRAND_PRIORITY = {
    '__default__': {'priority': 100},
    str(HIGH_PRIORITY_BRAND): {'priority': 1},
}

DEFAULT_BRAND_PRIORITY = {'__default__': {'priority': 100}}


@EATS_FTS_SELECTOR
@pytest.mark.parametrize('selector', ('shop', 'restaurant', 'all'))
@pytest.mark.parametrize(
    'sort_by_sku',
    [
        pytest.param(True, id='sort by sku'),
        pytest.param(False, id='not sort by sku'),
    ],
)
@pytest.mark.parametrize(
    'exp_sort_by_sku_value',
    [
        pytest.param(True, id='use sku exp'),
        pytest.param(False, id='no sku exp'),
    ],
)
@pytest.mark.parametrize(
    'sort_places_by_priority',
    [
        pytest.param(True, id='sort places by priority'),
        pytest.param(False, id='not sort places by priority'),
    ],
)
@translations.DEFAULT
async def test_catalog_search_sort_order(
        taxi_eats_full_text_search,
        mockserver,
        experiments3,
        eats_catalog,
        load_json,
        taxi_config,
        # parametrize
        selector,
        sort_by_sku,
        exp_sort_by_sku_value,
        sort_places_by_priority,
):
    """
    Проверяем порядок сортировки магазинов и товаров в выдаче поиска с главной
    """

    set_config(taxi_config, sort_by_sku, sort_places_by_priority)
    experiments.set_sort_by_sku_experiment(experiments3, exp_sort_by_sku_value)

    places = []
    for idx in range(1, 8):
        if 4 <= idx <= 6:
            brand_id = HIGH_PRIORITY_BRAND
        else:
            brand_id = 1
        places.append(
            catalog.Place(
                id=idx,
                slug=f'slug_{idx}',
                business=catalog.Business.Shop,
                brand=catalog.Brand(id=brand_id),
            ),
        )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    items_with_sku = {
        'N_1',
        'N_2',
        'N_3',
        'N_5',
        'N_6',
        'N_7',
        'N_8',
        'N_9',
        'N_11',
    }

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        group = []
        place_to_items = {
            1: [1, 3, 4, 5],
            2: [1, 2, 3, 4],
            3: [3, 6, 7, 8],
            4: [9],
            5: [1, 2, 10],
            6: [2, 3, 10],
            7: [11],
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

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

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
                    'is_sku': product_id in items_with_sku,
                    'name': f'title {product_id}',
                    'origin_id': f'origin_id_{product_id}',
                    'place_brand_id': '1',
                    'shipping_type': 'all',
                    'sku_id': (
                        product_id if product_id in items_with_sku else None
                    ),
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

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': selector,
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )
    assert response.status == 200

    response_json = response.json()

    if selector == 'restaurant':
        assert response_json == RESTAURANT_EMPTY_RESPONSE
    else:
        payload = response_json['blocks'][1]['payload']

        expected_places_sort_order, expected_items_sort_order = (
            get_expected_sort_order(
                sort_by_sku,
                sort_places_by_priority,
                selector,
                exp_sort_by_sku_value,
            )
        )
        assert expected_places_sort_order == [i['slug'] for i in payload]
        assert expected_items_sort_order == {
            i['slug']: [item['id'] for item in i['items']] for i in payload
        }


def set_config(taxi_config, sort_by_sku, sort_places_by_priority):
    brand_priority = DEFAULT_BRAND_PRIORITY
    if sort_places_by_priority:
        brand_priority = BRAND_PRIORITY

    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS': {
                'enable': True,
                'index': ELASTIC_INDEX,
                'size': 1000,
            },
            'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'place_products_info_batch_size': 250,
                'place_categories_get_parents_batch_size': 50,
                'place_settings': {'__default__': {'handlers_version': 'v2'}},
            },
            'EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS': {
                'enable_umlaas_eats': False,
            },
            'EATS_FULL_TEXT_SEARCH_SELECTOR': {
                'min_versions': [{'platform': PLATFORM, 'version': VERSION}],
            },
            'EATS_FULL_TEXT_SEARCH_SORT_SETTINGS': {
                'sort_by_sku': sort_by_sku,
                'sort_places_by_priority': sort_places_by_priority,
                'sku_items_count': 3,
            },
            'EATS_FULL_TEXT_SEARCH_BRAND_PRIORITY_SETTINGS': brand_priority,
        },
    )


def get_expected_sort_order(
        sort_by_sku, sort_places_by_priority, selector, exp_sort_by_sku_value,
):
    should_sort_by_sku = (
        sort_by_sku and exp_sort_by_sku_value and selector == 'shop'
    )
    should_sort_by_priority = sort_places_by_priority and selector == 'shop'

    if should_sort_by_priority and should_sort_by_sku:
        places_sort_order = [
            # high priority brand
            'slug_6',
            'slug_5',
            'slug_4',
            # other brand
            'slug_2',
            'slug_1',
            'slug_3',
            'slug_7',
        ]
        items_sort_order = {
            # items '4' and '10' do not have sku, hence ignored
            # high priority brand
            'slug_6': ['2', '3', '10'],
            'slug_5': ['2', '1', '10'],
            'slug_4': ['9'],
            # other brand
            'slug_2': ['3', '1', '2', '4'],
            'slug_1': ['3', '1', '4', '5'],
            'slug_3': ['3', '6', '7', '8'],
            'slug_7': ['11'],
        }
    elif should_sort_by_priority:
        places_sort_order = [
            # high priority brand
            'slug_6',
            'slug_5',
            'slug_4',
            # other brand
            'slug_7',
            'slug_3',
            'slug_2',
            'slug_1',
        ]
        items_sort_order = {
            'slug_6': ['2', '3', '10'],
            'slug_5': ['1', '2', '10'],
            'slug_4': ['9'],
            'slug_7': ['11'],
            'slug_3': ['3', '6', '7', '8'],
            'slug_2': ['1', '2', '3', '4'],
            'slug_1': ['1', '3', '4', '5'],
        }
    elif should_sort_by_sku:
        places_sort_order = [
            'slug_2',
            'slug_1',
            'slug_6',
            'slug_5',
            'slug_3',
            'slug_7',
            'slug_4',
        ]
        items_sort_order = {
            # items '4' and '10' do not have sku, hence ignored
            'slug_2': ['3', '1', '2', '4'],
            'slug_1': ['3', '1', '4', '5'],
            'slug_6': ['3', '10', '2'],
            'slug_5': ['10', '1', '2'],
            'slug_3': ['3', '6', '7', '8'],
            'slug_7': ['11'],
            'slug_4': ['9'],
        }
    else:
        places_sort_order = [
            'slug_7',
            'slug_6',
            'slug_5',
            'slug_4',
            'slug_3',
            'slug_2',
            'slug_1',
        ]
        items_sort_order = {
            'slug_7': ['11'],
            'slug_6': ['2', '3', '10'],
            'slug_5': ['1', '2', '10'],
            'slug_4': ['9'],
            'slug_3': ['3', '6', '7', '8'],
            'slug_2': ['1', '2', '3', '4'],
            'slug_1': ['1', '3', '4', '5'],
        }

    return places_sort_order, items_sort_order
