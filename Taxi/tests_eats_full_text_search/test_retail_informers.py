import pytest

from . import catalog
from . import experiments
from . import utils


INFORMERS_BLOCK = 'informers'

SAAS_RETAIL_SERVICE = 'eats_retail_search'
SAAS_FTS_SERVICE = 'eats_fts'
ELASTIC_INDEX = 'menu_items'
PLATFORM = 'ios_app'
VERSION = '5.15.0'


@pytest.mark.parametrize(
    ['requested_category', 'expected_types'],
    [
        pytest.param(
            None,
            [INFORMERS_BLOCK, 'categories', 'items'],
            id='without_category',
        ),
        pytest.param(
            '1',
            [INFORMERS_BLOCK, 'categories', 'items', 'categories', 'items'],
            id='with_category',
        ),
    ],
)
@experiments.eats_fts_communications(search_inside_shop_informers_enabled=True)
async def test_menu_retail_informers(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        requested_category,
        expected_types,
):
    """
    Проверяем, что если вызвается поиск внутри магазина и в конфиге информеры
    включены на этом экране, выполняется запрос в eats-communications.
    И если eats-communications вернул информеры, то эти информеры добавляются
    в ответ поиска самым первым блоком
    """

    place_id = 1
    brand_id = 1000
    place_slug = 'my_place_slug'
    location = {'latitude': 1.0, 'longitude': 2.0}
    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    item = get_item()

    category = get_category()
    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )
    informers = [make_text_image_informer('1'), make_background_informer('2')]

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return make_places_categories(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return make_place_products_info(item)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return make_products_info(item)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return make_get_parent()

    @mockserver.json_handler(
        '/eats-communications/internal/v1/screen/communications',
    )
    def _communications(request):
        assert request.json['types'] == ['informers']
        assert request.json['screen'] == 'search_inside_shop'
        assert request.json['place_id'] == str(place_id)
        assert request.json['brand_id'] == str(brand_id)
        assert request.json['position'] == {
            'lat': location['latitude'],
            'lon': location['longitude'],
        }
        return {'payload': {'stories': [], 'informers': informers}}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': location,
            'text': 'My Search Text',
            'place_slug': place_slug,
            'category': requested_category,
        },
    )
    assert _communications.times_called == 1

    assert response.status_code == 200
    blocks = response.json()['blocks']
    assert [block['type'] for block in blocks] == expected_types
    assert blocks[0] == {
        'title': '',
        'type': INFORMERS_BLOCK,
        'payload': informers,
    }


@pytest.mark.parametrize('requested_category', [None, '1'])
@pytest.mark.parametrize(
    'status', [400, 429, 500, 'timeout', 'network_error', 'bad_format'],
)
@experiments.eats_fts_communications(search_inside_shop_informers_enabled=True)
async def test_menu_retail_informers_bad_communication_response(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        status,
        requested_category,
):
    """
    Проверяем, что если включен эксперимент информеров и eats-communications
    вернул плохой ответ, то возвращается ответ 200 без информеров
    """

    place_slug = 'my_place_slug'
    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    item = get_item()

    category = get_category()
    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return make_places_categories(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return make_place_products_info(item)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return make_products_info(item)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return make_get_parent()

    @mockserver.json_handler(
        '/eats-communications/internal/v1/screen/communications',
    )
    def _communications(request):
        if status == 'timeout':
            raise mockserver.TimeoutError()
        if status == 'network_error':
            raise mockserver.NetworkError()
        elif status == 'bad_format':
            return {'payload': {'bad_format': 'bad_format'}}
        return mockserver.make_response(status=status)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': place_slug,
            'category': requested_category,
        },
    )
    assert _communications.times_called == 1

    assert response.status_code == 200
    assert INFORMERS_BLOCK not in {
        block['type'] for block in response.json()['blocks']
    }


