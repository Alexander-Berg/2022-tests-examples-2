# pylint: disable=too-many-lines
import pytest

from . import catalog
from . import experiments
from . import utils


SAAS_RETAIL_SERVICE = 'eats_retail_search'
SAAS_RETAIL_ITEMS_PREFIX = 2

SAAS_FTS_SERVICE = 'eats_fts'

ELASTIC_INDEX = 'menu_items'
PLATFORM = 'ios_app'
VERSION = '5.15.0'


@experiments.EATS_FTS_SELECTOR
@pytest.mark.parametrize('selector', ('shop', 'restaurant', 'all'))
@pytest.mark.parametrize('retail_search_exp_enable', (True, False))
async def test_catalog_retail_search(
        taxi_eats_full_text_search,
        mockserver,
        load_json,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
        # parametrize
        selector,
        retail_search_exp_enable,
):
    """
    Проверяем, что если включен эксперимент, то сервис пробрасывает запросы
    до saas eats_retail_search и формирует ответ на основе ответа saas.
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=retail_search_exp_enable)

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'slug_1',
            business=catalog.Business.Restaurant,
            brand=catalog.Brand(id=brand_id),
            name='Ресторан 1',
        ),
        catalog.Place(
            id=2,
            slug=f'slug_2',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 2',
        ),
        catalog.Place(
            id=3,
            slug=f'slug_3',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 3',
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))
    is_shop = {1: False, 2: True, 3: True}
    item_to_adult = {
        'N_1': False,
        'N_2': True,
        'N_3': False,
        'N_4': True,
        'N_5': False,
        'N_6': True,
    }

    requested_saas_services = []

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        requested_saas_services.append(args['service'])
        if args['service'] == SAAS_FTS_SERVICE:
            return get_fts_saas_response(load_json, is_shop)
        if args['service'] == SAAS_RETAIL_SERVICE:
            return get_retail_saas_response(load_json)
        assert False, f'Should be unreachable'
        return None

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        result = []
        for place in request.json['block']:
            items = []
            for item in place['items']:
                items.append({'id': item['id']})
            result.append(
                {
                    'place_id': place['place_id'],
                    'items': sorted(items, key=lambda item: item['id']),
                },
            )
        return {
            'exp_list': [],
            'request_id': 'MY_REQ_ID',
            'result': sorted(result, key=lambda item: item['place_id']),
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
                    'price': 0,
                }
                for product_id in request.json['product_ids']
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': item_to_adult[product_id],
                    'barcodes': [],
                    'description': {'general': 'description'},
                    'id': product_id,
                    'images': [],
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': f'Item {product_id}',
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
    assert sorted(requested_saas_services) == get_expected_saas_services(
        selector, retail_search_exp_enable,
    )
    if selector == 'restaurant':
        assert response_json == get_expected_response(
            selector, places, {1: [1, 2]}, is_shop, item_to_adult,
        )
    elif selector == 'shop':
        if retail_search_exp_enable:
            assert response_json == get_expected_response(
                selector, places, {2: [5, 6], 3: []}, is_shop, item_to_adult,
            )
        else:
            assert response_json == get_expected_response(
                selector, places, {2: [3, 4], 3: []}, is_shop, item_to_adult,
            )
    elif selector == 'all':
        if retail_search_exp_enable:
            assert response_json == get_expected_response(
                selector,
                places,
                {1: [1, 2], 2: [5, 6], 3: []},
                is_shop,
                item_to_adult,
            )
        else:
            assert response_json == get_expected_response(
                selector,
                places,
                {1: [1, 2], 2: [3, 4], 3: []},
                is_shop,
                item_to_adult,
            )


@experiments.EATS_FTS_SELECTOR
async def test_no_ranking(
        taxi_eats_full_text_search,
        mockserver,
        load_json,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
):
    """
    Проверяем, что товары не переранжируются на основе umlaas в случае поиска
    через saas eats_retail_search.
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=2,
            slug=f'slug_2',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 2',
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        if args['service'] == SAAS_FTS_SERVICE:
            return utils.get_saas_response([])
        if args['service'] == SAAS_RETAIL_SERVICE:
            return get_retail_saas_response(load_json)
        assert False, 'Should be unreachable'
        return None

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return {
            'exp_list': [],
            'request_id': 'MY_REQ_ID',
            'result': [{'place_id': '2', 'items': [{'id': '6'}, {'id': '5'}]}],
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
                    'price': 0,
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
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': f'Item {product_id}',
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

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'shop',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    items = response.json()['blocks'][1]['payload'][0]['items']

    expected_items_order = ('5', '6')

    for item, item_id in zip(items, expected_items_order):
        assert item['id'] == item_id


@experiments.EATS_FTS_SELECTOR
async def test_no_sort_by_sku(
        taxi_eats_full_text_search,
        mockserver,
        experiments3,
        load_json,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
):
    """
    Проверяем, что товары не сортируются по sku в случае поиска
    через saas eats_retail_search.
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)
    set_sort_by_sku_experiment(experiments3, sort_by_sku=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=2,
            slug=f'slug_2',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 2',
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    items_with_sku = {'N_6'}

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        if args['service'] == SAAS_FTS_SERVICE:
            return utils.get_saas_response([])
        if args['service'] == SAAS_RETAIL_SERVICE:
            return get_retail_saas_response(load_json)
        assert False, 'Should be unreachable'
        return None

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
                    'price': 0,
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
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': product_id in items_with_sku,
                    'name': f'Item {product_id}',
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
        'selector': 'shop',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    items = response.json()['blocks'][1]['payload'][0]['items']

    expected_items_order = ('5', '6')

    for item, item_id in zip(items, expected_items_order):
        assert item['id'] == item_id


@experiments.EATS_FTS_SELECTOR
@pytest.mark.parametrize(
    'items_formula_name', ['items_formula_1', 'items_formula_2'],
)
async def test_formula(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
        # parametrize
        items_formula_name,
):
    """
    Проверяем, что параметр relev управляется через конфиг
    """

    set_retail_settings(items_formula_name=items_formula_name)
    set_retail_saas_experiment(enable=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'slug_1',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    requested_services = set()

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        requested_services.add(args['service'])
        if args['service'] == SAAS_RETAIL_SERVICE:
            assert int(args['kps']) == SAAS_RETAIL_ITEMS_PREFIX
            assert args['relev'] == f'formula={items_formula_name}'
        return utils.get_saas_response([])

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'shop',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    # 2 сервиса, в каждый делается по 2 запроса: со * на конце и без
    assert _saas.times_called == 4
    assert requested_services == {SAAS_RETAIL_SERVICE, SAAS_FTS_SERVICE}


@experiments.EATS_FTS_SELECTOR
@pytest.mark.parametrize(
    'star_settings, expected_requested_texts',
    [
        ('no_star', {'My Search Text'}),
        ('with_star', {'My Search Text*'}),
        ('both', {'My Search Text*', 'My Search Text'}),
    ],
)
async def test_star_settings(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
        # parametrize
        star_settings,
        expected_requested_texts,
):
    """
    Проверяем, что запросы в saas делаются со * на конце или без
    в зависимости от конфига
    """

    set_retail_settings(star_settings=star_settings)
    set_retail_saas_experiment(enable=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'slug_1',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    requested_services = set()
    requested_texts = set()

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        requested_services.add(args['service'])
        if args['service'] == SAAS_RETAIL_SERVICE:
            requested_texts.add(args['text'])
        return utils.get_saas_response([])

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'shop',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    assert _saas.times_called == 4 if star_settings == 'both' else 3
    assert requested_services == {SAAS_RETAIL_SERVICE, SAAS_FTS_SERVICE}
    assert requested_texts == expected_requested_texts


@experiments.EATS_FTS_SELECTOR
@pytest.mark.parametrize('should_group_by_places', [True, False])
@pytest.mark.parametrize('docs_in_group_count', [100, 200])
@pytest.mark.parametrize('groups_count', [10, 20])
async def test_group_params(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        set_retail_settings,
        set_retail_saas_experiment,
        # parametrize
        should_group_by_places,
        docs_in_group_count,
        groups_count,
):
    """
    Проверяем, что параметры группировки управляются через конфиг
    """

    set_retail_settings(
        should_group_by_places=should_group_by_places,
        docs_in_group_count=docs_in_group_count,
        groups_count=groups_count,
    )
    set_retail_saas_experiment(enable=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'slug_1',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    requested_services = set()

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        requested_services.add(args['service'])
        if args['service'] == SAAS_RETAIL_SERVICE:
            assert int(args['kps']) == SAAS_RETAIL_ITEMS_PREFIX
            assert ('g' in args) == should_group_by_places
            if should_group_by_places:
                expected_g = (
                    f'1.i_pid.{groups_count}.{docs_in_group_count}.....rlv.0.'
                )
                assert args['g'] == expected_g
        return utils.get_saas_response([])

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'shop',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    # 2 сервиса, в каждый делается по 2 запроса: со * на конце и без
    assert _saas.times_called == 4
    assert requested_services == {SAAS_RETAIL_SERVICE, SAAS_FTS_SERVICE}


@experiments.EATS_FTS_SELECTOR
@pytest.mark.parametrize('show_price_category', (True, False))
@pytest.mark.parametrize('show_tags', (True, False))
async def test_shop_meta_settings(
        taxi_eats_full_text_search,
        mockserver,
        load_json,
        experiments3,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
        # parametrize
        show_price_category,
        show_tags,
):
    """
    Проверяем, что поля price_category и tags заполняются у магазинов
    в зависимости от экспа eats_fts_catalog_place_meta
    (на заполнение этих полей у ресторанов эксп не влияет)
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)
    experiments3.add_config(
        name='eats_fts_catalog_place_meta',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'show_rating': True,
                    'shop_settings': {
                        'show_price_category': show_price_category,
                        'show_tags': show_tags,
                    },
                },
            },
        ],
    )

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'slug_1',
            business=catalog.Business.Restaurant,
            brand=catalog.Brand(id=brand_id),
            name='Ресторан 1',
        ),
        catalog.Place(
            id=2,
            slug=f'slug_2',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 2',
        ),
        catalog.Place(
            id=3,
            slug=f'slug_3',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин 3',
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))
    is_shop = {1: False, 2: True, 3: True}

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        if args['service'] == SAAS_FTS_SERVICE:
            return get_fts_saas_response(load_json, is_shop)
        if args['service'] == SAAS_RETAIL_SERVICE:
            return get_retail_saas_response(load_json)
        assert False, f'Should be unreachable'
        return None

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        result = []
        for place in request.json['block']:
            items = []
            for item in place['items']:
                items.append({'id': item['id']})
            result.append(
                {
                    'place_id': place['place_id'],
                    'items': sorted(items, key=lambda item: item['id']),
                },
            )
        return {
            'exp_list': [],
            'request_id': 'MY_REQ_ID',
            'result': sorted(result, key=lambda item: item['place_id']),
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
                    'price': 0,
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
                    'description': {'general': 'description'},
                    'id': product_id,
                    'images': [],
                    'is_catch_weight': False,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': f'Item {product_id}',
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

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'all',
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    response_json = response.json()
    for place_response in response_json['blocks'][1]['payload']:
        if place_response['business'] == 'shop':
            assert ('price_category' in place_response) == show_price_category
            assert ('tags' in place_response) == show_tags
        else:
            assert 'price_category' in place_response
            assert 'tags' in place_response


def set_sort_by_sku_experiment(experiments3, sort_by_sku):
    experiments3.add_experiment(
        name='eats_fts_sort_by_sku',
        consumers=['eats_full_text_search/sort_by_sku'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Title',
                'predicate': {'type': 'true'},
                'value': {'sort_by_sku': sort_by_sku},
            },
        ],
    )


