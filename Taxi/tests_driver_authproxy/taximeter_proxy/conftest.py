# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
import pytest
from taximeter_proxy_plugins import *  # noqa: F403 F401


URL_PATH = 'driver/v1/auth/smth'
COOKIE_URL_PATH = 'driver/v1/cookie/smth'
UNAUTHORIZED_URL_PATH = 'driver/v1/noauth/smth'
REQUEST_BODY = {'x': 'y'}
REMOTE_RESPONSE = {'sentinel': True}


@pytest.fixture
async def request_post(taxi_taximeter_proxy):
    async def _wrapper(
            url_path=URL_PATH, request_body=None, headers=None, params=None,
    ):
        if request_body is None:
            request_body = REQUEST_BODY
        if headers is None:
            headers = {'User-Agent': 'Taximeter 9.13 (1882)'}
        response = await taxi_taximeter_proxy.post(
            url_path, json=request_body, headers=headers, params=params,
        )
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
            ya_uid=False,
    ):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            assert request.json == REQUEST_BODY

            assert 'X-Request-Application' in request.headers

            assert ('X-YaTaxi-Park-Id' in request.headers) is authorized
            assert (
                'X-YaTaxi-Driver-Profile-Id' in request.headers
            ) is authorized

            assert (
                'X-Request-Application-Version' in request.headers
            ) is taximeter
            assert ('X-Request-Version-Type' in request.headers) is taximeter
            assert ('X-Request-Platform' in request.headers) is taximeter
            assert (
                'X-Request-Application-Brand' in request.headers
            ) is taximeter

            assert ('X-Yandex-UID' in request.headers) is ya_uid

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper
