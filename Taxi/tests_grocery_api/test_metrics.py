import asyncio
import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import common
from . import const
from . import experiments


def _metric(name):
    return f'grocery_api_{name}'


TOTAL_SEARCHES = _metric('total_searches')
EMPTY_SEARCHES = _metric('empty_searches')
FALLBACK_SEARCHES = _metric('fallback_searches')
AVAILABLE_FROM_SEARCH = _metric('available_from_search_results')

LOCATION = const.LOCATION

UTC_TZ = datetime.timezone.utc
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

# percent = available_count / found_count
async def test_availability_percent(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        taxi_grocery_api_monitor,
):
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)

    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_product(product_id='product-3')

    grocery_p13n.add_modifier(product_id='product-1', value='0.1')
    grocery_p13n.add_modifier(product_id='product-2', value='1')
    grocery_p13n.add_modifier(product_id='product-3', value='2')

    request_json = {
        'text': 'query-text-for-product',
        'position': {'location': LOCATION},
        'offer_id': 'test-offer',
        'limit': 100,
    }
    wait_metrics_time = 6
    await asyncio.sleep(wait_metrics_time)
    await taxi_grocery_api.tests_control(reset_metrics=True)

    iter_count = 4
    for i in range(iter_count):
        grocery_search.add_product(product_id=f'unknown-product-{3 * i + 1}')
        grocery_search.add_product(product_id=f'unknown-product-{3 * i + 2}')
        grocery_search.add_product(product_id=f'unknown-product-{3 * i + 3}')
        response = await taxi_grocery_api.post(
            '/lavka/v1/api/v1/search', json=request_json,
        )
        assert response.status_code == 200

    # после выполнения имеем набор метрик:
    # {33, 22, 16, 13}

    await asyncio.sleep(wait_metrics_time)

    availability_percent = (
        await taxi_grocery_api_monitor.get_metric(
            'grocery_api_grocery_availability_percent',
        )
    )['1min']

    # Из за особенностей реализации метрик пустые эпохи учитываются
    # и все портят. Поэтому добавляем еще сравнение с 0.
    metrics_min = 0
    expected_metrics_max = 33
    expected_metrics_min = 13
    assert availability_percent['min'] in [metrics_min, expected_metrics_min]
    assert availability_percent['max'] == expected_metrics_max
    assert metrics_min <= availability_percent['avg'] <= expected_metrics_max


async def test_available_from_search_metrics(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        taxi_grocery_api_monitor,
        mocked_time,
):
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)

    grocery_search.add_product(product_id='unknown-product-1')
    grocery_search.add_product(product_id='unknown-product-2')
    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_product(product_id='product-3')

    grocery_p13n.add_modifier(product_id='product-1', value='0.1')
    grocery_p13n.add_modifier(product_id='product-2', value='1')
    grocery_p13n.add_modifier(product_id='product-3', value='2')

    request_json = {
        'text': 'query-text-for-product',
        'position': {'location': LOCATION},
        'offer_id': 'test-offer',
        'limit': 100,
    }

    mocked_time.set(NOW_DT)
    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=AVAILABLE_FROM_SEARCH,
    ) as collector:
        iter_count = 10
        for i in range(iter_count):
            grocery_search.add_product(product_id=f'unknown-product-{i + 3}')
            if i == iter_count - 1:
                # на последнем шаге ждем, чтобы все метрики проросли
                mocked_time.set(NOW_DT + datetime.timedelta(seconds=10))
            response = await taxi_grocery_api.post(
                '/lavka/v1/api/v1/search', json=request_json,
            )
            assert response.status_code == 200

    # после выполнения имеем набор метрик:
    # {33, 28, 25, 22, 20, 18, 16, 15, 14, 13}
    metrics = collector.collected_metrics

    percentile_to_value = {}
    for metric in metrics:
        assert metric.labels['sensor'] == AVAILABLE_FROM_SEARCH
        assert metric.labels['search_engine'] == 'grocery-search'
        percentile_to_value[metric.labels['percentile']] = metric.value

    assert percentile_to_value == {'p2': 14, 'p5': 14, 'p20': 15, 'p50': 20}


SAAS_ITEM_ID_KEY = 's_item_id'
SAAS_ITEM_TYPE_KEY = 'i_item_type'
SAAS_ITEM_TYPE_PRODUCT = '2'
SAAS_URL_PREFIX_PRODUCT = 'product'


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


# Выбираем пойсковый движок, который будет использоваться для поиска,
# мокаем его ответ в 200, и проверяем,
# что метрика увеличила нужное значение нужное число раз
@pytest.mark.parametrize(
    'total_search_engine',
    [
        pytest.param('saas', marks=experiments.SEARCH_FLOW_SAAS),
        pytest.param('market', marks=experiments.SEARCH_FLOW_MARKET),
        pytest.param('internal', marks=experiments.SEARCH_FLOW_INTERNAL),
    ],
)
async def test_total_searches_metric(
        taxi_grocery_api,
        overlord_catalog,
        grocery_search,
        load_json,
        taxi_grocery_api_monitor,
        mocked_time,
        mockserver,
        total_search_engine,
):

    product_id = 'product-1'

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

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)

    grocery_search.add_product(product_id='product-1')

    request_json = {
        'text': 'query-text-for-product',
        'position': {'location': LOCATION},
        'offer_id': 'test-offer',
        'limit': 100,
    }

    mocked_time.set(NOW_DT)
    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=TOTAL_SEARCHES,
    ) as collector:
        iter_count = 3
        for _ in range(iter_count):
            response = await taxi_grocery_api.post(
                '/lavka/v1/api/v1/search', json=request_json,
            )
            assert response.status_code == 200

    metric = collector.get_single_collected_metric()

    assert metric.value == 3
    assert metric.labels == {
        'search_engine': total_search_engine,
        'country': 'Russia',
        'sensor': TOTAL_SEARCHES,
    }