def get_fts_saas_place(load_json, place_id):
    place_response = load_json('saas_response_place.json')
    place_data = place_response['Document'][0]['ArchiveInfo']
    title = f'Place {place_id}'
    place_data['Title'] = title
    place_data['Url'] = f'/slug_{place_id}'
    place_data['GtaRelatedAttribute'] += [
        {'Key': 'title', 'Value': title},
        {'Key': 's_place_slug', 'Value': f'slug_{place_id}'},
        {'Key': 'i_pid', 'Value': str(place_id)},
        {'Key': 'i_type', 'Value': '0'},
    ]
    return place_response


def get_fts_saas_item(load_json, item_id, place_id, is_shop):
    item_response = load_json('saas_response_item.json')
    item_data = item_response['Document'][0]['ArchiveInfo']
    title = f'Item N_{item_id}'
    item_data['Title'] = title
    item_data['Url'] = f'/slug_{place_id}/items/N_{item_id}'
    item_data['GtaRelatedAttribute'] += [
        {'Key': 'i_pid', 'Value': f'{place_id}'},
        {'Key': 's_nom_item_id', 'Value': f'N_{item_id}'},
        {'Key': 's_place_slug', 'Value': f'slug_{place_id}'},
        {'Key': 's_origin_id', 'Value': f'origin_id_{item_id}'},
        {'Key': 'title', 'Value': title},
        {'Key': 'i_type', 'Value': '1' if is_shop[place_id] else '3'},
        {'Key': 'i_core_item_id', 'Value': f'{item_id}'},
        {'Key': 'i_category_id', 'Value': '1'},
    ]
    return item_response


