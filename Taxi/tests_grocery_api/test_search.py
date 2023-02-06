# pylint: disable=too-many-lines

import datetime

from grocery_mocks import (  # pylint: disable=E0401
    grocery_menu as mock_grocery_menu,
)
from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from testsuite.utils import ordered_object

from . import combo_products_common as common_combo
from . import common
from . import common_search
from . import conftest
from . import const
from . import experiments
from . import tests_headers


_make_market_offer = common_search.make_market_offer  # pylint: disable=C0103
_make_market_search_response = (  # pylint: disable=C0103
    common_search.make_market_search_response
)

# Возвращает ошибку, если лавка не найдена
async def test_can_not_find_depot(taxi_grocery_api):
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'test-query', 'position': {'location': [0, 0]}},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# Проверяем, что при ошибке ходим в фолбечный движок из экспа
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.create_search_flow_experiment('internal', fallback_flow='saas')
async def test_search_fallback(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_depots,
        saas_search_proxy,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={'code': 'SEARCH_FAILURE', 'message': 'error_message'},
            status=500,
        )

    saas_search_proxy.add_product(product_id='product-1')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
    )
    assert response.status_code == 200
    assert saas_search_proxy.saas_search_times_called() == 2
    assert _mock_grocery_search.times_called == 1
    assert len(response.json()['products']) == 1


# Ходит в основной и фолбечный движки, возвращает ошибку, если оба похода
# были с ошибкой
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.create_search_flow_experiment('internal', fallback_flow='saas')
async def test_search_failed(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_depots,
        grocery_search,
        saas_search_proxy,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_search.should_failed()
    saas_search_proxy.should_failed()

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
    )

    assert response.status_code == 500


# Ходит в /grocery-search/internal/v1/search/v1/search, фильтрует товары по
# лавке, добавляет к поисковой выдаче название, описание, остатки, цены, даже
# если скидки не доступны
@pytest.mark.parametrize('with_options', [True, False])
async def test_glue_products_with_stocks_prices_without_discounts(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        offers,
        grocery_search,
        grocery_depots,
        load_json,
        with_options,
        now,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = [0, 0]
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )

    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )
    if with_options:
        products_data = load_json(
            'overlord_catalog_products_data_with_options.json',
        )
    else:
        products_data = load_json('overlord_catalog_products_data.json')
    overlord_catalog.add_products_data(new_products_data=products_data)
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json('overlord_catalog_products_stocks.json'),
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-1', available=True,
    )

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _mock_discount_modifiers(request):
        return mockserver.make_response(json={}, status=500)

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-not-in-depot')

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=depot_id,
        location=location,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200

    if with_options:
        expected_response = load_json(
            'search_with_options_expected_response.json',
        )
    else:
        expected_response = load_json('search_expected_response.json')

    ordered_object.assert_eq(response.json(), expected_response, [''])


# Цены со скидками и кэшбэком
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED),
        pytest.param(True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
        pytest.param(True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
async def test_glue_products_with_stocks_prices_with_discounts(
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        grocery_search,
        grocery_depots,
        load_json,
        antifraud_enabled,
        is_fraud,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = common.DEFAULT_LOCATION
    color = '#51c454'
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None
    cashback = 12.3
    expected_cashback = '13'  # ceil(cashback)

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json('overlord_catalog_products_stocks.json'),
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-1', available=True,
    )

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_product(product_id='product-not-in-depot')

    grocery_p13n.add_modifier(
        product_id='product-1',
        value='0.7',
        meta={'title_tanker_key': 'test_discount_label', 'label_color': color},
    )

    grocery_p13n.add_modifier(
        product_id='product-1',
        value=str(cashback),
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )

    grocery_p13n.add_modifier(product_id='product-2', value='0.15')

    grocery_p13n.add_modifier(
        product_id='product-2',
        value=str(cashback),
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )

    expected_discount_pricing = {
        'price': '1',
        'price_template': '1 $SIGN$$CURRENCY$',
        'discount_label': '-50% discount',
        'bundle_discount_desc': '-50% discount',
        'label_color': color,
        'cashback': expected_cashback,
    }

    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(orders_count),
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': 'test-offer',
            'additional_data': common.DEFAULT_ADDITIONAL_DATA,
        },
        headers={
            'X-Yandex-UID': yandex_uid,
            'User-Agent': common.DEFAULT_USER_AGENT,
        },
    )
    assert response.status_code == 200
    assert grocery_p13n.discount_modifiers_times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )
    response_json = response.json()
    assert len(response_json['products']) == 1
    response_product = response_json['products'][0]
    assert response_product['discount_pricing'] == expected_discount_pricing


# Кусочная выдача
@pytest.mark.config(GROCERY_API_INTERNAL_SEARCH_LIMIT_MULTIPLIER=2.0)
@pytest.mark.parametrize(
    'cursor,limit,expected_results',
    [
        pytest.param(
            {'offset': 0},
            2,
            ['product-1', 'product-2', 'product-3'],
            id='smoke',
        ),
        pytest.param(
            None,
            2,
            ['product-1', 'product-2', 'product-3'],
            id='init cursor is absent',
        ),
        pytest.param(
            None,
            100,
            ['product-1', 'product-2', 'product-3'],
            id='limit > total count',
        ),
        pytest.param({'offset': 0}, 0, [], id='corner case: limit = 0'),
        pytest.param(
            {'offset': 11}, 2, [], id='corner case: cursor = total count',
        ),
        pytest.param(
            {'offset': 100}, 2, [], id='corner case: cursor > total count',
        ),
    ],
)
async def test_returns_by_chunks(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        grocery_depots,
        load_json,
        cursor,
        limit,
        expected_results,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = [0, 0]
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '10',
            },
            {
                'in_stock': '10',
                'product_id': 'product-3',
                'quantity_limit': '3',
            },
        ],
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-2', available=True,
    )

    grocery_search.add_product(product_id='unknown-product-1')
    grocery_search.add_product(product_id='unknown-product-2')
    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='unknown-product-3')
    grocery_search.add_product(product_id='unknown-product-4')
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_product(product_id='unknown-product-5')
    grocery_search.add_product(product_id='unknown-product-6')
    grocery_search.add_product(product_id='unknown-product-7')
    grocery_search.add_product(product_id='unknown-product-8')
    grocery_search.add_product(product_id='product-3')

    grocery_p13n.add_modifier(product_id='product-1', value='0.1')
    grocery_p13n.add_modifier(product_id='product-2', value='1')
    grocery_p13n.add_modifier(product_id='product-3', value='2')

    results = []
    non_empty_responses = 0
    while True:
        request_json = {
            'text': 'query-text-for-product',
            'position': {'location': location},
            'offer_id': 'test-offer',
            'limit': limit,
            'categories_limit': 0,
        }
        if cursor:
            request_json['cursor'] = cursor

        response = await taxi_grocery_api.post(
            '/lavka/v1/api/v1/search', json=request_json,
        )

        assert response.status_code == 200
        response_json = response.json()

        if response_json['products']:
            non_empty_responses += 1
        results.extend(map(lambda p: p['id'], response_json['products']))
        if 'cursor' not in response_json:
            break

        cursor = response_json['cursor']

    assert sorted(results) == sorted(expected_results)
    assert grocery_p13n.discount_modifiers_times_called == non_empty_responses


# Применяет множитель для limit
@pytest.mark.config(GROCERY_API_INTERNAL_SEARCH_LIMIT_MULTIPLIER=4.0)
async def test_limit_multiplier_apply(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        grocery_depots,
        load_json,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = [0, 0]
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
        ],
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )

    grocery_search.add_product(product_id='unknown-product-1')
    grocery_search.add_product(product_id='unknown-product-2')
    grocery_search.add_product(product_id='unknown-product-3')
    grocery_search.add_product(product_id='product-1')

    grocery_p13n.add_modifier(product_id='product-1', value='0.1')

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
        'limit': 1,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    response_json = response.json()
    products = response_json['products']
    assert len(products) == 1
    assert products[0]['id'] == 'product-1'
    assert grocery_search.internal_search_v2_times_called() == 1


