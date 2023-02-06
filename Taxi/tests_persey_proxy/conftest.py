# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
import pytest

from persey_proxy_plugins import *  # noqa: F403 F401

URL_PATH = 'persey/v1/auth/smth'
UNAUTHORIZED_URL_PATH = 'persey/v1/noauth/smth'
REQUEST_BODY = {'x': 'y'}
REMOTE_RESPONSE = {'sentinel': True}


@pytest.fixture
async def request_post(taxi_persey_proxy):
    async def _wrapper(
            url_path=URL_PATH,
            request_body=None,
            headers=None,
            token=None,
            method='post',
    ):
        if request_body is None:
            request_body = REQUEST_BODY
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['origin'] = 'localhost'

        if token:
            extra = {'bearer': token}
        else:
            extra = {}

        if method == 'post':
            response = await taxi_persey_proxy.post(
                url_path, json=request_body, headers=headers, **extra,
            )
        elif method == 'get':
            response = await taxi_persey_proxy.get(
                url_path, headers=headers, **extra,
            )
        else:
            assert False
        return response

    return _wrapper


@pytest.fixture
def mock_remote(mockserver):
    def _wrapper(
            url_path=URL_PATH,
            response_code=200,
            response_body=None,
            authorized=True,
            taximeter=True,
    ):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == REQUEST_BODY

            assert 'X-External-API-Key' not in request.headers

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper
