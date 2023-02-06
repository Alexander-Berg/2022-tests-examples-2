# pylint: disable=redefined-outer-name
from aiohttp import web
from lxml import etree
import pytest

import process_automation_salesforce_esb.generated.service.pytest_init  # noqa: F401,E501

pytest_plugins = [
    'process_automation_salesforce_esb.generated.service.pytest_plugins',
]


@pytest.fixture
def mock_balance(mockserver, load):
    def _do_mock(method_response):
        @mockserver.handler('/balance/xmlrpctvm')
        def _handler(request):
            parser = etree.XMLParser(resolve_entities=False)
            root = etree.fromstring(request.get_data(), parser)
            method_name = root.xpath('//methodName[1]')[0].text

            if method_name in method_response:
                fname = method_response[method_name]
                response_body = load(fname)
            else:
                raise ValueError(method_name)

            assert method_name

            return mockserver.make_response(response_body, 200)

        return _handler

    return _do_mock


@pytest.fixture
def mock_limits(mock_salesforce):
    def _wrapper(response):
        @mock_salesforce('/services/data/v50.0/limits')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_auth(mock_salesforce):
    @mock_salesforce('/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_solomon(mockserver):
    def _wrapper():
        @mockserver.json_handler('/solomon/')
        async def _handler(request):
            return {}

        return _handler

    return _wrapper


@pytest.fixture
def create_object_mock(request, patch):
    def wrapper(expected_data, root, response):
        @patch(root)
        async def _create_person(*args, **kwargs):
            assert args == expected_data
            return response

    return wrapper


@pytest.fixture
def create_collateral_mock(request, patch):
    def wrapper(expected_data, root, response):
        @patch(root)
        async def _create_collateral(*args, **kwargs):
            assert kwargs == expected_data
            return response

    return wrapper


@pytest.fixture
def mock_external_startrek(mockserver):
    def _wrapper(response: dict):
        @mockserver.json_handler('/external_startrek/v2/issues')
        async def _handler(_request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_upload_data(mockserver):
    @mockserver.handler(
        r'/salesforce/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)/batches',
        regex=True,
    )
    async def _handler(request, job_id):
        return web.Response(status=201)

    return _handler


@pytest.fixture
def mock_salesforce_create_bulk_job(mock_salesforce):
    def _wrapper(response: dict):
        @mock_salesforce('/services/data/v52.0/jobs/ingest')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_close_bulk_job(mock_salesforce):
    @mock_salesforce(
        r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)', regex=True,
    )
    async def _handler(request, job_id):
        return {}

    return _handler


@pytest.fixture
def mock_stq_queue(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _wrapper(request, queue_name):
        return {}

    return _wrapper