# Проверяем что неперечеркнутые цены заменяют
# цену в каталоге в выдаче ручки
@pytest.mark.parametrize(
    'should_replace',
    [
        pytest.param(False, id='not replace by default'),
        pytest.param(
            True,
            marks=[experiments.SUBSTITUTE_UNCROSSED_PRICE_ENABLED],
            id='replace by experiment',
        ),
        pytest.param(
            False,
            marks=[experiments.SUBSTITUTE_UNCROSSED_PRICE_DISABLED],
            id='not replace by experiment',
        ),
    ],
)
async def test_replace_catalog_price_search(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        should_replace,
        grocery_search,
):
    location = [0, 0]
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    grocery_p13n.add_modifier(
        product_id=product_id, value='1.09', meta={'is_price_uncrossed': True},
    )

    grocery_search.add_product(product_id='product-1')

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
        'limit': 1,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    res_product = response.json()['products'][0]
    if should_replace:
        assert res_product['pricing']['price'] == '1'
        assert res_product['pricing']['price_template'] == '1 $SIGN$$CURRENCY$'
        assert 'price' not in res_product['discount_pricing']
        assert 'price_template' not in res_product['discount_pricing']
    else:
        assert res_product['pricing']['price'] == '2'
        assert res_product['pricing']['price_template'] == '2 $SIGN$$CURRENCY$'
        assert res_product['discount_pricing']['price'] == '1'
        assert (
            res_product['discount_pricing']['price_template']
            == '1 $SIGN$$CURRENCY$'
        )


@experiments.SEARCH_FLOW_INTERNAL
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@conftest.DIFFERENT_LAYOUT_SOURCE
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_search_with_categories_flow(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_search,
        grocery_products,
):
    """ Test search with categories and subcategories
    all items should be sorted by type in response """

    location = [0, 0]

    product_id = 'product-1'
    layout_id = 'layout-1'
    group_id = 'category-group-1'
    virtual_category_id = 'virtual-category-1'
    subcategory_id = 'category-1-subcategory-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    common.build_basic_layout(grocery_products)

    grocery_search.add_product(product_id=product_id)
    grocery_search.add_product(product_id='product-not-in-depot')
    grocery_search.add_subcategory(subcategory_id=subcategory_id)
    grocery_search.add_subcategory(subcategory_id='subcategory-not-found')
    grocery_search.add_virtual_category(
        virtual_category_id=virtual_category_id,
    )
    grocery_search.add_subcategory(subcategory_id='virtual-category-not-found')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_products = response.json()['products']
    assert len(response_products) == 3
    # First item should be virtual_category with path
    assert response_products[0]['type'] == 'category'
    assert response_products[0]['id'] == virtual_category_id
    assert response_products[0]['layout_id'] == layout_id
    assert response_products[0]['group_id'] == group_id

    # Second item should be subcategory with path
    assert response_products[1]['type'] == 'subcategory'
    assert response_products[1]['id'] == subcategory_id
    assert response_products[1]['virtual_category_id'] == virtual_category_id
    assert response_products[1]['layout_id'] == layout_id
    assert response_products[1]['group_id'] == group_id

    # Third item should be product
    assert response_products[2]['type'] == 'good'
    assert response_products[2]['id'] == product_id


SAAS_SERVICE = common_search.SAAS_SERVICE
SAAS_PREFIX = common_search.SAAS_PREFIX
SAAS_CUSTOM_PREFIX = common_search.SAAS_CUSTOM_PREFIX
SAAS_MISPELL = common_search.SAAS_MISPELL
SAAS_ITEM_ID_KEY = 's_item_id'
SAAS_ITEM_TYPE_KEY = 'i_item_type'
SAAS_ITEM_TYPE_CATEGORY = '1'
SAAS_ITEM_TYPE_PRODUCT = '2'
SAAS_URL_PREFIX_PRODUCT = 'product'
SAAS_URL_PREFIX_CATEGORY = 'category'


def _saas_make_response(docs):
    group = []
    for doc in docs:
        group.append({'CategoryName': '', 'Document': [doc]})

    return {
        'Head': {'Version': 1, 'SegmentId': '', 'IndexGeneration': 0},
        'DebugInfo': {
            'BaseSearchCount': 1,
            'BaseSearchNotRespondCount': 0,
            'AnswerIsComplete': True,
        },
        'BalancingInfo': {'Elapsed': 1, 'WaitInQueue': 1, 'ExecutionTime': 1},
        'SearcherProp': [],
        'ErrorInfo': {'GotError': 2},
        'TotalDocCount': [51, 0, 0],
        'Grouping': [
            {
                'Attr': '',
                'Mode': 1,
                'NumGroups': [51, 0, 0],
                'NumDocs': [51, 0, 0],
                'Group': group,
            },
        ],
    }


def _saas_make_product_document(product_id, relevance=1, mtime=100):
    return _saas_make_document(
        _saas_make_document_url(SAAS_URL_PREFIX_PRODUCT, product_id),
        [
            _saas_make_item_id_gta(product_id),
            _saas_make_item_type_gta(SAAS_ITEM_TYPE_PRODUCT),
        ],
        relevance,
        mtime,
    )


def _saas_make_category_document(category_id, relevance=1, mtime=100):
    return _saas_make_document(
        _saas_make_document_url(SAAS_URL_PREFIX_CATEGORY, category_id),
        [
            _saas_make_item_id_gta(category_id),
            _saas_make_item_type_gta(SAAS_ITEM_TYPE_CATEGORY),
        ],
        relevance,
        mtime,
    )


def _saas_make_document(url, gta, relevance=1, mtime=100):
    return {
        'Relevance': relevance,
        'Priority': 1,
        'InternalPriority': 1,
        'DocId': 'doc_1',
        'SRelevance': 1,
        'SPriority': 1,
        'SInternalPriority': 1,
        'ArchiveInfo': {
            'Title': '',
            'Headline': '',
            'IndexGeneration': 1,
            'Passage': [''],
            'Url': url,
            'Size': 1,
            'Charset': 'utf-8',
            'Mtime': mtime,
            'GtaRelatedAttribute': gta,
        },
    }


def _saas_make_item_type_gta(item_type):
    return _saas_make_gta(SAAS_ITEM_TYPE_KEY, item_type)


def _saas_make_item_id_gta(item_id):
    return _saas_make_gta(SAAS_ITEM_ID_KEY, item_id)


def _saas_make_gta(key, value):
    return {'Key': key, 'Value': value}


def _saas_make_document_url(prefix, item_id):
    return prefix + '/' + item_id


@pytest.mark.config(
    GROCERY_API_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISPELL,
        'debug_relevance': True,
        'relev': 'formula=<formula_name>',
    },
)
@experiments.SEARCH_FLOW_SAAS
@experiments.create_saas_custom_formula('<formula_name>')
async def test_prepare_saas_request(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]
    query_text = 'query-text'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        query = request.query
        assert query['service'] == SAAS_SERVICE
        assert int(query['kps']) == SAAS_PREFIX
        assert query['msp'] == SAAS_MISPELL
        assert query['ms'] == 'proto'
        assert query['hr'] == 'json'
        assert (query['text'] == query_text) or (
            query['text'] == query_text + '*'
        )
        assert 'reqid' in query
        assert query['dbgrlv'] == 'da'
        assert query['fsgta'] == '_RtyFactors'
        assert query['relev'] == 'formula=<formula_name>'
        assert query['haha'] == 'da'
        assert query['pron'] == 'earlyurls'

        return mockserver.make_response(
            json=_saas_make_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }
    await taxi_grocery_api.post('/lavka/v1/api/v1/search', json=request_json)


@pytest.mark.config(
    GROCERY_API_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISPELL,
    },
)
@experiments.SEARCH_FLOW_SAAS
@experiments.create_saas_custom_params(True, 'default', SAAS_CUSTOM_PREFIX)
async def test_custom_relev_params(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        query = request.query
        assert query['dbgrlv'] == 'da'
        assert query['fsgta'] == '_RtyFactors'
        assert query['relev'] == 'formula=default'
        assert int(query['kps']) == SAAS_CUSTOM_PREFIX

        return mockserver.make_response(
            json=_saas_make_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
    )


@pytest.mark.config(
    GROCERY_API_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISPELL,
    },
)
@experiments.create_search_flow_experiment(
    'saas',
    search_flow_api_params={
        'saas_search_flow_api_params': {'prefix': SAAS_CUSTOM_PREFIX},
    },
)
async def test_saas_prefix_from_experiment(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        assert int(request.query['kps']) == SAAS_CUSTOM_PREFIX
        return mockserver.make_response(
            json=_saas_make_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }
    await taxi_grocery_api.post('/lavka/v1/api/v1/search', json=request_json)
    assert _saas_search_proxy.times_called == 2


@pytest.mark.config(
    GROCERY_API_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISPELL,
    },
)
@experiments.SEARCH_FLOW_SAAS
async def test_search_with_saas(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        mockserver,
):
    location = [0, 0]
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_p13n.add_modifier(product_id=product_id, value='1.2')

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = _saas_make_response(
            [_saas_make_product_document(product_id)],
        )
        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    found_product = response_json['products'][0]
    assert found_product['id'] == product_id
    assert found_product['pricing']['price'] == '2'
    assert (
        'discount_pricing' in found_product
        and found_product['discount_pricing']['price'] == '1'
    )
    assert _saas_search_proxy.times_called == 2


