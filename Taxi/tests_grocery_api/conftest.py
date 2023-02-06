# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name
# pylint: disable=too-many-lines

import re

from grocery_api_plugins import *  # noqa: F403 F401
from grocery_mocks import (  # pylint: disable=E0401
    grocery_menu as mock_grocery_menu,
)
import pytest

from . import common
from . import combo_products_common as common_combo
from . import common_search
from . import const
from . import experiments

DEFAULT_TOTAL_TIME = 0
DEFAULT_COOKING_TIME = 0
DEFAULT_DELIVERY_TIME = 0

DEFAULT_OFFER_ID = 'default-offer-id'
DEFAULT_OFFER_TIME = '2021-01-21T10:00:00+00:00'


@pytest.fixture(name='add_depots', autouse=True)
async def add_depots(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=const.DEPOT_ID,
        location=const.LOCATION,
        auto_add_zone=False,
    )


@pytest.fixture(name='offers', autouse=True)
def simple_offer_service(mockserver):
    class Context:
        def __init__(self):
            self.offers_created = 0

            # Some predefined cache
            self.offer_storage = {}
            for i in range(5):
                # Warning: time should be rounded
                self.add_offer(
                    str(i),
                    {
                        'place_id': str(110 + i),
                        'offer_time': '2020-02-20T10:05:00+00:00',
                    },
                    {'surge_info': {'load_level': i}},
                )

        def add_offer(self, offer_id, params, payload):
            if offer_id not in self.offer_storage.keys():
                self.offer_storage[offer_id] = {
                    'params': params,
                    'payload': payload,
                }

        def add_offer_elementwise(
                self, offer_id, offer_time, depot_id, location,
        ):
            if offer_id not in self.offer_storage.keys():
                self.offer_storage[offer_id] = {
                    'params': {
                        'depot_id': depot_id,
                        'lat_lon': ';'.join([str(item) for item in location]),
                    },
                    'payload': {
                        'request_time': offer_time.astimezone().isoformat(),
                    },
                }

        @property
        def created_times(self):
            return self.offers_created

        @property
        def matched_times(self):
            return match.times_called

        @property
        def match_create_times_called(self):
            return _match_create.times_called

    ctx = Context()

    @mockserver.json_handler('/grocery-offers/v1/create')
    def _create(request):
        body = request.json
        ctx.add_offer(str(ctx.offers_created), body['params'], body['payload'])
        ctx.offers_created += 1

        return {'id': str(ctx.offers_created - 1)}

    @mockserver.json_handler('/grocery-offers/v1/create/multi')
    def _create_multi(request):
        offers = request.json['offers']
        ans = []
        index = ctx.offers_created
        for offer in offers:
            ctx.add_offer(
                str(len(ctx.offer_storage)), offer['params'], offer['payload'],
            )
            ans.append(str(index))
            index += 1

        ctx.offers_created += len(offers)
        return {'ids': ans}

    @mockserver.json_handler('/grocery-offers/v1/match/multi')
    def match(request):
        body_offers = request.json['offers']
        ans = []
        for offer_id in ctx.offer_storage:
            offer = ctx.offer_storage[offer_id]
            for body in body_offers:
                if offer['params'] == body['params']:
                    result = {
                        'matched': True,
                        'offer_params': offer['params'],
                        'payload': offer['payload'],
                    }
                    ans.append(result)
        return {'offers': ans}

    @mockserver.json_handler(
        '/grocery-offers/internal/v1/offers/v1/match-create',
    )
    def _match_create(request):
        offer_id = None
        if request.json['current_id']:
            offer_id = request.json['current_id']

        # ищем по id
        if offer_id is not None:
            if offer_id in ctx.offer_storage:
                offer = ctx.offer_storage[offer_id]
                return {
                    'id': offer_id,
                    'matched': True,
                    'offer_params': offer['params'],
                    'payload': offer['payload'],
                }

        # ищем по параметрам
        params = request.json['params']
        for offer_id, offer in ctx.offer_storage.items():
            if offer['params'] == params:
                return {
                    'id': offer_id,
                    'matched': True,
                    'offer_params': offer['params'],
                    'payload': offer['payload'],
                }

        # не нашли — значит, надо создать
        new_id = str(ctx.offers_created)
        ctx.add_offer(new_id, request.json['params'], request.json['payload'])
        ctx.offers_created += 1

        return {
            'id': new_id,
            'matched': False,
            'offer_params': request.json['params'],
            'payload': request.json['payload'],
        }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge-grocery')
    def calc(request):
        results = []
        for place_id in request.json['place_ids']:
            lvl = 0
            if 100 <= place_id < 200:
                lvl = place_id % 10
            else:
                continue
            item = {
                'calculator_name': 'calc_surge_grocery_v1',
                'results': [
                    {
                        'place_id': place_id,
                        'result': {'load_level': lvl, 'delivery_zone_id': 55},
                    },
                ],
            }
            results.append(item)

        return {'results': results, 'errors': []}

    @mockserver.json_handler('/grocery-offers/v1/retrieve/by-id')
    def retrieve(request):
        offer_id = request.json['id']
        offer = {}
        if offer_id in ctx.offer_storage.keys():
            offer = ctx.offer_storage[offer_id]
            offer['id'] = offer_id
            offer['tag'] = 'offer_tag'
            offer['payload']['request_time'] = offer['params']['offer_time']
            offer['due'] = '2022-02-20T10:05:00+00:00'
        return offer

    return ctx


