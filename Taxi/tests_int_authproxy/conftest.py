# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import os

import aiohttp.web
import pytest

from int_authproxy_plugins import *  # noqa: F403 F401

REMOTE_RESPONSE = {'sentinel': True}
URL_PATH = 'test/123'


@pytest.fixture
def mock_remote(mockserver):
    def _wrapper(url_path=URL_PATH, response_code=200, response_body=None):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper


@pytest.fixture
async def request_post(taxi_int_authproxy):
    async def _wrapper(
            url_path=URL_PATH,
            request_body=None,
            headers=None,
            params=None,
            token=None,
            method='post',
    ):
        if request_body is None:
            request_body = ''
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['origin'] = 'localhost'

        if not params:
            params = {}

        if method == 'post':
            response = await taxi_int_authproxy.post(
                url_path, json=request_body, headers=headers, params=params,
            )
        elif method == 'get':
            response = await taxi_int_authproxy.get(
                url_path, headers=headers, params=params,
            )
        else:
            assert False
        return response

    return _wrapper


# ya tool tvmknife unittest service -s 404 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIlAMQqRI:Ta6H2YvxBztdoylkA5V9jOsk_ZoEfPw8MEr1N'
    'et0nrw84sTLgkL3iw6Db4qL7-GifB4Pm06RAoQAseBmmCTdHmYjd0Vk-py6lFR6iQK9QprtN'
    '3Z5_k4fDQ-JLEY9cI6L5qGs2Dcsprt8zTXjmCQPY5CdQnWPOSuU6iu9AqHYWPY'
)


@pytest.fixture
async def service_ticket():
    return MOCK_SERVICE_TICKET


@pytest.fixture
def auth_headers():
    return {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


@pytest.fixture
def am_proxy_name():
    return 'int-authproxy'


# run all tests in old config-based rules mode and in am-base rules mode
@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param('legacy', marks=[]),
        pytest.param(
            'am', marks=[pytest.mark.config(INT_AUTHPROXY_MANAGER=True)],
        ),
    ],
)
def routing_mode():
    pass


@pytest.fixture()
def collected_rules_filename():
    return os.path.join(
        os.path.dirname(__file__), 'static', 'collected-rules.json',
    )