# В зависимости от эксперимента используем разные движки для получения
# поисковой выдачи для категорий.
@pytest.mark.parametrize(
    'expected_results, expected_saas_calls, expected_grocery_search_calls',
    [
        pytest.param(
            ['product-1'],
            0,
            1,
            marks=experiments.SEARCH_CATEGORIES_FLOW_NONE,
            id='none',
        ),
        pytest.param(
            ['product-1'],
            0,
            1,
            marks=experiments.create_search_categories_flow_experiment(
                'none', allowed_categories=['category'],
            ),
            id='none with allowed_categories',
        ),
        pytest.param(
            ['category-2-subcategory-1', 'product-1'],
            0,
            2,
            marks=experiments.SEARCH_CATEGORIES_FLOW_INTERNAL,
            id='internal',
        ),
        pytest.param(
            ['category-1-subcategory-1', 'product-1'],
            2,  # в SaaS отправляем всегда два запроса (с *[префиксный] и без)
            2,
            marks=experiments.SEARCH_CATEGORIES_FLOW_SAAS,
            id='saas',
        ),
    ],
)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_search_categories_flow(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_search,
        saas_search_proxy,
        load_json,
        grocery_products,
        expected_results,
        expected_saas_calls,
        expected_grocery_search_calls,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )

    saas_search_proxy.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_subcategory(subcategory_id='category-2-subcategory-1')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status == 200
    assert len(response.json()['products']) == len(expected_results)

    found_items_ids = []
    for search_item in response.json()['products']:
        found_items_ids.append(search_item['id'])

    assert found_items_ids == expected_results
    assert saas_search_proxy.saas_search_times_called() == expected_saas_calls
    assert (
        grocery_search.internal_search_v2_times_called()
        == expected_grocery_search_calls
    )


# Проверяет, что результаты префиксного поиска подмерживаются согласно
# заданному порядку невозрастания релевантности.
@pytest.mark.config(
    GROCERY_API_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISPELL,
    },
)
@experiments.SEARCH_FLOW_SAAS
async def test_search_with_saas_prefix(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]
    product_id_1 = 'product-1'
    product_id_2 = 'product-2'

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '5',
            },
        ],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        query = request.query
        response = None
        if query['text'].endswith('*'):
            response = _saas_make_response(
                [
                    _saas_make_product_document(product_id_1, 1),
                    _saas_make_product_document(product_id_2, 1),
                ],
            )
        else:
            response = _saas_make_response(
                [_saas_make_product_document(product_id_2, 2)],
            )

        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 2
    assert response_json['products'][0]['id'] == product_id_2
    assert response_json['products'][1]['id'] == product_id_1


async def test_search_offer_time(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        offers,
        grocery_search,
        grocery_depots,
        load_json,
):
    depot_id = 'test-depot'
    location = [0, 0]
    legacy_depot_id = '123'
    category_tree = load_json('overlord_catalog_category_tree.json')
    product_stocks = load_json('overlord_catalog_products_stocks.json')
    common.prepare_overlord_catalog(
        overlord_catalog,
        location,
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
        category_tree=category_tree,
        product_stocks=product_stocks,
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    date = '2020-01-21T10:00:00+00:00'
    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=datetime.datetime.fromisoformat(date),
        depot_id=depot_id,
        location=location,
    )

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _mock_p13n_discount_modifiers(request):
        assert request.json['offer_time'] == date
        return {'modifiers': []}

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-not-in-depot')
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    assert _mock_p13n_discount_modifiers.times_called == 1


# проверяем что ходим в grocery-search независимо от результата saas
@pytest.mark.parametrize(
    'saas_response',
    [
        pytest.param(
            {
                'json': {'code': 'SEARCH_FAILURE', 'message': 'error_message'},
                'status': 404,
            },
            id='saas_error',
        ),
        pytest.param(
            {
                'json': _saas_make_response(
                    [_saas_make_product_document('product-1')],
                ),
                'status': 200,
            },
            id='no_saas_error',
        ),
    ],
)
@experiments.SEARCH_FLOW_SAAS
async def test_search_saas_error(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        saas_response,
):
    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=saas_response['json'],
            status=saas_response['status'],
            headers={},
            content_type='application/json',
        )

    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _saas_search_proxy.times_called == 2
    assert grocery_search.internal_search_v2_times_called() == 1
    assert response.status == 200


# Проверяем что в случае ошибки grocery-search,
# отработает корректно, но не вернет категорий
@experiments.SEARCH_FLOW_SAAS
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_grocery_search_error(
        taxi_grocery_api, mockserver, overlord_catalog, load_json,
):
    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [_saas_make_product_document('product-1')],
            ),
            status=200,
            headers={},
            content_type='application/json',
        )

    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'json': {
                            'code': 'SEARCH_FAILURE',
                            'message': 'error_message',
                        },
                        'status': 400,
                    },
                ],
            },
            status=400,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _saas_search_proxy.times_called == 2
    assert _mock_grocery_search.times_called == 2
    assert response.status == 200
    items = response.json()['products']
    assert len(items) == 1
    assert items[0]['type'] == 'good'


# Проверяем что в выдаче saas не будет категории из конфига
@pytest.mark.config(
    GROCERY_API_SEARCH_HIDDEN_CATEGORIES=['category-2-subcategory-1'],
)
@experiments.SEARCH_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_search_hidden_categories_config(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        grocery_products,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [
                    _saas_make_product_document('product-1'),
                    _saas_make_category_document('category-1-subcategory-1'),
                    _saas_make_category_document('category-2-subcategory-1'),
                ],
            ),
            status=200,
            headers={},
            content_type='application/json',
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _saas_search_proxy.times_called == 2
    assert response.status == 200
    subcategory_1_in_response = False
    subcategory_2_in_response = False
    for item in response.json()['products']:
        if item['id'] == 'category-1-subcategory-1':
            subcategory_1_in_response = True
        if item['id'] == 'category-2-subcategory-1':
            subcategory_2_in_response = True
    assert subcategory_1_in_response is True
    assert subcategory_2_in_response is False


# Проверяем, что выдача категорий из SaaS обрезается по category_limit.
@experiments.SEARCH_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'categories_limit,expected_categories', [(0, 0), (1, 1), (4, 2)],
)
async def test_cut_categories_by_limit(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        grocery_products,
        categories_limit,
        expected_categories,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [
                    _saas_make_product_document('product-1'),
                    _saas_make_category_document('category-1-subcategory-1'),
                    _saas_make_category_document('category-2-subcategory-1'),
                ],
            ),
            status=200,
            headers={},
            content_type='application/json',
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'pro',
            'position': {'location': location},
            'categories_limit': categories_limit,
        },
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status == 200

    categories = 0
    for item in response.json()['products']:
        if item['type'] == 'subcategory' or item['type'] == 'category':
            categories = categories + 1
    assert categories == expected_categories


