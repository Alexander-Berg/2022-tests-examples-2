import pytest

from . import translations
from . import utils


SAAS_RETAIL_SERVICE = 'eats_retail_search'
SAAS_RETAIL_CATEGORIES_PREFIX = 1
SAAS_RETAIL_ITEMS_PREFIX = 2
SAAS_RETAIL_MISSPELL = 'try_at_first'

SAAS_FTS_SERVICE = 'eats_fts'
SAAS_FTS_PREFIX = 3
SAAS_FTS_MISSPELL = 'force'


@pytest.mark.parametrize(
    'fts_request, fts_status_code, fts_response',
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
@translations.DEFAULT
async def test_retail_search(
        taxi_eats_full_text_search,
        mockserver,
        sql_set_place,
        set_retail_saas_experiment,
        set_retail_settings,
        fts_request,
        fts_status_code,
        fts_response,
):
    """
    Проверяем, что если включен эксперимент, то сервис пробрасывает запросы
    до saas eats_retail_search и формирует ответ на основе ответа saas.
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, 'shop')
    set_retail_settings()
    set_retail_saas_experiment(enable=True)

    item = get_item()
    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    category = get_category()
    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_RETAIL_SERVICE
        assert args['msp'] == SAAS_RETAIL_MISSPELL
        assert args['gta'] == '_AllDocInfos'
        assert args['ms'] == 'proto'
        assert args['hr'] == 'json'
        kps = int(args['kps'])
        if kps == SAAS_RETAIL_CATEGORIES_PREFIX:
            return utils.get_saas_response(
                [
                    utils.gta_to_document(
                        category_url, utils.category_to_gta(category),
                    ),
                ],
            )
        if kps == SAAS_RETAIL_ITEMS_PREFIX:
            return utils.get_saas_response(
                [
                    utils.gta_to_document(
                        item_url, utils.retail_item_to_gta(item),
                    ),
                ],
            )
        assert False, 'Should be unreachable'
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

    assert (
        _saas_search_proxy.times_called == 4
    )  # items and categories with and without star

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
    response_request_id = response.headers.get('x-request-id')
    assert response_request_id is not None
    assert response_request_id == request_id


@pytest.mark.parametrize('exp_enable', [True, False])
@pytest.mark.parametrize(
    'business', ['restaurant', 'store', 'shop', 'pharmacy', 'zapravki'],
)
@translations.DEFAULT
async def test_saas_service(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        sql_set_place,
        set_retail_saas_experiment,
        exp_enable,
        business,
):
    """
    Проверяем, что запрос пробрасывается в нужный сервис saas
    в зависимости от эксперимента и поля business заведения
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, business)
    set_retail_settings()
    set_retail_saas_experiment(enable=exp_enable)

    request_retail_saas = business == 'shop' and exp_enable

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        kps = int(args['kps'])
        if request_retail_saas:
            expected_service = SAAS_RETAIL_SERVICE
            expected_misspell = SAAS_RETAIL_MISSPELL
            expected_prefixes = {
                SAAS_RETAIL_CATEGORIES_PREFIX,
                SAAS_RETAIL_ITEMS_PREFIX,
            }
        else:
            expected_service = SAAS_FTS_SERVICE
            expected_misspell = SAAS_FTS_MISSPELL
            expected_prefixes = {SAAS_FTS_PREFIX}
        assert args['service'] == expected_service
        assert args['msp'] == expected_misspell
        assert kps in expected_prefixes

        return utils.get_saas_response([])

    await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    expected_saas_times_called = 4 if request_retail_saas else 2
    assert _saas_search_proxy.times_called == expected_saas_times_called