# Выбираем пойсковый движок, который будет возвращать пустую поисковую выдачу,
# мокаем его ответ в 200, и проверяем,
# что метрика увеличила нужное значение нужное число раз
@pytest.mark.parametrize(
    'empty_search_engine',
    [
        pytest.param('saas', marks=experiments.SEARCH_FLOW_SAAS),
        pytest.param('market', marks=experiments.SEARCH_FLOW_MARKET),
        pytest.param('internal', marks=experiments.SEARCH_FLOW_INTERNAL),
    ],
)
async def test_empty_searches_metric(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        taxi_grocery_api_monitor,
        mocked_time,
        mockserver,
        empty_search_engine,
):
    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return mockserver.make_response(
            json=_saas_make_response([]),
            headers={},
            content_type='application/json',
            status=200,
        )

    @mockserver.json_handler('/market-report/yandsearch')
    def _market_report_proxy(request):
        return mockserver.make_response(
            json={'search': {'results': []}}, status=200,
        )

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)

    grocery_p13n.add_modifier(product_id='product-1', value='0.1')

    request_json = {
        'text': 'query-text-for-product',
        'position': {'location': LOCATION},
        'offer_id': 'test-offer',
        'limit': 100,
    }

    mocked_time.set(NOW_DT)
    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=EMPTY_SEARCHES,
    ) as collector:
        iter_count = 3
        for _ in range(iter_count):
            response = await taxi_grocery_api.post(
                '/lavka/v1/api/v1/search', json=request_json,
            )
            assert response.status_code == 200

    metric = collector.get_single_collected_metric()

    assert metric.value == 3
    assert metric.labels == {
        'search_engine': empty_search_engine,
        'country': 'Russia',
        'sensor': EMPTY_SEARCHES,
    }


def _brake_search_engine(
        search_flow, grocery_search, saas_search_proxy, market_report_proxy,
):
    if search_flow == 'internal':
        grocery_search.should_failed()
    if search_flow == 'saas':
        saas_search_proxy.should_failed()
    if search_flow == 'market':
        market_report_proxy.should_failed()


# Выбираем поисковый движок, который будем фоллбэчить, мокаем его ответ в 500,
# И проверяем, что метрика увеличила нужное значение нужное число раз
@pytest.mark.parametrize(
    'search_engine_to_fallback, fallback_engine',
    [
        pytest.param('saas', 'internal'),
        pytest.param('market', 'internal'),
        pytest.param('internal', 'saas'),
    ],
)
async def test_fallback_searches(
        taxi_grocery_api,
        taxi_grocery_api_monitor,
        load_json,
        experiments3,
        mocked_time,
        overlord_catalog,
        grocery_search,
        saas_search_proxy,
        market_report_proxy,
        search_engine_to_fallback,
        fallback_engine,
):
    experiments3.add_experiment3_from_marker(
        experiments.create_search_flow_experiment(
            search_engine_to_fallback, fallback_flow=fallback_engine,
        ),
        load_json,
    )
    _brake_search_engine(
        search_engine_to_fallback,
        grocery_search,
        saas_search_proxy,
        market_report_proxy,
    )
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)
    mocked_time.set(NOW_DT)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=FALLBACK_SEARCHES,
    ) as collector:
        iter_count = 3
        for _ in range(iter_count):
            response = await taxi_grocery_api.post(
                '/lavka/v1/api/v1/search',
                json={
                    'text': 'query-text',
                    'position': {'location': LOCATION},
                },
            )
            assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    assert metric.value == 3
    assert metric.labels == {
        'search_engine': search_engine_to_fallback,
        'country': 'Russia',
        'sensor': FALLBACK_SEARCHES,
    }


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'sensor,label,label_value',
    [
        (
            'modes_root_sessions_application',
            'app_name',
            'Market native (android)',
        ),
        ('modes_root_sessions_city', 'city_name', 'Moscow'),
        ('modes_root_sessions_country', 'country', 'Russia'),
    ],
)
@pytest.mark.parametrize('yandex_uid', ['some_uid', None])
async def test_modes_root_sessions_metric(
        taxi_grocery_api,
        overlord_catalog,
        taxi_grocery_api_monitor,
        grocery_products,
        sensor,
        label,
        label_value,
        yandex_uid,
):
    common.build_basic_layout(grocery_products)
    location = LOCATION
    common.prepare_overlord_catalog(
        overlord_catalog, location, depot_id=const.DEPOT_ID,
    )
    offer_id = 'some-offer-id'

    json = {
        'modes': ['grocery', 'upsale'],
        'offer_id': offer_id,
        'position': {'location': location},
    }
    async with metrics_helpers.MetricsCollector(
            taxi_grocery_api_monitor, sensor=f'grocery_api_{sensor}',
    ) as collector:
        response = await taxi_grocery_api.post(
            '/lavka/v1/api/v1/modes/root',
            json=json,
            headers={
                'X-Request-Application': 'app_name=market_android',
                'X-Yandex-UID': yandex_uid,
            },
        )
        assert response.status_code == 200

    metric = collector.get_single_collected_metric()

    if yandex_uid is None:
        assert metric is None
    else:
        assert metric.value == 1
        assert metric.labels == {
            label: label_value,
            'sensor': f'grocery_api_{sensor}',
        }