# Проверяем что при наличии поисковой подстановки для
# подкатегории или виртуальной категории ее вернут вместо title
@experiments.SEARCH_FLOW_INTERNAL
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.translations(
    virtual_catalog={
        'virtual_category_title_1': {'ru': 'virtual-category-1-title'},
        'virtual_category_title_2': {'ru': 'virtual-category-2-title'},
    },
    wms_categories_search_titles_testing={
        'category-1-subcategory-1_search_title': {'ru': 'synonym'},
    },
    virtual_categories_search_titles_testing={
        'virtual-category-1_search_title': {'ru': 'synonym'},
    },
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_SUBCATEGORY_SEARCH_TITLE={
        'keyset': 'wms_categories_search_titles_testing',
        'suffix': '_search_title',
    },
    GROCERY_LOCALIZATION_VIRTUAL_CATEGORY_SEARCH_TITLE={
        'keyset': 'virtual_categories_search_titles_testing',
        'suffix': '_search_title',
    },
    GROCERY_API_USE_SUBCATEGORY_SEARCH_TITLE=True,
    GROCERY_API_USE_VIRTUAL_CATEGORY_SEARCH_TITLE=True,
)
async def test_search_titles_for_categories(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_products,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={'search_results': [{'id': 'product-1', 'type': 'good'}]}
            if 'products' in request.query['allowed_items']
            else {
                'search_results': [
                    {
                        'id': virtual_category_1.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_2.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {'id': 'category-1-subcategory-1', 'type': 'subcategory'},
                    {'id': 'category-2-subcategory-1', 'type': 'subcategory'},
                ],
            },
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _mock_grocery_search.times_called == 2
    assert response.status == 200
    found_with_substitution = 0
    for item in response.json()['products']:
        if item['type'] == 'subcategory' or item['type'] == 'category':
            if (
                    item['id'] == 'category-1-subcategory-1'
                    or item['id'] == virtual_category_1.virtual_category_id
            ):
                found_with_substitution = found_with_substitution + 1
                assert item['search_title'] == 'synonym'
            else:
                assert 'search_title' not in item
    assert found_with_substitution == 2


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'pigeon_data_enabled',
    [
        pytest.param(False, marks=[experiments.PIGEON_DATA_DISABLED]),
        pytest.param(True, marks=[experiments.PIGEON_DATA_ENABLED]),
    ],
)
async def test_grocery_search_request_with_enabled_pigeon(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_products,
        pigeon_data_enabled,
):
    if pigeon_data_enabled:
        grocery_products.products_response_enabled = False
    else:
        grocery_products.menu_response_enabled = False

    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        assert (
            request.query['pigeon_data_enabled'] == 'true'
            if pigeon_data_enabled
            else 'false'
        )
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category_1.virtual_category_id,
                        'type': 'virtual_category',
                    },
                ],
            },
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _mock_grocery_search.times_called == 1
    assert response.status == 200
    response_products = response.json()['products']
    assert response_products
    for item in response_products:
        assert item['type'] == 'category'
        assert item['id'] == virtual_category_1.virtual_category_id


# Проверяем наличие информации о подкатегориях для товаров
@experiments.SEARCH_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('subcategories_count', [0, 1, 2])
async def test_search_products_parent_categories(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        mockserver,
        grocery_products,
        subcategories_count,
):
    location = [0, 0]
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    for i in range(subcategories_count):
        virtual_category.add_subcategory(
            subcategory_id=f'category-{i + 1}-subcategory-1',
        )
    grocery_p13n.add_modifier(product_id=product_id, value='1.2')

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = _saas_make_response(
            [_saas_make_product_document(product_id)],
        )
        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    subcategories_info = response.json()['products'][0]['subcategories']
    assert subcategories_count == len(subcategories_info)
    for i in range(subcategories_count):
        assert subcategories_info[i] == {
            'subcategory_id': f'category-{i + 1}-subcategory-1',
            'subcategory_title': f'category-{i + 1}-subcategory-1-title',
            'subcategory_path': {
                'layout_id': 'layout-1',
                'group_id': 'category-group-1',
                'virtual_category_id': 'virtual-category-1',
            },
        }