def get_int_query_param(request, param, default):
    return int(request.query[param]) if param in request.query else default


def compare(allowed_items, category_result):
    mapped_allowed = []
    for allowed in allowed_items:
        if allowed == 'products':
            mapped_allowed.append('good')
        if allowed == 'combos':
            mapped_allowed.append('combo')
        if allowed == 'categories':
            mapped_allowed.extend(['subcategory', 'virtual_category'])
    return category_result in mapped_allowed


@pytest.fixture(name='grocery_search', autouse=True)
def mock_grocery_search(mockserver):
    class Context:
        def __init__(self):
            self.was_error_ = False
            self.found_products_v2_ = []

        def add_product(self, *, product_id):
            self.found_products_v2_.append({'id': product_id, 'type': 'good'})

        def add_combo(self, *, metaproduct_id):
            self.found_products_v2_.append(
                {'id': metaproduct_id, 'type': 'combo'},
            )

        def add_subcategory(self, *, subcategory_id):
            self.found_products_v2_.append(
                {'id': subcategory_id, 'type': 'subcategory'},
            )

        def add_virtual_category(self, *, virtual_category_id):
            self.found_products_v2_.append(
                {'id': virtual_category_id, 'type': 'virtual_category'},
            )

        def internal_search_v2_times_called(self):
            return _mock_grocery_search_v2.times_called

        def should_failed(self):
            self.was_error_ = True

    context = Context()

    @mockserver.json_handler('/grocery-search/internal/v1/search/v2/search')
    def _mock_grocery_search_v2(request):
        if context.was_error_:
            return mockserver.make_response(status=500)

        result = []
        if 'allowed_items' not in request.query.keys():
            result = context.found_products_v2_
        else:
            allowed_items = request.query['allowed_items'].split(',')
            if not allowed_items:
                result = context.found_products_v2_
            else:
                for product in context.found_products_v2_:
                    if compare(allowed_items, product['type']):
                        result.append(product)
        start = get_int_query_param(request, 'offset', 0)
        stop = start + get_int_query_param(
            request, 'limit', len(result) - start,
        )
        return {'search_results': result[start:stop]}

    return context


SAAS_SERVICE = 'grocery'
SAAS_PREFIX = 123
SAAS_CUSTOM_PREFIX = 999
SAAS_MISPELL = 'force'
SAAS_ITEM_ID_KEY = 's_item_id'
SAAS_ITEM_TYPE_KEY = 'i_item_type'
SAAS_ITEM_TYPE_CATEGORY = '1'
SAAS_ITEM_TYPE_PRODUCT = '2'
SAAS_ITEM_TYPE_COMBO = '3'
SAAS_URL_PREFIX_PRODUCT = 'product'
SAAS_URL_PREFIX_CATEGORY = 'category'
SAAS_URL_PREFIX_COMBO = 'combo'


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


