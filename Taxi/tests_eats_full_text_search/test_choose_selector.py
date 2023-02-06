# pylint: disable=too-many-lines
import pytest

from . import catalog
from . import utils


SAAS_RETAIL_SERVICE = 'eats_retail_search'
SAAS_FTS_SERVICE = 'eats_fts'

PLATFORM = 'ios_app'
VERSION = '5.15.0'

RESTAURANT_SELECTOR = 'restaurant'
SHOP_SELECTOR = 'shop'
ALL_SELECTOR = 'all'
DEFAULT_CONFIG_SELECTOR = 'all'

QUERY_TEXT = 'my search text'


@pytest.mark.parametrize(
    'request_selector',
    (RESTAURANT_SELECTOR, SHOP_SELECTOR, ALL_SELECTOR, None),
)
@pytest.mark.parametrize(
    'should_choose_selector',
    [
        pytest.param(True, id='choose selector by statistics'),
        pytest.param(False, id='not choose selector by statistics'),
        pytest.param(None, id='no choose selector exp'),
    ],
)
@pytest.mark.parametrize(
    'should_choose_selector_if_all',
    [
        pytest.param(True, id='choose selector if selector is all'),
        pytest.param(False, id='not choose selector if selector is all'),
    ],
)
async def test_choose_selector_exp(
        taxi_eats_full_text_search,
        mockserver,
        experiments3,
        taxi_config,
        eats_catalog,
        pgsql,
        set_retail_settings,
        set_retail_saas_experiment,
        # parametrize
        request_selector,
        should_choose_selector,
        should_choose_selector_if_all,
):
    """
    Проверяем, что если включен эксперимент eats_fts_choose_selector и
    в запросе не выбран селектор, то вкладка выбирается на основе
    selector_statistics
    """

    percentage_threshold = 60
    count_threshold = 1000
    shop_percentage = 10
    restaurant_percentage = 80
    count = 2000
    default_selector = 'all'

    set_retail_settings()
    set_selector_config(experiments3)
    set_choose_selector_settings(
        taxi_config,
        percentage_threshold=percentage_threshold,
        count_threshold=count_threshold,
    )
    if should_choose_selector is not None:
        set_choose_selector_experiment(
            experiments3,
            should_choose_selector=should_choose_selector,
            default_selector=default_selector,
            should_choose_selector_if_all=should_choose_selector_if_all,
        )
    set_retail_saas_experiment(enable=True)

    set_selector_statistics(
        pgsql,
        query=QUERY_TEXT,
        shop_percentage=shop_percentage,
        restaurant_percentage=restaurant_percentage,
        count=count,
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
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))
    places_data = [
        {'place_id': 1, 'items': [1], 'is_shop': False},
        {'place_id': 2, 'items': [2], 'is_shop': True},
    ]

    rest_item = _gen_item(place_id=1, item_id=1)
    shop_item = _gen_item(place_id=2, item_id=2)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        return _gen_saas_response(request, places, rest_item, shop_item)

    @mockserver.json_handler('eats-fts-elastic-search/menu_items/_search')
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return {'exp_list': [], 'request_id': 'MY_REQ_ID', 'result': []}

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return _gen_nmn_places_cat(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return _gen_nmn_place_prod_info(request)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return _gen_nmn_prod_info(request)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return _gen_nmn_place_cat_get_parent(request)

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': QUERY_TEXT,
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': request_selector,
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    expected_selector = get_expected_current_selector(
        shop_percentage,
        restaurant_percentage,
        count,
        percentage_threshold,
        count_threshold,
        default_selector,
        should_choose_selector,
        request_selector,
        should_choose_selector_if_all,
    )
    expected_response = get_expected_response(
        expected_selector, places, places_data,
    )
    assert expected_response == response.json()


@pytest.mark.parametrize('default_selector', ('restaurant', 'shop', 'all'))
@pytest.mark.parametrize(
    'query_text',
    [
        pytest.param('my search text', id='lower case query text'),
        pytest.param('MY SEARCH TEXT', id='upper case query text'),
    ],
)
@pytest.mark.parametrize(
    'shop_percentage, restaurant_percentage, count',
    [
        pytest.param(10, 80, 2000, id='restaurant_percentage is larger'),
        pytest.param(80, 10, 2000, id='shop_percentage is larger'),
    ],
)
@pytest.mark.parametrize(
    'percentage_threshold',
    [
        pytest.param(10, id='both percentages are larger than threshold'),
        pytest.param(50, id='only one percentage is larger than threshold'),
        pytest.param(90, id='both percentages are smaller than threshold'),
    ],
)
@pytest.mark.parametrize(
    'count_threshold',
    [
        pytest.param(1000, id='count is larger than threshold'),
        pytest.param(3000, id='count is smaller than threshold'),
    ],
)
async def test_selector_statistics(
        taxi_eats_full_text_search,
        mockserver,
        experiments3,
        taxi_config,
        eats_catalog,
        pgsql,
        set_retail_settings,
        set_retail_saas_experiment,
        # parametrize
        query_text,
        default_selector,
        shop_percentage,
        restaurant_percentage,
        count,
        percentage_threshold,
        count_threshold,
):
    """
    Проверяем, что при выборе вкладки на основе selector_statistics,
    учитываются пороговые значения и дефолтная вкладка из эксперимента
    """

    should_choose_selector = True
    request_selector = None

    set_retail_settings()
    set_selector_config(experiments3)
    set_choose_selector_settings(
        taxi_config,
        percentage_threshold=percentage_threshold,
        count_threshold=count_threshold,
    )
    set_choose_selector_experiment(
        experiments3,
        should_choose_selector=should_choose_selector,
        default_selector=default_selector,
    )
    set_retail_saas_experiment(enable=True)

    set_selector_statistics(
        pgsql,
        query=query_text.lower(),
        shop_percentage=shop_percentage,
        restaurant_percentage=restaurant_percentage,
        count=count,
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
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))
    places_data = [
        {'place_id': 1, 'items': [1], 'is_shop': False},
        {'place_id': 2, 'items': [2], 'is_shop': True},
    ]

    rest_item = _gen_item(place_id=1, item_id=1)
    shop_item = _gen_item(place_id=2, item_id=2)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        return _gen_saas_response(request, places, rest_item, shop_item)

    @mockserver.json_handler('eats-fts-elastic-search/menu_items/_search')
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return {'exp_list': [], 'request_id': 'MY_REQ_ID', 'result': []}

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return _gen_nmn_places_cat(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return _gen_nmn_place_prod_info(request)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return _gen_nmn_prod_info(request)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return _gen_nmn_place_cat_get_parent(request)

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': query_text,
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': request_selector,
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200

    expected_selector = get_expected_current_selector(
        shop_percentage,
        restaurant_percentage,
        count,
        percentage_threshold,
        count_threshold,
        default_selector,
        should_choose_selector,
        request_selector,
        should_choose_selector_if_all=False,
    )
    expected_response = get_expected_response(
        expected_selector, places, places_data,
    )
    assert expected_response == response.json()


@pytest.mark.parametrize(
    'config_default_selector',
    (RESTAURANT_SELECTOR, SHOP_SELECTOR, ALL_SELECTOR),
)
@pytest.mark.parametrize(
    'exp_default_selector', (RESTAURANT_SELECTOR, SHOP_SELECTOR, ALL_SELECTOR),
)
@pytest.mark.parametrize(
    'should_remove_all_selector',
    [
        pytest.param(True, id='remove all selector'),
        pytest.param(False, id='not remove all selector'),
    ],
)
async def test_should_remove_all_selector(
        taxi_eats_full_text_search,
        experiments3,
        set_retail_settings,
        set_retail_saas_experiment,
        # parametrize
        config_default_selector,
        exp_default_selector,
        should_remove_all_selector,
):
    """
    Проверяем, что если включен эксперимент eats_fts_choose_selector и
    should_remove_all_selector = true, то вкладка Все не возвращается
    из ответа. Если вкладка Все была дефолтной, то дефолтной будет вкладка
    из эксперимента (если в эксперименте дефолтной тоже является вкладка Все,
    то дефолтной выберется первая из оставшихся вкладок конфига).
    """

    set_retail_settings()
    set_selector_config(experiments3, default_selector=config_default_selector)
    set_choose_selector_experiment(
        experiments3,
        default_selector=exp_default_selector,
        should_remove_all_selector=should_remove_all_selector,
    )
    set_retail_saas_experiment(enable=True)

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': QUERY_TEXT,
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
    }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert response.status == 200
    response = response.json()
    selectors = response['blocks'][0]['payload']
    assert selectors == get_expected_selectors(
        config_default_selector,
        exp_default_selector,
        should_remove_all_selector,
    )