# Проверяем правильность шаблона: разделитель и количество знаков
@experiments.SEARCH_FLOW_SAAS
@pytest.mark.parametrize('locale', ['en', 'fr', 'ru'])
@pytest.mark.parametrize(
    'price,expected_result',
    [('5.30', '5.30'), ('5.25', '5.25'), ('1.001', '1.00')],
)
@pytest.mark.parametrize('currency', ['EUR', 'GBP', 'RUB'])
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'grocery': 0.01},
        'GBP': {'grocery': 0.01},
        '__default__': {'__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={
        'EUR': {'__default__': 2, 'iso4217': 2},
        'GBP': {'__default__': 2, 'iso4217': 2},
        'RUB': {'grocery': 2},
    },
    LOCALES_SUPPORTED=['en', 'fr', 'ru'],
)
async def test_price_format_and_trailing_zeros(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_products,
        mockserver,
        load_json,
        locale,
        price,
        expected_result,
        currency,
        grocery_depots,
):
    if currency == 'RUB':
        expected_result = expected_result.split('.')[0]

    location = const.LOCATION
    depot_id = const.DEPOT_ID

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=depot_id,
        location=location,
        currency=currency,
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location=location, currency=currency,
    )

    product_id = 'product-1'
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree={
            'categories': [{'id': 'category-2-subcategory-2'}],
            'products': [
                {
                    'full_price': price,
                    'id': product_id,
                    'category_ids': ['category-2-subcategory-2'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )

    grocery_p13n.add_modifier(product_id=product_id, value=price)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = _saas_make_response(
            [_saas_make_product_document(product_id)],
        )
        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.invalidate_caches()

    json = {'text': 'query-text', 'position': {'location': location}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=json,
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    actual_price = response.json()['products'][0]['pricing']['price_template']
    if locale == 'en':
        assert actual_price == '$SIGN${}$CURRENCY$'.format(expected_result)
    if locale in ('fr', 'ru'):
        expected_result = expected_result.replace('.', ',')
        assert actual_price == '{} $SIGN$$CURRENCY$'.format(expected_result)


@pytest.mark.config(GROCERY_API_RETRIEVE_STOCKS_LIMIT=3)
@pytest.mark.parametrize(
    'products_count,expected_times_called',
    [
        pytest.param(1, 1, id='one_product'),
        pytest.param(0, 0, id='no_products'),
        pytest.param(7, 3, id='indivisible'),
        pytest.param(9, 3, id='divisible'),
    ],
)
async def test_search_get_stocks_by_parts(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        products_count,
        expected_times_called,
):
    depot_id = 'test-depot-id'
    location = [0, 0]
    category_tree = {
        'categories': [{'id': 'category-1-subcategory-1'}],
        'depot_ids': [depot_id],
        'markdown_products': [],
        'products': [],
    }
    for i in range(products_count):
        category_tree['products'].append(
            {
                'category_ids': ['category-1-subcategory-1'],
                'full_price': '2.2',
                'id': 'product-{}'.format(i),
                'rank': i + 1,
            },
        )
    product_stocks = load_json('overlord_catalog_products_stocks.json')
    common.prepare_overlord_catalog(
        overlord_catalog,
        location,
        depot_id=depot_id,
        category_tree=category_tree,
        product_stocks=product_stocks,
    )

    @mockserver.json_handler('overlord-catalog/internal/v1/catalog/v1/stocks')
    def mock_stocks(request):
        return {
            'stocks': [
                {
                    'product_id': request.json['product_ids'][i],
                    'in_stock': '10',
                    'quantity_limit': '10',
                }
                for i in range(len(request.json['product_ids']))
            ],
        }

    for i in range(products_count):
        grocery_search.add_product(product_id='product-{}'.format(i))
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'product', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    assert mock_stocks.times_called == expected_times_called


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'allowed',
    [
        pytest.param(
            ['virtual_categories', 'categories'],
            marks=(
                pytest.mark.experiments3(
                    filename='search_flow_exp_category_and_v_cat_allowed.json',
                )
            ),
            id='categories and virtual_categories',
        ),
        pytest.param(
            [],
            marks=(
                pytest.mark.experiments3(
                    filename='search_flow_exp_no_category_allowed.json',
                )
            ),
            id='no category allowed',
        ),
    ],
)
async def test_search_flow_allowed_category_type(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        load_json,
        allowed,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = [0, 0]
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        if request.query['allowed_items'] != 'products':
            assert (
                request.query['allowed_items'].split(',').sort()
                == allowed.sort()
            )
        return mockserver.make_response(
            json={'search_results': []}, status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
    )
    assert response.status_code == 200
    if allowed:
        assert _mock_grocery_search.times_called == 1
    else:
        # empty allowed_category list skips category search
        assert _mock_grocery_search.times_called == 1


MARKET_CLIENT = 'lavka'
MARKET_PLACE = 'prime'
MARKET_PP = 18
MARKET_RIDS = 213
MARKET_REGSET = 1
MARKET_NUMDOC = 20
MARKET_FESH = 100
MARKET_LOCALE = common_search.MARKET_LOCALE
MARKET_ENTITY = 'offer'
MARKET_ALLOW_COLLAPSING = 0
MARKET_FORCE_BUSINESS_ID = 1
MARKET_ENABLE_FOODTECH_OFFERS = 1
MARKET_FESH_BY_LOCALE = {MARKET_LOCALE: MARKET_FESH}
MARKET_COMPLETE_QUERY = 'lavka'
MARKET_SHOW_URLS = 'offercard'
MARKET_COUNTRY_ISO3 = common_search.MARKET_COUNTRY_ISO3
MARKET_REGION_ID = common_search.MARKET_REGION_ID

MARKET_SERVICE_ID = common_search.MARKET_SERVICE_ID
MARKET_EATS_AND_LAVKA_ID = common_search.MARKET_EATS_AND_LAVKA_ID
MARKET_FEED_ID = common_search.MARKET_FEED_ID
MARKET_PARTNER_ID = common_search.MARKET_PARTNER_ID
MARKET_BUSINESS_ID = common_search.MARKET_BUSINESS_ID


@pytest.mark.config(
    GROCERY_API_MARKET_REPORT_SETTINGS={
        'client': MARKET_CLIENT,
        'fesh_by_locale': MARKET_FESH_BY_LOCALE,
        'numdoc': MARKET_NUMDOC,
        'pp': MARKET_PP,
        'complete_query': True,
    },
)
@experiments.SEARCH_FLOW_MARKET
async def test_prepare_market_request(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        mbi_api,
        mockserver,
        grocery_depots,
):
    location = [0, 0]
    query_text = 'query-text'
    ip_address = '::ffff:176.60.169.56'

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        legacy_depot_id=MARKET_EATS_AND_LAVKA_ID,
    )

    mbi_api.add_depot(
        MARKET_SERVICE_ID,
        MARKET_EATS_AND_LAVKA_ID,
        MARKET_FEED_ID,
        MARKET_PARTNER_ID,
        MARKET_BUSINESS_ID,
    )
    grocery_depots.add_depot(
        depot_test_id=int(MARKET_EATS_AND_LAVKA_ID),
        location=location,
        country_iso3=MARKET_COUNTRY_ISO3,
        region_id=MARKET_REGION_ID,
    )

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        query = request.query

        assert query['client'] == MARKET_CLIENT
        assert query['place'] == MARKET_PLACE
        assert int(query['pp']) == MARKET_PP
        assert int(query['rids']) == MARKET_RIDS
        assert int(query['regset']) == MARKET_REGSET
        assert 'ignore-has-gone' not in query
        assert query['text'] == query_text
        assert int(query['numdoc']) == MARKET_NUMDOC
        assert int(query['market_max_offers_per_shop_count']) == MARKET_NUMDOC
        assert int(query['fesh']) == MARKET_PARTNER_ID
        assert query['locale'] == MARKET_LOCALE
        assert query['entities'] == MARKET_ENTITY
        assert query['country-iso3'] == MARKET_COUNTRY_ISO3
        assert int(query['region-id']) == MARKET_REGION_ID
        assert int(query['allow-collapsing']) == MARKET_ALLOW_COLLAPSING
        assert (
            int(query['market-force-business-id']) == MARKET_FORCE_BUSINESS_ID
        )
        assert (
            int(query['enable-foodtech-offers'])
            == MARKET_ENABLE_FOODTECH_OFFERS
        )
        assert query['complete-query'] == MARKET_COMPLETE_QUERY
        assert 'reqid' in query
        _market_report_proxy.reqid = query['reqid']
        assert query['show-urls'] == MARKET_SHOW_URLS
        assert query['ip'] == ip_address
        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=request_json,
        headers={
            'X-Request-Language': MARKET_LOCALE,
            'X-Remote-IP': ip_address,
        },
    )
    assert response.headers['X-YaTraceId'] == _market_report_proxy.reqid


MARKET_FOODTECH_CGI = 'complete-query=lavka'


# Проверка на пробрсывание market_search_flow_api_params
# с помощью /lavka/v1/api/v1/search-report
@pytest.mark.parametrize(
    'request_json,place_param',
    [
        pytest.param(
            {
                'text': 'test-query',
                'external_depot_id': '123',
                'search_flow': 'market',
                'search_flow_api_params': {
                    'market_search_flow_api_params': {
                        'foodtech_cgi': MARKET_FOODTECH_CGI,
                        'place': 'lavka',
                    },
                },
            },
            'lavka',
            id='place',
        ),
        pytest.param(
            {
                'text': 'test-query',
                'external_depot_id': '123',
                'search_flow': 'market',
                'search_flow_api_params': {
                    'market_search_flow_api_params': {
                        'foodtech_cgi': MARKET_FOODTECH_CGI,
                    },
                },
            },
            'prime',
            id='no place',
        ),
    ],
)
async def test_foodtech_cgi_in_market(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        mockserver,
        request_json,
        place_param,
):
    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        assert request.query['foodtech-cgi'] == MARKET_FOODTECH_CGI
        assert request.query['place'] == place_param

        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search-report', json=request_json,
    )


# Проверка на пробрсывание foodtech_cgi
# с помощью /lavka/v1/api/v1/search
@experiments.create_search_flow_experiment(
    'market',
    search_flow_api_params={
        'market_search_flow_api_params': {'foodtech_cgi': MARKET_FOODTECH_CGI},
    },
)
async def test_foodtech_cgi_in_experiment(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        assert request.query['foodtech-cgi'] == MARKET_FOODTECH_CGI

        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert _market_report_proxy.times_called == 1
    assert response.status_code == 200


@pytest.mark.config(
    GROCERY_API_MARKET_REPORT_SETTINGS={
        'client': MARKET_CLIENT,
        'fesh_by_locale': MARKET_FESH_BY_LOCALE,
    },
)
@experiments.SEARCH_FLOW_MARKET
async def test_search_with_market(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        mockserver,
):
    location = [0, 0]
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_p13n.add_modifier(product_id=product_id, value='1.2')

    @mockserver.json_handler('market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json=_make_market_search_response(
                [_make_market_offer('offer', 'product-1')],
            ),
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=request_json,
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    found_product = response_json['products'][0]
    assert found_product['id'] == product_id
    assert found_product['pricing']['price'] == '2'
    assert (
        'discount_pricing' in found_product
        and found_product['discount_pricing']['price'] == '1'
    )
    assert _market_report_proxy.times_called == 1


# Проверяет, что фолбечится на grocery-search при 400 от маркетного поиска.
@pytest.mark.config(
    GROCERY_API_MARKET_REPORT_SETTINGS={
        'client': MARKET_CLIENT,
        'fesh_by_locale': MARKET_FESH_BY_LOCALE,
    },
)
@experiments.SEARCH_FLOW_MARKET
async def test_short_queries_with_market(
        taxi_grocery_api, overlord_catalog, load_json, mockserver,
):
    location = [0, 0]
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json={
                'error': {
                    'code': 'TOO_SHORT_REQUEST',
                    'message': 'Your request (q) is supershort.',
                },
            },
            headers={},
            content_type='application/json',
            status=400,
        )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={'search_results': [{'id': product_id, 'type': 'good'}]},
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'q',
            'position': {'location': location},
            'offer_id': 'test-offer',
            'categories_limit': 0,
        },
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    found_product = response_json['products'][0]
    assert found_product['id'] == product_id
    assert _market_report_proxy.times_called == 1
    assert _mock_grocery_search.times_called == 1


# Проверяем что в выдаче поиска маркета будут категории из grocery-search
@experiments.SEARCH_FLOW_MARKET
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_search_categories_to_market(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_products,
):
    @mockserver.json_handler('market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json=_make_market_search_response(
                [_make_market_offer('offer', 'product-1')],
            ),
            headers={},
            content_type='application/json',
            status=200,
        )

    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category.virtual_category_id,
                        'type': 'virtual_category',
                    },
                ],
            },
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'pro', 'position': {'location': location}},
        headers={'X-Request-Language': 'ru'},
    )
    assert _market_report_proxy.times_called == 1
    assert _mock_grocery_search.times_called == 2
    assert response.status == 200
    item = response.json()['products'][0]
    assert item['type'] == 'category'
    assert item['id'] == 'virtual-category-1'


TEST_LOCATION = [0, 0]


