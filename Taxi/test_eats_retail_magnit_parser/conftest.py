# pylint: disable=redefined-outer-name
import json
import re

import pytest

from eats_retail_magnit_parser import utils
import eats_retail_magnit_parser.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_retail_magnit_parser.generated.service.pytest_plugins']

BASIC_AUTH = utils.b64encode('test_login:test_password')
MDS_TEST_PREFIX = '/mds_s3/eats_retail_magnit_parser'
TASK_ID = 'task_id'


@pytest.fixture
def magnit_mocks(mockserver, load_json):
    token = load_json('test_token.json')['token']

    @mockserver.handler('/authentication/token')
    def get_token(request):
        assert request.headers['Authorization'] == f'Basic {BASIC_AUTH}'
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler(r'/stores/(?P<place_id>\w+)/stock', regex=True)
    def get_stock(request, place_id):
        assert request.headers['Authorization'] == f'Bearer {token}'
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

    @mockserver.handler(
        r'/stores/(?P<place_id>\w+)/catalog/categories', regex=True,
    )
    def get_categories(request, place_id):
        assert request.headers['Authorization'] == f'Bearer {token}'
        return mockserver.make_response(
            json.dumps(load_json('test_request_categories.json')), 200,
        )

    @mockserver.handler(
        r'/stores/(?P<place_id>\w+)/catalog/products', regex=True,
    )
    def get_products(request, place_id):
        assert request.headers['Authorization'] == f'Bearer {token}'
        return mockserver.make_response(
            json.dumps(load_json('test_request_products.json')), 200,
        )

    return {
        'get_token': get_token,
        'get_stock': get_stock,
        'get_categories': get_categories,
        'get_products': get_products,
    }


@pytest.fixture
def mds_mocks(mockserver, load_json):
    async def put(request):
        one_of_types = r'(availability|nomenclature|prices|stocks)'
        assert re.match(
            rf'^{MDS_TEST_PREFIX}/integration/collector'
            rf'/{one_of_types}/{one_of_types}_(.*)_(.*).json$',
            request.path,
        )

        place_id = re.search(r'_(place_id.*).json', request.path).group(1)
        mds_data = load_json('mds_data.json')
        expected = mds_data[place_id]

        assert expected['place_id'] == 'place_id'
        assert request.json['place_id'] == 'place_id'
        assert expected == request.json

        result = json.dumps(request.json)
        result = result.replace('<', '&lt;')
        result = result.replace('>', '&gt;')

        return mockserver.make_response(
            f'<Body>{result}</Body>', headers={'ETag': 'asdf'},
        )

    async def get(request):
        mds_data = json.dumps(load_json('existing_mds_data.json'))
        return mockserver.make_response(
            f'<Body>{mds_data}</Body>', headers={'ETag': 'asdf'},
        )

    @mockserver.handler('/mds_s3', prefix=True)
    async def mock(request, **kwargs):
        if request.method == 'PUT':
            return await put(request)
        if request.method == 'GET':
            return await get(request)
        raise NotImplementedError(f'{request.method} method not implemented')

    return mock


@pytest.fixture
def procaas_parsed_mocks(mock_processing, load_json):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == TASK_ID
        assert request.json['phase'] == 'parsed'
        assert request.headers['X-Idempotency-Token'] == f'parser_{TASK_ID}'

        return {'event_id': TASK_ID}

    return create_event


@pytest.fixture
def procaas_fallback_mocks(mock_processing, load_json):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        assert request.query['item_id'] == TASK_ID
        assert request.json['phase'] == 'fallback'
        assert request.headers['X-Idempotency-Token'] == f'parser_{TASK_ID}'

        return {'event_id': TASK_ID}

    return create_event