@pytest.mark.parametrize(
    'business', ['restaurant', 'store', 'pharmacy', 'zapravki'],
)
@experiments.eats_fts_communications(search_inside_shop_informers_enabled=True)
async def test_retail_informers_other_business_types(
        taxi_eats_full_text_search, mockserver, sql_set_place, business,
):
    """
    Проверяем, что при поиске в типах заведений отличных от магазина запроса
    в eats-communications за информерами нет
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, business)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response([])

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': place_slug,
        },
        headers=utils.get_headers(),
    )
    assert response.status_code == 200


@experiments.EATS_FTS_SELECTOR
@experiments.eats_fts_communications(search_main_shops_informers_enabled=True)
async def test_retail_informers_main_shops(
        taxi_eats_full_text_search,
        mockserver,
        load_json,
        set_retail_settings,
        set_retail_saas_experiment,
        eats_catalog,
):
    """
    Проверяем, что если вызвается поиск на главной во вкладке Магазины и в
    конфиге информеры включены на этом экране, выполняется запрос в
    eats-communications. И если eats-communications вернул информеры, то эти
    информеры добавляются в ответ поиска после блока селектора
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    brand_id = 1
    places = [
        catalog.Place(
            id=1,
            slug=f'my_place_slug',
            business=catalog.Business.Shop,
            brand=catalog.Brand(id=brand_id),
            name='Магазин',
        ),
    ]
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    location = {'latitude': 1.0, 'longitude': 2.0}
    informers = [make_text_image_informer('1'), make_background_informer('2')]

    item = get_item()
    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler(
        '/eats-communications/internal/v1/screen/communications',
    )
    def _communications(request):
        assert request.json['types'] == ['informers']
        assert request.json['screen'] == 'search_main_shops'
        assert request.json['position'] == {
            'lat': location['latitude'],
            'lon': location['longitude'],
        }
        return {'payload': {'stories': [], 'informers': informers}}

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.retail_item_to_gta(item))],
        )

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
            'result': [{'place_id': '1', 'items': [{'id': '10'}]}],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return make_places_categories(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return make_place_products_info(item)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return make_products_info(item)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return make_get_parent()

    headers = utils.get_headers()
    headers.update({'x-platform': PLATFORM, 'x-app-version': VERSION})
    request_params = {
        'text': 'My Search Text',
        'location': location,
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
    assert _communications.times_called == 1

    assert response.status == 200
    blocks = response.json()['blocks']
    assert [block['type'] for block in blocks] == [
        'selector',
        'informers',
        'places',
    ]
    assert blocks[1] == {
        'title': '',
        'type': INFORMERS_BLOCK,
        'payload': informers,
    }


@pytest.mark.parametrize(
    'status', [400, 429, 500, 'timeout', 'network_error', 'bad_format'],
)
@experiments.EATS_FTS_SELECTOR
@experiments.eats_fts_communications(search_main_shops_informers_enabled=True)
async def test_menu_retail_informers_main_shop_bad_response(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        status,
):
    """
    Проверяем, что поиске на главной во вкладке Магаизны, если включен
    эксперимент информеров и eats-communications вернул плохой ответ,
    то возвращается ответ 200 без информеров
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    item = get_item()

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response([])

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return make_places_categories(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return make_place_products_info(item)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return make_products_info(item)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return make_get_parent()

    @mockserver.json_handler(
        '/eats-communications/internal/v1/screen/communications',
    )
    def _communications(request):
        if status == 'timeout':
            raise mockserver.TimeoutError()
        if status == 'network_error':
            raise mockserver.NetworkError()
        elif status == 'bad_format':
            return {'payload': {'bad_format': 'bad_format'}}
        return mockserver.make_response(status=status)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'region_id': 1,
            'shipping_type': 'all',
            'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
            'selector': 'shop',
        },
    )
    assert _communications.times_called == 1

    assert response.status_code == 200
    assert INFORMERS_BLOCK not in {
        block['type'] for block in response.json()['blocks']
    }


@pytest.mark.parametrize('selector', ['all', 'restaurant'])
@experiments.EATS_FTS_SELECTOR
@experiments.eats_fts_communications(search_main_shops_informers_enabled=True)
async def test_menu_retail_informers_main_shop_other_selectors(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        set_retail_saas_experiment,
        selector,
):
    """
    Проверяем, что поиске на главной, если включен эксперимент информеров,
    но выбрана не вкладка Магазины, то запроса в eats-communications не будет
    """

    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    item = get_item()

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response([])

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return make_places_categories(request)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return make_place_products_info(item)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return make_products_info(item)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return make_get_parent()

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'region_id': 1,
            'shipping_type': 'all',
            'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
            'selector': selector,
        },
    )

    assert response.status_code == 200
    assert INFORMERS_BLOCK not in {
        block['type'] for block in response.json()['blocks']
    }


def get_item():
    return {
        'place_id': 1,
        'place_slug': 'my_place_slug',
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'measure': '100 g',
        'categories': [100],
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'Category 1'},
            {'id': 200, 'parent_id': None, 'title': 'Category 2'},
        ],
        'brand': 'Item brand',
        'type': 'Item type',
        'is_catch_weight': False,
        'buy_score': 0.1,
        'in_stock': 2,
        'price': 100.99,
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
    }


def get_category():
    return {
        'place_id': 1,
        'place_slug': 'my_place_slug',
        'category_id': 100,
        'title': 'My Search Category',
        'gallery': [{'url': 'URL'}],
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': None, 'title': 'Base Category'},
        ],
    }


def make_places_categories(request):
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


def make_get_parent():
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


def make_place_products_info(item):
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


def make_products_info(item):
    return {
        'products': [
            {
                'adult': item['adult'],
                'barcodes': [],
                'description': {'general': item['description']},
                'id': item['nomenclature_item_id'],
                'images': [
                    {'url': image['url'], 'sort_order': 1}
                    for image in item['gallery']
                ],
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


def make_text_image_informer(informer_id):
    return {
        'id': informer_id,
        'payload': {
            'text': {
                'value': 'some_text',
                'color': {'light': '#0000FF', 'dark': '#FF0000'},
            },
            'image': {'light': 'light_image', 'dark': 'dark_image'},
            'background': {
                'light': {
                    'type': 'image',
                    'content': 'light_background_image',
                },
                'dark': {'type': 'color', 'content': '#6D131C'},
            },
            'type': 'text_with_image',
        },
        'has_close_button': True,
        'url': 'http://yandex.ru',
        'deeplink': 'http://yandex.ru/mobile',
    }


def make_background_informer(informer_id):
    return {
        'id': informer_id,
        'payload': {
            'background': {
                'light': {
                    'type': 'image',
                    'content': 'light_background_image',
                },
                'dark': {'type': 'color', 'content': '#FF00FF'},
            },
            'text': {
                'value': 'some_text',
                'color': {'light': '#000FFF', 'dark': '#FFF000'},
            },
            'type': 'background',
        },
        'has_close_button': True,
        'url': 'http://yandex.ru',
        'deeplink': 'http://yandex.ru/mobile',
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