# Проверяем что используем дефолтное значение ограничения
# на количество категорий, если не получили в запросе. Если
# получили, то используем это ограничение
@pytest.mark.config(GROCERY_API_SEARCH_CATEGORIES_LIMIT=2)
@experiments.SEARCH_FLOW_SAAS
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'request_json,expected_limit',
    [
        pytest.param(
            {
                'text': 'query-text',
                'position': {'location': TEST_LOCATION},
                'offer_id': 'test-offer',
            },
            2,
            id='no_categories_limit',
        ),
        pytest.param(
            {
                'text': 'query-text',
                'position': {'location': TEST_LOCATION},
                'offer_id': 'test-offer',
                'categories_limit': 3,
            },
            3,
            id='categories_limit',
        ),
    ],
)
async def test_search_categories_limit(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_products,
        request_json,
        expected_limit,
):
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, TEST_LOCATION,
    )
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-1', available=True,
    )
    virtual_category_3 = category_group.add_virtual_category(test_id='3')
    virtual_category_3.add_subcategory(
        subcategory_id='category-3-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-3-subcategory-1', available=True,
    )
    virtual_category_4 = category_group.add_virtual_category(test_id='4')
    virtual_category_1.add_subcategory(
        subcategory_id='category-4-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-4-subcategory-1', available=True,
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [_saas_make_product_document('product-1')],
            ),
            status=200,
            headers={},
            content_type='application/json',
        )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category_1.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_2.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_3.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_4.virtual_category_id,
                        'type': 'virtual_category',
                    },
                ],
            },
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=request_json,
        headers={'X-Request-Language': 'ru'},
    )

    assert _mock_grocery_search.times_called == 2
    assert response.status == 200
    response_json = response.json()
    products = response_json['products']
    category_cnt = 0
    for item in products:
        if item['type'] == 'category':
            category_cnt += 1
    assert category_cnt <= expected_limit


# Проверяем, получили мы showUid в response
# от market-report
@experiments.SEARCH_FLOW_MARKET
async def test_show_uid_in_response(
        taxi_grocery_api, mockserver, overlord_catalog, load_json,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json={
                'search': {
                    'results': [
                        {
                            'entity': 'offer',
                            'shop': {'feed': {'offerId': 'product-1'}},
                            'showUid': '1',
                        },
                    ],
                },
            },
            headers={},
            content_type='application/json',
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'test-query', 'position': {'location': location}},
    )

    assert _market_report_proxy.times_called == 1
    assert response.status == 200
    response_json = response.json()
    assert response_json['products'][0]['show_market_report_uid'] == '1'


# Возвращает ошибку, если лавка не найдена
async def test_report_returns_error_if_depot_not_found(taxi_grocery_api):
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search-report',
        json={
            'text': 'test-query',
            'external_depot_id': '1',
            'search_flow': 'internal',
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# Ходит в указанный search_flow
@pytest.mark.parametrize('search_flow', ['internal', 'saas', 'market'])
async def test_report_uses_specific_search_flow(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        load_json,
        search_flow,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'

    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=depot_id,
    )
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )

    @mockserver.json_handler('market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json=_make_market_search_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _grocery_search(request):
        return mockserver.make_response(
            json={'search_results': []},
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search-report',
        json={
            'text': 'test-query',
            'external_depot_id': legacy_depot_id,
            'search_flow': search_flow,
        },
    )

    assert search_flow != 'internal' or _grocery_search.times_called == 1
    assert search_flow != 'saas' or _saas_search_proxy.times_called == 2
    assert search_flow != 'market' or _market_report_proxy.times_called == 1


# Ходит в искомый поисковой бэкенд и фильтрует товары по лавке.
@pytest.mark.parametrize('search_flow', ['internal', 'saas', 'market'])
async def test_report_filters_results_by_depot(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        load_json,
        search_flow,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'

    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=depot_id,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )
    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_catalog_products_data.json'),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json('overlord_catalog_products_stocks.json'),
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )
    product_in_depot = 'product-1'
    product_not_in_depot = 'product-not-in-depot'

    @mockserver.json_handler('market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json=_make_market_search_response(
                [
                    _make_market_offer('offer', product_in_depot),
                    _make_market_offer('offer', product_not_in_depot),
                ],
            ),
            headers={},
            content_type='application/json',
            status=200,
        )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [
                    _saas_make_product_document(product_in_depot),
                    _saas_make_product_document(product_not_in_depot),
                ],
            ),
            headers={},
            content_type='application/json',
            status=200,
        )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {'id': product_in_depot, 'type': 'good'},
                    {'id': product_not_in_depot, 'type': 'good'},
                ],
            },
            headers={},
            content_type='application/json',
            status=200,
        )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search-report',
        json={
            'text': 'test-query',
            'external_depot_id': legacy_depot_id,
            'search_flow': search_flow,
        },
    )
    assert response.status_code == 200
    products = response.json()['products']
    assert len(products) == 1
    assert products[0]['id'] == product_in_depot


# проверяем что цена в поиске повышается если товар
# задан в эксперрименте повышения цен
# повышающий коэфициет = 3.5, цена товара = 2.2, скидка = 1.
# тогда финальная цена = floor(3.5*2.2)=7, скидочная цена 7-1
@experiments.GROCERY_PRICE_RISE_MAP
async def test_modes_product_price_rise(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        grocery_search,
        load_json,
):
    location = [0, 0]
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    grocery_p13n.add_modifier(product_id=product_id, value='1')

    grocery_search.add_product(product_id='product-1')

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
        'limit': 1,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    data = response.json()['products'][0]
    assert data['id'] == 'product-1'
    assert data['pricing'] == {
        'price_template': '7 $SIGN$$CURRENCY$',
        'price': '7',
    }
    assert data['discount_pricing'] == {
        'price_template': '6 $SIGN$$CURRENCY$',
        'price': '6',
    }


@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_no_empty_or_hided_results_in_search(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        taxi_config,
        grocery_products,
        load_json,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    item_meta = '{"hide_if_empty":' + 'true' + '}'
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(
        test_id='1', item_meta=item_meta,
    )
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_3 = category_group.add_virtual_category(
        test_id='3', item_meta=item_meta,
    )
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-1', available=False,
    )
    virtual_category_3.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )
    overlord_catalog.set_category_availability(
        category_id='category-2-subcategory-2', available=False,
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category_1.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_2.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {
                        'id': virtual_category_3.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {'id': 'category-1-subcategory-1', 'type': 'subcategory'},
                    {'id': 'category-2-subcategory-2', 'type': 'subcategory'},
                ],
            },
            status=200,
        )

    json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=json,
    )
    assert response.status == 200

    virtual_category_1_in_response = False
    virtual_category_2_in_response = False
    virtual_category_3_in_response = False
    subcategory_1_in_response = False
    subcategory_2_in_response = False
    for item in response.json()['products']:
        if item['id'] == virtual_category_1.virtual_category_id:
            virtual_category_1_in_response = True
        if item['id'] == virtual_category_2.virtual_category_id:
            virtual_category_2_in_response = True
        if item['id'] == virtual_category_3.virtual_category_id:
            virtual_category_3_in_response = True
        if item['id'] == 'category-1-subcategory-1':
            subcategory_1_in_response = True
        if item['id'] == 'category-2-subcategory-2':
            subcategory_2_in_response = True
    assert virtual_category_1_in_response
    assert subcategory_1_in_response
    assert not virtual_category_2_in_response
    assert not virtual_category_3_in_response
    assert not subcategory_2_in_response


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.SEARCH_FLOW_SAAS
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
async def test_no_subcat_if_virtual_cat_hidden_in_search(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_products,
        load_json,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    item_meta = '{"hide_if_empty_key":' + 'true' + '}'
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')

    item_meta = (
        '{"hide_if_subcategory_is_empty":' + '"category-1-subcategory-1"' + '}'
    )
    virtual_category = category_group.add_virtual_category(
        test_id='1', item_meta=item_meta,
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=False,
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-2')
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-2', available=True,
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response(
                [_saas_make_product_document('product-1')],
            ),
            status=200,
            headers={},
            content_type='application/json',
        )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        if request.query['allowed_items'] == 'categories':
            return mockserver.make_response(
                json={
                    'search_results': [
                        {
                            'id': 'category-1-subcategory-2',
                            'type': 'subcategory',
                        },
                    ],
                },
                status=200,
            )
        return mockserver.make_response(
            json={'search_results': []}, status=200,
        )

    json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=json,
    )
    assert response.status == 200
    assert _mock_grocery_search.times_called == 2

    subcategory_2_in_response = False
    for item in response.json()['products']:
        if item['id'] == 'category-1-subcategory-2':
            subcategory_2_in_response = True
    assert not subcategory_2_in_response