def get_fts_saas_response(load_json, is_shop):
    group = []
    place_to_items = {1: [1, 2], 2: [3, 4], 3: []}
    for place_id, items in place_to_items.items():
        place_response = get_fts_saas_place(load_json, place_id)
        group.append(place_response)
        for item_id in items:
            item_response = get_fts_saas_item(
                load_json, item_id, place_id, is_shop,
            )
            group.append(item_response)

    return {
        'Grouping': [
            {
                'Attr': '',
                'Group': group,
                'Mode': 0,
                'NumDocs': [9, 0, 0],
                'NumGroups': [1, 0, 0],
            },
        ],
    }


def get_retail_saas_item(load_json, item_id, place_id, place_slug):
    item_response = load_json('saas_response_item.json')
    item_data = item_response['Document'][0]['ArchiveInfo']
    item_data['Title'] = f'Item N_{item_id}'
    item_data['Url'] = f'/{place_id}/items/N_{item_id}'

    item_data['GtaRelatedAttribute'] = [
        {'Key': 'i_pid', 'Value': f'{place_id}'},
        {'Key': 's_place_slug', 'Value': f'{place_slug}'},
        {'Key': 'z_title', 'Value': f'Item N_{item_id}'},
        {'Key': 'p_public_id', 'Value': f'N_{item_id}'},
        {'Key': 'p_origin_id', 'Value': f'origin_id_{item_id}'},
    ]
    return item_response