def set_choose_selector_settings(
        taxi_config, count_threshold=1000, percentage_threshold=60,
):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_CHOOSE_SELECTOR_SETTINGS': {
                'count_threshold': count_threshold,
                'percentage_threshold': percentage_threshold,
            },
        },
    )


def set_choose_selector_experiment(
        experiments3,
        should_choose_selector=False,
        default_selector='all',
        should_choose_selector_if_all=False,
        should_remove_all_selector=False,
):
    experiments3.add_experiment(
        name='eats_fts_choose_selector',
        consumers=['eats-full-text-search/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Title',
                'predicate': {'type': 'true'},
                'value': {
                    'should_choose_selector': should_choose_selector,
                    'default_selector': default_selector,
                    'should_choose_selector_if_all': (
                        should_choose_selector_if_all
                    ),
                    'should_remove_all_selector': should_remove_all_selector,
                },
            },
        ],
    )


def set_selector_config(experiments3, default_selector='all'):
    experiments3.add_config(
        name='eats_fts_selector',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'default': default_selector,
                    'selectors': [
                        {
                            'slug': ALL_SELECTOR,
                            'text': 'Все',
                            'businesses': ['restaurant', 'shop', 'store'],
                        },
                        {
                            'slug': RESTAURANT_SELECTOR,
                            'text': 'Рестораны',
                            'businesses': ['restaurant', 'store'],
                        },
                        {
                            'slug': SHOP_SELECTOR,
                            'text': 'Магазины',
                            'businesses': ['shop', 'store'],
                        },
                    ],
                },
            },
        ],
    )