# Проверяем, что проверяются все родительские категории для подката,
# а так же проверяем что в пути подката указывается доступная категория
@experiments.SEARCH_CATEGORIES_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_all_parent_categories_checked(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        saas_search_proxy,
):
    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    subcategory = 'category-1-subcategory-1'
    meta = '{"hide_if_subcategory_is_empty": "category-1-subcategory-2"}'
    virtual_category_1 = category_group.add_virtual_category(
        test_id='1', item_meta=meta,
    )
    virtual_category_2 = category_group.add_virtual_category(test_id='2')
    virtual_category_3 = category_group.add_virtual_category(
        test_id='3', item_meta=meta,
    )
    virtual_category_1.add_subcategory(subcategory_id=subcategory)
    virtual_category_2.add_subcategory(subcategory_id=subcategory)
    virtual_category_3.add_subcategory(subcategory_id=subcategory)
    overlord_catalog.set_category_availability(
        category_id=subcategory, available=True,
    )
    saas_search_proxy.add_subcategory(subcategory_id=subcategory)

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=request_json,
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )

    assert response.status_code == 200
    products = response.json()['products']
    assert len(products) == 1
    assert products[0]['id'] == subcategory
    assert products[0]['virtual_category_id'] == 'virtual-category-2'


@experiments.CASHBACK_EXPERIMENT
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_hidden_params_special_category(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_products,
        load_json,
):
    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    item_meta = '{"hide_if_empty":' + 'true' + '}'
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group.add_virtual_category(
        test_id='1', item_meta=item_meta, special_category='cashback-caas',
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category_1.virtual_category_id,
                        'type': 'virtual_category',
                    },
                ],
            },
            status=200,
        )

    json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=json,
    )
    assert response.status == 200
    virtual_category_in_response = False
    for item in response.json()['products']:
        if item['id'] == virtual_category_1.virtual_category_id:
            virtual_category_in_response = True
    assert virtual_category_in_response


# проверяем что для подкатегорий и виртуальных категорий
# передается поле deep_link
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_search_deep_link_for_response_products(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
):
    location = [0, 0]
    category_deep_link = 'virtual-category-deeplink'
    subcategory_deep_link = 'subcategory-deeplink'

    categories_data = [
        {
            'category_id': 'category-1-subcategory-1',
            'description': 'category-1-subcategory-1-description',
            'image_url_template': (
                'category-1-subcategory-1-image-url-template'
            ),
            'title': 'category-1-subcategory-1-title',
            'deep_link': subcategory_deep_link,
        },
    ]
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, categories_data=categories_data,
    )

    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id='1', add_short_title=True, deep_link=category_deep_link,
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        return mockserver.make_response(
            json={
                'search_results': [
                    {
                        'id': virtual_category.virtual_category_id,
                        'type': 'virtual_category',
                    },
                    {'id': 'category-1-subcategory-1', 'type': 'subcategory'},
                ],
            },
            status=200,
        )

    json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=json,
    )
    assert response.status_code == 200
    assert {
        item['deep_link']
        for item in response.json()['products']
        if 'deep_link' in item
    } == {category_deep_link, subcategory_deep_link}


@pytest.mark.translations(
    wms_attributes={
        'sahar': {'en': 'shugar'},
        'fish': {'en': 'translated_fish'},
    },
)
@pytest.mark.config(
    GROCERY_API_ATTRIBUTES_ICONS={
        'sahar': {'icon_link': 'sahar_icon'},
        'fish': {'icon_link': 'fish_icon', 'big_icon_link': 'big_fish_icon'},
    },
)
async def test_search_attributes_in_response(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_search,
        grocery_depots,
):
    location = [0, 0]
    depot_id = '123'
    product_id = 'product-1'
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data=products_data,
        depot_id=depot_id,
    )
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=depot_id,
        location=location,
    )

    grocery_search.add_product(product_id=product_id)

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
        'limit': 1,
        'user_preferences': {
            'important_ingredients': ['sahar'],
            'main_allergens': ['fish', 'some more'],
            'custom_tags': ['halal'],
        },
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    options = response.json()['products'][0]['options']
    assert options['important_ingredients'] == [
        {'attribute': 'sahar', 'title': 'shugar', 'icon_link': 'sahar_icon'},
    ]
    assert options['main_allergens'] == [
        {
            'attribute': 'fish',
            'title': 'translated_fish',
            'icon_link': 'fish_icon',
            'big_icon_link': 'big_fish_icon',
        },
    ]
    assert options['custom_tags'] == [{'attribute': 'halal', 'title': 'halal'}]


@experiments.SEARCH_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('is_filter_enabled', [False, True])
@pytest.mark.parametrize(
    'product_id',
    [
        pytest.param('product-1', id='with categories'),
        pytest.param('product-4', id='without categories'),
    ],
)
async def test_filter_products_by_layout(
        taxi_grocery_api,
        overlord_catalog,
        mockserver,
        load_json,
        grocery_products,
        grocery_search,
        grocery_depots,
        taxi_config,
        is_filter_enabled,
        product_id,
):
    taxi_config.set(
        GROCERY_API_FILTER_PRODUCTS_IN_SEARCH={
            'category_availability': False,
            'layout_availability': is_filter_enabled,
        },
    )

    location = [0, 0]
    depot_id = '123'

    products_data = load_json('overlord_catalog_products_data.json')

    category_tree = load_json('overlord_catalog_category_tree_for_filter.json')

    stocks = load_json('overlord_catalog_products_stocks.json')

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        category_tree=category_tree,
        product_stocks=stocks,
        depot_id=depot_id,
    )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=depot_id,
        location=location,
    )

    grocery_search.add_product(product_id=product_id)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = _saas_make_response(
            [_saas_make_product_document(product_id)],
        )
        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    subcategories = next(
        product_in_tree
        for product_in_tree in category_tree['products']
        if product_in_tree['id'] == product_id
    )['category_ids']

    assert response.status_code == 200

    if is_filter_enabled and not subcategories:
        assert not response.json()['products']
    else:
        assert response.json()['products']
        assert response.json()['products'][0]['id'] == product_id


SEARCH_API_FLOW_PARAMS_FULL = {
    'search_flow': 'market',
    'search_flow_api_params': {
        'market_search_flow_api_params': {'foodtech_cgi': MARKET_FOODTECH_CGI},
    },
}
SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY = {
    'search_flow': 'market',
    'search_flow_api_params': {'market_search_flow_api_params': {}},
}
SEARCH_API_FLOW_PARAMS_ONLY_FLOW = {'search_flow': 'market'}


# проверяем, передаётся ли параметр из экспа
# grocery_api_search_use_popularity
# при запросе в ручку маркетного поиска
@pytest.mark.parametrize(
    'search_flow_api_params,use_popularity_flow,foodtech_cgi',
    [
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            'do_not_use',
            'complete-query=lavka',
            id='full_params-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            'use_general_popularity',
            'complete-query=lavka&use-popularity=1',
            id='full_params-general_popularity',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            'use_normalized_popularity',
            'complete-query=lavka&use-popularity-normalized=1',
            id='full_params-normalized',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            'do_not_use',
            None,
            id='foodtech_cgi_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            'use_general_popularity',
            'use-popularity=1',
            id='foodtech_cgi_empty-general_popularity',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            'use_normalized_popularity',
            'use-popularity-normalized=1',
            id='foodtech_cgi_empty-normalized',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            'do_not_use',
            None,
            id='params_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            'use_general_popularity',
            'use-popularity=1',
            id='params_empty-general_popularity',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            'use_normalized_popularity',
            'use-popularity-normalized=1',
            id='params_empty-normalized',
        ),
    ],
)
async def test_use_popularity_exp(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        mockserver,
        experiments3,
        search_flow_api_params,
        foodtech_cgi,
        use_popularity_flow,
):
    experiments3.add_experiment(
        name='grocery_api_search_flow',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': search_flow_api_params,
            },
        ],
    )

    experiments3.add_experiment(
        name='grocery_api_search_use_popularity',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Disabled',
                'predicate': {'type': 'true'},
                'value': {'use_popularity_flow': use_popularity_flow},
            },
        ],
    )

    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        if 'foodtech-cgi' in request.query:
            assert request.query['foodtech-cgi'] == foodtech_cgi
        else:
            assert foodtech_cgi is None

        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'test-query', 'position': {'location': location}},
    )
    assert _market_report_proxy.times_called == 1