@pytest.mark.parametrize(
    'items_formula_name', ['items_formula_1', 'items_formula_2'],
)
@pytest.mark.parametrize(
    'categories_formula_name',
    ['categories_formula_1', 'categories_formula_2'],
)
@translations.DEFAULT
async def test_formula(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        sql_set_place,
        set_retail_saas_experiment,
        items_formula_name,
        categories_formula_name,
):
    """
    Проверяем, что параметр relev управляется через конфиг
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, 'shop')
    set_retail_settings(
        items_formula_name=items_formula_name,
        categories_formula_name=categories_formula_name,
    )
    set_retail_saas_experiment(enable=True)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_RETAIL_SERVICE
        kps = int(args['kps'])
        if kps == SAAS_RETAIL_CATEGORIES_PREFIX:
            assert args['relev'] == f'formula={categories_formula_name}'
        elif kps == SAAS_RETAIL_ITEMS_PREFIX:
            assert args['relev'] == f'formula={items_formula_name}'
        else:
            assert False, 'Should be unreachable'

        return utils.get_saas_response([])

    await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    assert _saas_search_proxy.times_called == 4


@pytest.mark.parametrize('no_star_items_threshold', [1, 5, 10])
@pytest.mark.parametrize('saas_items_count', [0, 4, 9, 11])
@pytest.mark.parametrize(
    'star_settings', ['no_star', 'with_star', 'both', 'try_no_star_first'],
)
@pytest.mark.parametrize(
    'request_text_star_settings',
    ['no_star', 'with_star', 'both', 'try_no_star_first', None],
)
@pytest.mark.parametrize('request_text', ['My Search Text', 'my search text'])
@translations.DEFAULT
async def test_star_settings(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        set_retail_settings,
        sql_set_place,
        set_retail_saas_experiment,
        # parametrize
        no_star_items_threshold,
        saas_items_count,
        star_settings,
        request_text_star_settings,
        request_text,
):
    """
    Проверяем, что запросы в saas делаются со * на конце или без
    в зависимости от конфига с общими настройками и конфига с настройками
    по поисковым запросам
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, 'shop')
    set_retail_settings(
        star_settings=star_settings,
        no_star_items_threshold=no_star_items_threshold,
    )
    set_retail_saas_experiment(enable=True)
    if request_text_star_settings:
        set_request_text_star_settings(
            taxi_config, request_text.lower(), request_text_star_settings,
        )

    request_texts = set()
    item = get_item()
    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_RETAIL_SERVICE
        request_texts.add(args['text'])
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.retail_item_to_gta(item))]
            * saas_items_count,
        )

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return {'places_categories': []}

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return {'products': []}

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {'products': []}

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return {'categories': []}

    await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': request_text,
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    expected_request_texts = get_expected_request_texts(
        request_text,
        no_star_items_threshold,
        saas_items_count,
        star_settings,
        request_text_star_settings,
    )
    assert (
        _saas_search_proxy.times_called
        == len(expected_request_texts)
        * 2  # умножаем на 2, т.к. делается запрос для товаров и для категорий
    )
    assert request_texts == expected_request_texts


@pytest.mark.parametrize('should_group_by_places', [True, False])
@translations.DEFAULT
async def test_group_params(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        sql_set_place,
        set_retail_saas_experiment,
        # parametrize
        should_group_by_places,
):
    """
    Проверяем, что параметр группировки не передается в saas
    при поиске в магазине вне зависимости от параметра should_group_by_places
    """

    place_id = 1
    place_slug = 'my_place_slug'
    sql_set_place(place_id, place_slug, 'shop')
    set_retail_settings(should_group_by_places=should_group_by_places)
    set_retail_saas_experiment(enable=True)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_RETAIL_SERVICE
        assert 'g' not in args
        return utils.get_saas_response([])

    await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    assert _saas_search_proxy.has_calls


@pytest.mark.parametrize('use_synonyms_dict', [True, False])
@pytest.mark.parametrize(
    'synonyms_dict_name', ['SomeDictName1', 'SomeDictName2'],
)
@translations.DEFAULT
async def test_wizard_settings(
        taxi_eats_full_text_search,
        mockserver,
        set_retail_settings,
        sql_set_place,
        set_retail_saas_experiment,
        # parametrize
        use_synonyms_dict,
        synonyms_dict_name,
):
    """
    Проверяем, что параметр rwr заполняется корректно
    """

    place_id = 1
    place_slug = 'my_place_slug'
    request_text = 'My Search Text'
    sql_set_place(place_id, place_slug, 'shop')
    set_retail_settings(
        use_synonyms_dict=use_synonyms_dict,
        synonyms_dict_name=synonyms_dict_name,
    )
    set_retail_saas_experiment(enable=True)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert ('rwr' in args) == use_synonyms_dict
        if use_synonyms_dict:
            assert args['rwr'] == f'on:CustomThesaurus/{synonyms_dict_name}'
        return utils.get_saas_response([])

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return {'places_categories': []}

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return {'products': []}

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {'products': []}

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return {'categories': []}

    await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': request_text,
            'place_slug': 'my_place_slug',
        },
        headers=utils.get_headers(),
    )

    assert _saas_search_proxy.has_calls


def get_expected_request_texts(
        request_text,
        no_star_items_threshold,
        saas_items_count,
        star_settings,
        request_text_star_settings,
):
    if request_text_star_settings:
        star_settings = request_text_star_settings
    request_text_with_star = f'{request_text}*'
    if star_settings == 'no_star':
        return {request_text}
    if star_settings == 'with_star':
        return {request_text_with_star}
    if star_settings == 'both':
        return {request_text_with_star, request_text}
    if star_settings == 'try_no_star_first':
        if saas_items_count < no_star_items_threshold:
            return {request_text_with_star, request_text}
        return {request_text}
    return None


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


def set_request_text_star_settings(taxi_config, text, star_settings):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_REQUEST_TEXT_STAR_SETTINGS': {
                text: star_settings,
            },
        },
    )
