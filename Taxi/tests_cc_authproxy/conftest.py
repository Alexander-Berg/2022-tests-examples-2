# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
import pytest

from cc_authproxy_plugins import *  # noqa: F403 F401

DEFAULT_URL = '/cc/test'
DEFAULT_RESPONSE = {'x': 'gg'}
DEFAULT_REQUEST = '"123"'


@pytest.fixture(name='default_url')
def _default_url():
    return DEFAULT_URL


@pytest.fixture(name='default_response')
def _default_response():
    return DEFAULT_RESPONSE


@pytest.fixture(name='cc_request')
async def _request(taxi_cc_authproxy):
    async def _wrapper(
            url_path=DEFAULT_URL, request_body=None, token=None, headers=None,
    ):
        if request_body is None:
            request_body = DEFAULT_REQUEST
        basic_headers = {'X-Real-IP': '1.2.3.4', 'Origin': 'localhost'}
        if headers:
            basic_headers.update(headers)
        if not basic_headers['Origin']:
            del basic_headers['Origin']
        if token:
            extra = {'bearer': token}
        else:
            extra = {}
        response = await taxi_cc_authproxy.post(
            url_path, json=request_body, headers=basic_headers, **extra,
        )
        return response

    return _wrapper


@pytest.fixture(name='mock_remote')
def _mock_remote(mockserver):
    def _wrapper(url_path=DEFAULT_URL, response_code=200, response_body=None):
        if response_body is None:
            response_body = DEFAULT_RESPONSE

        @mockserver.json_handler('%s' % url_path)
        def handler(request):
            return aiohttp.web.json_response(
                status=response_code,
                data=response_body,
                headers={'X-YaRequestId': '122333'},
            )

        return handler

    return _wrapper


@pytest.fixture
async def request_post(taxi_cc_authproxy):
    async def _wrapper(
            url_path=DEFAULT_URL,
            request_body=None,
            headers=None,
            token=None,
            method='post',
    ):
        if request_body is None:
            request_body = DEFAULT_REQUEST
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['origin'] = 'localhost'

        if token:
            extra = {'bearer': token}
        else:
            extra = {}

        if method == 'post':
            response = await taxi_cc_authproxy.post(
                url_path, json=request_body, headers=headers, **extra,
            )
        elif method == 'get':
            response = await taxi_cc_authproxy.get(
                url_path, headers=headers, **extra,
            )
        else:
            assert False
        return response

    return _wrapper


@pytest.fixture(name='mock_audit')
def _mock_audit(mockserver):
    def _wrapper(status=200, new_id='new_id'):
        @mockserver.json_handler('/audit/v1/robot/logs', prefix=True)
        def _audit_logs(request):
            return mockserver.make_response(status=status, json={'id': new_id})

        return _audit_logs

    return _wrapper