# Проверяем, что продукты в выдаче помечаются лайками
@experiments.SEARCH_FLOW_SAAS
async def test_search_favorites(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        mockserver,
        grocery_fav_goods,
):
    location = [0, 0]
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    grocery_p13n.add_modifier(product_id=product_id, value='1.2')

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        response = _saas_make_response(
            [_saas_make_product_document(product_id)],
        )
        return mockserver.make_response(
            json=response,
            headers={},
            content_type='application/json',
            status=200,
        )

    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id=product_id,
    )
    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json=request_json,
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )

    assert response.status_code == 200
    assert response.json()['products'][0]['is_favorite']


# проверяем, передаётся ли параметр из экспа
# grocery_api_search_use_private_label
# при запросе в ручку маркетного поиска
@pytest.mark.parametrize(
    'search_flow_api_params,use_private_label,foodtech_cgi',
    [
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            False,
            'complete-query=lavka',
            id='full_params-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            True,
            'complete-query=lavka&use-private-label=1',
            id='full_params-use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            False,
            None,
            id='foodtech_cgi_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            True,
            'use-private-label=1',
            id='foodtech_cgi_empty-use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            False,
            None,
            id='params_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            True,
            'use-private-label=1',
            id='params_empty-use',
        ),
    ],
)
async def test_use_private_label_exp(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        mockserver,
        experiments3,
        search_flow_api_params,
        use_private_label,
        foodtech_cgi,
):
    experiments3.add_experiment(
        name='grocery_api_search_flow',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': search_flow_api_params,
            },
        ],
    )

    experiments3.add_experiment(
        name='grocery_api_search_use_private_label',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Disabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': use_private_label},
            },
        ],
    )

    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        if 'foodtech-cgi' in request.query:
            assert request.query['foodtech-cgi'] == foodtech_cgi
        else:
            assert foodtech_cgi is None

        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'test-query', 'position': {'location': location}},
    )
    assert _market_report_proxy.times_called == 1


# проверяем, передаётся ли параметр из экспа
# grocery_api_search_use_front_margin
# при запросе в ручку маркетного поиска
@pytest.mark.parametrize(
    'search_flow_api_params,use_front_margin,foodtech_cgi',
    [
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            False,
            'complete-query=lavka',
            id='full_params-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FULL,
            True,
            'complete-query=lavka&use-front-margin=1',
            id='full_params-use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            False,
            None,
            id='foodtech_cgi_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_FOODTECH_EMPTY,
            True,
            'use-front-margin=1',
            id='foodtech_cgi_empty-use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            False,
            None,
            id='params_empty-not_use',
        ),
        pytest.param(
            SEARCH_API_FLOW_PARAMS_ONLY_FLOW,
            True,
            'use-front-margin=1',
            id='params_empty-use',
        ),
    ],
)
async def test_use_front_margin_exp(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        mockserver,
        experiments3,
        search_flow_api_params,
        use_front_margin,
        foodtech_cgi,
):
    experiments3.add_experiment(
        name='grocery_api_search_flow',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': search_flow_api_params,
            },
        ],
    )

    experiments3.add_experiment(
        name='grocery_api_search_use_front_margin',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Disabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': use_front_margin},
            },
        ],
    )

    location = [0, 0]

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        if 'foodtech-cgi' in request.query:
            assert request.query['foodtech-cgi'] == foodtech_cgi
        else:
            assert foodtech_cgi is None

        return mockserver.make_response(
            json={'search': {'results': []}},
            headers={},
            content_type='application/json',
            status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'test-query', 'position': {'location': location}},
    )
    assert _market_report_proxy.times_called == 1


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.SEARCH_FLOW_INTERNAL
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
@experiments.SEARCH_FILTER_CATEGORIES_FOUND_BY_NOT_EQUALLY_MATCHED_PREFIXES
async def test_includes_filter_not_equally_matched_prefixes(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        load_json,
):
    depot_id = 'test-depot'
    legacy_depot_id = '123'
    location = [0, 0]
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_location(
        location=location, depot_id=depot_id, legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        location=location,
    )

    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_catalog_category_tree.json'),
    )

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search(request):
        if 'products' in request.query['allowed_items']:
            assert 'filter_not_equally_matched_prefixes' not in request.query
        else:
            assert (
                ('filter_not_equally_matched_prefixes' in request.query)
                and (
                    request.query['filter_not_equally_matched_prefixes']
                    == 'true'
                )
            )

        return mockserver.make_response(
            json={'search_results': []}, status=200,
        )

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'query-text-for-product-1',
            'position': {'location': location},
            'offer_id': 'test-offer',
        },
    )
    assert _mock_grocery_search.times_called == 2


# Проверка 'catalog_paths' в ответе ручки
@pytest.mark.parametrize(
    'layout_id',
    [
        pytest.param(
            'layout-1', marks=experiments.create_modes_layouts_exp('layout-1'),
        ),
        pytest.param(
            'layout-2', marks=experiments.create_modes_layouts_exp('layout-2'),
        ),
    ],
)
@pytest.mark.parametrize('need_catalog_paths', [None, False, True])
async def test_catalog_paths(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_search,
        offers,
        now,
        layout_id,
        need_catalog_paths,
):
    product_id = 'some-product-id'
    offer_id = 'some-offer-id'
    common.setup_catalog_for_paths_test(
        overlord_catalog, grocery_products, product_id,
    )
    grocery_search.add_product(product_id=product_id)
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    headers = {'X-Request-Language': 'en'}
    request_body = {
        'text': 'query-for-{}'.format(product_id),
        'position': {'location': common.DEFAULT_LOCATION},
        'offer_id': offer_id,
    }
    if need_catalog_paths is not None:
        request_body['need_catalog_paths'] = need_catalog_paths

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', headers=headers, json=request_body,
    )
    assert response.status_code == 200

    response_data = response.json()
    if need_catalog_paths is True:
        assert 'catalog_paths' in response_data['products'][0]
        common.check_catalog_paths(
            response_data['products'][0]['catalog_paths'], layout_id,
        )
    else:
        assert 'catalog_paths' not in response_data['products'][0]


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
@experiments.SEARCH_CATEGORIES_FLOW_INTERNAL
async def test_search_items_order(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [common_combo.COMBO_ID],
            [
                common_combo.PRODUCT_GROUP1,
                common_combo.PRODUCT_GROUP2,
                common_combo.PRODUCT_GROUP3,
            ],
            'combo_revision_1',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            ('meta-product-1', '0'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
    )

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_combo(metaproduct_id=common_combo.COMBO_ID)
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_virtual_category(
        virtual_category_id='virtual-category-1',
    )

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert [
        'virtual-category-1',
        'product-1',
        common_combo.COMBO_ID,
        'product-2',
    ] == [product['id'] for product in response_json['products']]


@experiments.SEARCH_FLOW_SAAS
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('is_filter_enabled', [False, True])
@pytest.mark.parametrize('available', [False, True])
async def test_filter_products_by_category_availability(
        taxi_grocery_api,
        overlord_catalog,
        saas_search_proxy,
        load_json,
        grocery_search,
        grocery_depots,
        taxi_config,
        is_filter_enabled,
        available,
):
    taxi_config.set(
        GROCERY_API_FILTER_PRODUCTS_IN_SEARCH={
            'category_availability': is_filter_enabled,
            'layout_availability': False,
        },
    )

    location = [0, 0]
    depot_id = '123'
    product_id = 'product-1'

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        category_tree=load_json(
            'overlord_catalog_category_tree_for_filter.json',
        ),
        depot_id=depot_id,
    )
    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=available,
    )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=depot_id,
        location=location,
    )

    grocery_search.add_product(product_id=product_id)

    saas_search_proxy.add_product(product_id=product_id)

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200

    if is_filter_enabled and not available:
        assert not response.json()['products']
    else:
        assert response.json()['products']
        assert response.json()['products'][0]['id'] == product_id