def get_retail_saas_response(load_json):
    group = []
    place_to_items = {2: [5, 6]}
    groups = []
    for place_id, items in place_to_items.items():
        group = []
        place_slug = f'slug_{place_id}'
        for item_id in items:
            item_response = get_retail_saas_item(
                load_json, item_id, place_id, place_slug,
            )
            group.append(item_response)
        groups.append(
            {
                'Attr': '',
                'Group': group,
                'Mode': 0,
                'NumDocs': [2, 0, 0],
                'NumGroups': [1, 0, 0],
            },
        )

    return {'Grouping': groups}


def get_expected_saas_services(selector, retail_search_exp_enable):
    if selector == 'restaurant' or not retail_search_exp_enable:
        return [SAAS_FTS_SERVICE, SAAS_FTS_SERVICE]
    return [
        SAAS_FTS_SERVICE,
        SAAS_FTS_SERVICE,
        SAAS_RETAIL_SERVICE,
        SAAS_RETAIL_SERVICE,
    ]


def get_expected_response(
        selector, catalog_places, place_to_items, is_shop, item_to_adult,
):
    places_response = []
    for place_id, items in place_to_items.items():
        catalog_place = catalog_places[place_id - 1]
        place_response = {
            'available': True,
            'available_from': '2021-02-18T00:00:00+03:00',
            'available_to': '2021-02-18T23:00:00+03:00',
            'brand': {'slug': 'brand_slug'},
            'business': 'shop' if is_shop[place_id] else 'restaurant',
            'delivery': {'text': '10 - 20 min'},
            'picture': {'ratio': 1.33, 'url': 'picture.url'},
            'price_category': {'title': '₽'},
            'slug': catalog_place.slug,
            'tags': [{'title': 'Завтраки'}],
            'title': catalog_place.name,
            'items': [],
        }
        for item in items:
            item_response = {
                'decimal_price': '0',
                'id': str(item),
                'parent_category_id': '1',
                'price': '0 ₽',
                'search_type': 'menu',
                'title': f'Item N_{item}',
                'adult': (
                    item_to_adult[f'N_{item}'] if is_shop[place_id] else False
                ),
            }
            if is_shop[place_id]:
                item_response['public_id'] = f'N_{item}'
            place_response['items'].append(item_response)
        places_response.append(place_response)
    return {
        'blocks': [
            {
                'title': '',
                'type': 'selector',
                'payload': {
                    'current': selector,
                    'list': [
                        {'slug': 'all', 'text': 'Все'},
                        {'slug': 'restaurant', 'text': 'Рестораны'},
                        {'slug': 'shop', 'text': 'Магазины'},
                    ],
                },
            },
            {'title': '', 'type': 'places', 'payload': places_response},
        ],
    }