def _saas_make_combo_document(metaproduct_id, relevance=1, mtime=100):
    return _saas_make_document(
        _saas_make_document_url(SAAS_URL_PREFIX_COMBO, metaproduct_id),
        [
            _saas_make_item_id_gta(metaproduct_id),
            _saas_make_item_type_gta(SAAS_ITEM_TYPE_COMBO),
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


def _get_allowed_items(request):
    item_types = None

    template = None
    if 'template' in request.query:
        template = request.query['template']

    if template:
        # Примеры:
        # %request% && i_item_type:1
        # %request% && ( i_item_type:2 | i_item_type:3 )
        item_types = re.findall(f'{SAAS_ITEM_TYPE_KEY}:([0-9]+)', template)

    is_correct = item_types is None
    if not is_correct:
        for item_type in item_types:
            is_correct = is_correct or (
                item_type
                in [
                    SAAS_ITEM_TYPE_CATEGORY,
                    SAAS_ITEM_TYPE_PRODUCT,
                    SAAS_ITEM_TYPE_COMBO,
                ]
            )

    assert is_correct

    if item_types is not None:
        allow_categories = SAAS_ITEM_TYPE_CATEGORY in item_types
        if allow_categories:
            return True, False, False

        allow_products = SAAS_ITEM_TYPE_PRODUCT in item_types
        allow_combos = SAAS_ITEM_TYPE_COMBO in item_types
        return False, allow_products, allow_combos

    return True, True, True


@pytest.fixture(name='saas_search_proxy', autouse=True)
def mock_saas_search_proxy(mockserver):
    class Context:
        def __init__(self):
            self.was_error_ = False
            self.found_products_ = []
            self.found_categories_ = []
            self.found_combos_ = []

        def add_product(self, *, product_id):
            self.found_products_.append(product_id)

        def add_subcategory(self, *, subcategory_id):
            self.found_categories_.append(subcategory_id)

        def add_metaproduct(self, *, metaproduct_id):
            self.found_combos_.append(metaproduct_id)

        def should_failed(self):
            self.was_error_ = True

        def saas_search_times_called(self):
            return _mock_saas_search_proxy.times_called

    context = Context()

    @mockserver.json_handler('/saas-search-proxy/')
    def _mock_saas_search_proxy(request):
        if context.was_error_:
            return mockserver.make_response(status=500)

        documents = []
        allow_categories, allow_products, allow_combos = _get_allowed_items(
            request,
        )
        if allow_categories:
            for category_id in context.found_categories_:
                documents.append(_saas_make_category_document(category_id))

        if allow_products:
            for product_id in context.found_products_:
                documents.append(_saas_make_product_document(product_id))

        if allow_combos:
            for metaproduct_id in context.found_combos_:
                documents.append(_saas_make_combo_document(metaproduct_id))

        return mockserver.make_response(
            json=_saas_make_response(documents),
            headers={},
            content_type='application/json',
            status=200,
        )

    return context


def _make_market_offer(product_id):
    return {
        'entity': 'offer',
        'shop': {'feed': {'offerId': product_id}},
        'showUid': '1',
    }


@pytest.fixture(name='market_report_proxy', autouse=True)
def mock_market_report_proxy(mockserver):
    class Context:
        def __init__(self):
            self.was_error_ = False
            self.found_products_ = []
            self.expected_query_params = {}

        def add_product(self, *, product_id):
            self.found_products_.append(product_id)

        def should_failed(self):
            self.was_error_ = True

        @property
        def times_called(self):
            return _market_report_proxy.times_called

        def expect_query_params(self, *, params):
            self.expected_query_params = params

    context = Context()

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        if context.expected_query_params:
            for _, (p, v) in enumerate(context.expected_query_params.items()):
                assert (
                    p in request.query and request.query[p] == v
                    if v
                    else p not in request.query
                )

        if context.was_error_:
            return mockserver.make_response(status=500)

        results = []
        for found_product in context.found_products_:
            results.append(_make_market_offer(found_product))
        return mockserver.make_response(
            json={'search': {'results': results}},
            content_type='application/json',
            status=200,
        )

    return context


@pytest.fixture(name='umlaas_grocery_eta', autouse=True)
def mock_umlaas_eta(mockserver):
    class Context:
        def __init__(self):
            self.predicted_times = []
            self.times_called = 0
            self.umlaas_grocery_eta_times_called = 0
            self.umlaas_grocery_eta_prediction = {}
            self.request_id = None

        def set_request_id(self, request_id):
            self.request_id = request_id

        def set_prediction(
                self,
                eta_min,
                eta_max,
                total_time=0,
                cooking_time=0,
                delivery_time=0,
        ):
            self.umlaas_grocery_eta_prediction = {
                'total_time': total_time,
                'cooking_time': cooking_time,
                'delivery_time': delivery_time,
                'promise': {'min': eta_min, 'max': eta_max},
            }

        def add_prediction(
                self,
                eta_min,
                eta_max,
                total_time=0,
                cooking_time=0,
                delivery_time=0,
        ):
            self.set_prediction(
                eta_min * 60,
                eta_max * 60,
                total_time * 60,
                cooking_time * 60,
                delivery_time * 60,
            )
            times = {'boundaries': {'min': eta_min, 'max': eta_max}}
            if total_time is not None:
                times['total_time'] = total_time
            if cooking_time is not None:
                times['cooking_time'] = cooking_time
            if delivery_time is not None:
                times['delivery_time'] = delivery_time

            self.predicted_times.append(
                {'id': len(self.predicted_times), 'times': times},
            )

    context = Context()

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        context.umlaas_grocery_eta_times_called += 1
        if context.request_id is not None:
            assert context.request_id == request.query['offer_id']
        return context.umlaas_grocery_eta_prediction

    return context


@pytest.fixture(name='grocery_dispatch', autouse=True)
def mock_grocery_dispatch(mockserver):
    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/check-price',
    )
    def _mock_eta_prediction(request):
        return {'price': 123.56}


@pytest.fixture(
    name='parametrized_layout_source',
    params=[
        pytest.param(
            (True, False),
            marks=[experiments.PIGEON_DATA_DISABLED],
            id='products-source',
        ),
        pytest.param(
            (False, True),
            marks=[experiments.PIGEON_DATA_ENABLED],
            id='pigeon-source',
        ),
    ],
)
def _parametrize_layout_source(request, grocery_products):
    (products_response_enabled, menu_response_enabled) = request.param
    grocery_products.products_response_enabled = products_response_enabled
    grocery_products.menu_response_enabled = menu_response_enabled


DIFFERENT_LAYOUT_SOURCE = pytest.mark.usefixtures('parametrized_layout_source')

_get_products_from_modes_response = lambda json: list(
    product for product in json['products'] if product['type'] == 'good'
)


@pytest.fixture(
    name='grocery_modes',
    params=[
        pytest.param(
            (
                '/lavka/v1/api/v1/modes/category',
                _get_products_from_modes_response,
            ),
            id='category',
        ),
        pytest.param(
            ('/lavka/v1/api/v1/modes/product', lambda json: [json['product']]),
            id='product',
        ),
        pytest.param(
            (
                '/lavka/v1/api/v1/modes/category-group',
                _get_products_from_modes_response,
            ),
            id='category-group',
        ),
        pytest.param(
            ('/lavka/v1/api/v1/search', _get_products_from_modes_response),
            id='search',
        ),
        pytest.param(
            ('/lavka/v1/api/v1/modes/root', _get_products_from_modes_response),
            id='root',
        ),
    ],
)
def _grocery_modes(
        taxi_grocery_api,
        load_json,
        overlord_catalog,
        grocery_products,
        grocery_search,
        request,
):
    class Context:
        def __init__(self, request):
            (self.handler, self.get_products) = request.param

        def add_product(
                self,
                product_id='product_id',
                subcategory_id='category-1-subcategory-1',
        ):
            common.prepare_overlord_catalog_json(
                load_json, overlord_catalog, const.LOCATION,
            )
            layout = grocery_products.add_layout(test_id='1')
            category_group = layout.add_category_group(test_id='1')
            category_group.layout_meta = (
                category_group.layout_meta[:-1]
                + f', "show_as_carousels": true'
                + f', "products_per_category_count": {5}'
                + '}'
            )
            virtual_category = category_group.add_virtual_category(test_id='1')
            virtual_category.add_subcategory(subcategory_id=subcategory_id)
            grocery_search.add_product(product_id=product_id)
            return [layout, virtual_category]

        async def post(
                self, product_id, layout, virtual_category, locale='en',
        ):
            return await taxi_grocery_api.post(
                self.handler,
                json=common.build_grocery_mode_request(
                    self.handler,
                    layout.layout_id,
                    layout.group_ids_ordered[0],
                    virtual_category.virtual_category_id,
                    product_id=product_id,
                    query='query-text',
                ),
                headers={'X-Request-Language': locale},
            )

        def get_products(self, json):
            return self.get_products(json)

    context = Context(request)

    return context


@pytest.fixture
def add_test_offer(offers, now):
    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )


@pytest.fixture
def add_default_depot(overlord_catalog, mbi_api, grocery_depots):
    overlord_catalog.add_location(
        location=common.DEFAULT_LOCATION,
        depot_id=const.DEPOT_ID,
        legacy_depot_id=common_search.MARKET_EATS_AND_LAVKA_ID,
    )

    mbi_api.add_depot(
        common_search.MARKET_SERVICE_ID,
        common_search.MARKET_EATS_AND_LAVKA_ID,
        common_search.MARKET_FEED_ID,
        common_search.MARKET_PARTNER_ID,
        common_search.MARKET_BUSINESS_ID,
    )
    grocery_depots.add_depot(
        depot_id=const.DEPOT_ID,
        depot_test_id=int(common_search.MARKET_EATS_AND_LAVKA_ID),
        location=common.DEFAULT_LOCATION,
        country_iso3=common_search.MARKET_COUNTRY_ISO3,
        region_id=common_search.MARKET_REGION_ID,
    )


@pytest.fixture
def prepare_default_combo(grocery_menu, grocery_products, overlord_catalog):
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
            (common_combo.COMBO_ID, '0'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
    )