def set_selector_statistics(
        pgsql, query, shop_percentage, restaurant_percentage, count,
):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        INSERT INTO fts.selector_statistics(
            query, count, restaurant_percentage, shop_percentage
        )
        VALUES (
            '{query}',{count},
            {restaurant_percentage}, {shop_percentage});
        """,
    )


def get_expected_current_selector(
        shop_percentage,
        restaurant_percentage,
        count,
        percentage_threshold,
        count_threshold,
        default_selector,
        choose_selector_enabled,
        request_selector,
        should_choose_selector_if_all,
):
    if request_selector and (
            not should_choose_selector_if_all
            or request_selector != ALL_SELECTOR
    ):
        return request_selector

    if not choose_selector_enabled:
        return DEFAULT_CONFIG_SELECTOR

    if count < count_threshold or shop_percentage == restaurant_percentage:
        return default_selector

    if shop_percentage > percentage_threshold:
        if restaurant_percentage <= percentage_threshold:
            return SHOP_SELECTOR
        if shop_percentage > restaurant_percentage:
            return SHOP_SELECTOR
        return RESTAURANT_SELECTOR

    if restaurant_percentage > percentage_threshold:
        return RESTAURANT_SELECTOR

    return default_selector


def get_expected_selectors(
        config_default_selector,
        exp_default_selector,
        should_remove_all_selector,
):
    selectors = [
        {'slug': 'all', 'text': 'Все'},
        {'slug': 'restaurant', 'text': 'Рестораны'},
        {'slug': 'shop', 'text': 'Магазины'},
    ]
    if should_remove_all_selector:
        del selectors[0]

    current_selector = config_default_selector
    if config_default_selector == 'all' and should_remove_all_selector:
        if exp_default_selector != 'all':
            current_selector = exp_default_selector
        else:
            # RESTAURANT_SELECTOR идет первой в конфиге селекторов
            current_selector = RESTAURANT_SELECTOR

    return {'current': current_selector, 'list': selectors}


def get_expected_response(selector, catalog_places, places_data):
    places_response = []
    for place in places_data:
        if selector == RESTAURANT_SELECTOR and place['is_shop']:
            continue
        if selector == SHOP_SELECTOR and not place['is_shop']:
            continue
        catalog_place = catalog_places[place['place_id'] - 1]
        place_response = {
            'available': True,
            'available_from': '2021-02-18T00:00:00+03:00',
            'available_to': '2021-02-18T23:00:00+03:00',
            'brand': {'slug': 'brand_slug'},
            'business': 'shop' if place['is_shop'] else 'restaurant',
            'delivery': {'text': '10 - 20 min'},
            'picture': {'ratio': 1.33, 'url': 'picture.url'},
            'price_category': {'title': '₽'},
            'slug': catalog_place.slug,
            'tags': [{'title': 'Завтраки'}],
            'title': catalog_place.name,
            'items': [],
        }
        for item in place['items']:
            item_response = {
                'decimal_price': '0',
                'id': str(item),
                'parent_category_id': '1',
                'price': '0 ₽',
                'search_type': 'menu',
                'title': f'Item N_{item}',
                'adult': False,
            }
            if place['is_shop']:
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


def _gen_nmn_places_cat(request):
    return {
        'places_categories': [
            {
                'categories': [
                    str(category_id)
                    for category_id in request.json['places_categories'][0][
                        'categories'
                    ]
                ],
                'place_id': request.json['places_categories'][0]['place_id'],
            },
        ],
    }


def _gen_nmn_place_prod_info(request):
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


def _gen_nmn_prod_info(request):
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


def _gen_nmn_place_cat_get_parent(request):
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


def _gen_item(place_id, item_id):
    return {
        'place_id': place_id,
        'place_slug': f'slug_{place_id}',
        'nomenclature_item_id': f'N_{item_id}',
        'origin_id': f'N_{item_id}',
        'core_item_id': item_id,
        'title': f'Item N_{item_id}',
        'measure': '100 g',
        'categories': [1],
        'parent_categories': [
            {'id': 1, 'parent_id': 200, 'title': 'Category 1'},
        ],
        'brand': 'Item brand',
        'type': 'Item type',
        'is_catch_weight': False,
        'buy_score': 0.1,
        'in_stock': 2,
        'price': 100.99,
        'adult': False,
        'shipping_type': 0,
        'description': 'Some item description',
    }


def _gen_saas_response(request, places, rest_item, shop_item):
    def _gen_url(item):
        return '/{}/items/{}'.format(
            item['place_id'], item['nomenclature_item_id'],
        )

    args = request.query
    if args['service'] == SAAS_FTS_SERVICE:
        place_docs = [
            utils.catalog_place_to_saas_doc(place) for place in places
        ]
        item_doc = [
            utils.gta_to_document(
                _gen_url(rest_item), utils.item_to_gta(rest_item, doc_type=3),
            ),
        ]
        return utils.get_saas_response(place_docs + item_doc)
    if args['service'] == SAAS_RETAIL_SERVICE:
        return utils.get_saas_response(
            [
                utils.gta_to_document(
                    _gen_url(shop_item), utils.retail_item_to_gta(shop_item),
                ),
            ],
        )
    assert False, f'Should be unreachable'
    return None
