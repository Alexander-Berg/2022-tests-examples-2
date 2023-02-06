# pylint: disable=redefined-outer-name
import json
import re

import pytest

from taxi.stq import async_worker_ng

import eats_retail_globus_parser.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from eats_retail_globus_parser.generated.service.swagger.models import (
    api as models,
)

pytest_plugins = ['eats_retail_globus_parser.generated.service.pytest_plugins']

MDS_TEST_PREFIX = '/mds_s3/eats_retail_globus_parser'


@pytest.fixture
def parser_mocks(mockserver, load_json, mock_globus_parsing):
    @mock_globus_parsing('/fastcache/Price/GetPricesForMarket')
    def get_prices(request):
        data = load_json('globus_responses_data/prices.json')
        response_data = data[int(request.args['PageNumber']) - 1]
        print(response_data)
        return mockserver.make_response(json=response_data)

    @mock_globus_parsing('/fastcache/Stock/GetStocksForMarket')
    def get_stocks(request):
        data = load_json('globus_responses_data/stocks.json')
        response_data = data[int(request.args['PageNumber']) - 1]
        return mockserver.make_response(json=response_data)

    @mock_globus_parsing('/fastcache/Availability/GetAvailabilitiesForMarket')
    def get_availabilities(request):
        data = load_json('globus_responses_data/availabilities.json')
        response_data = data[int(request.args['PageNumber']) - 1]
        return mockserver.make_response(json=response_data)

    @mock_globus_parsing('/fastcache/Product/GetProductsForMarket')
    def get_products(request):
        data = load_json('globus_responses_data/nomenclature.json')
        response_data = data[int(request.args['PageNumber']) - 1]
        return mockserver.make_response(json=response_data)

    @mock_globus_parsing('/catalog/Catalog/GetCategoriesByParentId')
    def get_categories(request):
        if 'StoreId' in request.args:
            return load_json('globus_responses_data/categories_store.json')
        return load_json('globus_responses_data/categories_full.json')

    return {
        'get_prices': get_prices,
        'get_stocks': get_stocks,
        'get_availabilities': get_availabilities,
        'get_products': get_products,
        'get_categories': get_categories,
    }


@pytest.fixture
def proxy_mocks(mock_rate_limiter_proxy, mockserver):
    @mock_rate_limiter_proxy('/quota')
    async def _quota(request):
        return mockserver.make_response(
            request._data,  # pylint: disable=protected-access
            content_type='application/flatbuffer',
        )


@pytest.fixture
def stq_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=0, reschedule_counter=1, queue='',
    )


@pytest.fixture(name='parse_task_stq_runner')
def _parse_task_stq_runner(stq_runner, load_json):
    async def call_stq(task_type, kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'

        await getattr(
            stq_runner, f'eats_retail_globus_parser_{task_type}',
        ).call(
            task_id='task_id',
            args=(),
            kwargs={
                'retail_data': models.RequestDetail.deserialize(
                    load_json('stq_kwargs.json')[
                        kwargs_name
                    ],  # проверка на валидность жсона
                ).serialize(),
            },
        )

    return call_stq


@pytest.fixture(name='invalidate_cache_stq_runner')
def _invalidate_cache_stq_runner(stq_runner, load_json):
    async def call_stq(kwargs_name=None):
        if kwargs_name is None:
            kwargs_name = 'default'

        await stq_runner.eats_retail_globus_parser_invalidate_cache.call(
            task_id='task_id',
            args=(),
            kwargs={
                'cache_data': models.Cache.deserialize(
                    load_json('stq_cache_kwargs.json')[
                        kwargs_name
                    ],  # проверка на валидность жсона
                ).serialize(),
            },
        )

    return call_stq


@pytest.fixture
def task_uuid():
    return 'task_uuid__1'


@pytest.fixture
def task_details_factory(load_json, task_uuid):
    def factory(**kwargs):
        default = load_json('task_details_default.json')
        default['uuid'] = task_uuid
        data = {**default, **kwargs}
        return models.TaskDetails(**data)

    return factory


@pytest.fixture
def mds_mocks(mockserver, load_json):
    @mockserver.handler('/mds_s3', prefix=True)
    async def mock(request, **kwargs):
        one_of_types = r'(availability|nomenclature|prices|stocks)'
        cache_types = (
            r'(prices|products|categories|stocks|availability|quantum)'
        )

        if 'cache' in request.path:
            match = re.match(
                rf'^{MDS_TEST_PREFIX}/integration/collector'
                rf'/{one_of_types}/cache_{cache_types}_(.*).json$',
                request.path,
            )
            assert match

            last_modified = 'Thu, 02 Aug 2021 12:03:13 GMT'
            if request.method == 'PUT':
                return mockserver.make_response(
                    f'<body></body>',
                    headers={'ETag': 'asdf', 'Last-Modified': last_modified},
                )

            cache = load_json(f'mds_data/cache/{match.groups()[1]}.json')
            return mockserver.make_response(
                f'{json.dumps(cache)}',
                headers={'ETag': 'asdf', 'Last-Modified': last_modified},
            )

        match = re.match(
            rf'^{MDS_TEST_PREFIX}/integration/collector'
            rf'/{one_of_types}/{one_of_types}_(.*)_(.*).json$',
            request.path,
        )
        assert match

        expected = load_json(f'mds_data/{match.groups()[0]}.json')

        assert expected == request.json

        result = json.dumps(request.json)
        result = result.replace('<', '&lt;')
        result = result.replace('>', '&gt;')

        return mockserver.make_response(
            f'<Body>{result}</Body>', headers={'ETag': 'asdf'},
        )

    return mock


@pytest.fixture
def procaas_parsed_mocks(mock_processing, load_json, task_uuid):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == task_uuid
        assert request.json['phase'] == 'parsed'
        assert request.headers['X-Idempotency-Token'] == f'parser_{task_uuid}'

        return {'event_id': task_uuid}

    return create_event


@pytest.fixture
def procaas_fallback_mocks(mock_processing, load_json, task_uuid):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == task_uuid
        assert request.json['phase'] == 'fallback'
        assert request.headers['X-Idempotency-Token'] == f'parser_{task_uuid}'

        return {'event_id': task_uuid}

    return create_event


def check_stq(stq_mock, **kwargs):
    call_args = stq_mock.next_call()

    assert call_args['kwargs'] == kwargs
