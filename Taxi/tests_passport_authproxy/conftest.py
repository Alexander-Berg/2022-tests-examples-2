# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
import pytest

from passport_authproxy_plugins import *  # noqa: F403 F401
from tests_passport_authproxy import utils  # noqa: I201

DEFAULT_REQUEST_BODY = {'foo': 'tasty'}
DEFAULT_REMOTE_RESPONSE = {'bar': 'snaky'}


@pytest.fixture(name='perform_request')
async def _perform_request(taxi_passport_authproxy):
    async def _func(
            url_path,
            request_body=None,
            headers=None,
            token=None,
            method='POST',
    ):
        if request_body is None:
            request_body = DEFAULT_REQUEST_BODY

        if headers is None:
            headers = {}
        headers.update(
            {
                'X-Real-IP': utils.REAL_IP,
                'Origin': 'localhost',
                'User-Agent': utils.USER_AGENT,
                'Accept-Language': utils.ACCEPT_LANGUAGE,
            },
        )

        if token:
            extra = {'bearer': token}
        else:
            extra = {}

        if url_path.startswith('/'):
            url_path = url_path[1:]

        if method == 'POST':
            response = await taxi_passport_authproxy.post(
                url_path, json=request_body, headers=headers, **extra,
            )
        elif method == 'GET':
            response = await taxi_passport_authproxy.get(
                url_path, headers=headers, **extra,
            )
        else:
            raise ValueError('unsupported method')

        return response

    return _func


@pytest.fixture(name='mock_remote')
def _mock_remote(mockserver):
    def _func(url_path: str, response_code=200, response_body=None):
        if response_body is None:
            response_body = DEFAULT_REMOTE_RESPONSE

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        @mockserver.json_handler(url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == DEFAULT_REQUEST_BODY

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _func


@pytest.fixture(name='do_test_ok')
def _do_test_ok(perform_request, mock_remote):
    async def _perform(
            url_path: str,
            headers: dict = None,
            method: str = 'POST',
            token=None,
    ):
        handler = mock_remote(url_path)
        response = await perform_request(
            url_path=url_path, headers=headers, method=method, token=token,
        )

        assert handler.has_calls
        remote_request = handler.next_call()['request']

        assert response.status_code == 200
        assert response.json() == DEFAULT_REMOTE_RESPONSE
        assert not response.cookies

        return remote_request

    return _perform


@pytest.fixture(name='do_test_fail')
def _do_test_fail(perform_request, mock_remote):
    async def _perform(
            url_path: str,
            headers: dict = None,
            method: str = 'POST',
            token=None,
            expected_code: int = 401,
    ):
        handler = mock_remote(url_path)
        response = await perform_request(
            url_path=url_path, headers=headers, method=method, token=token,
        )

        assert not handler.has_calls
        assert response.status_code == expected_code
        assert not response.cookies

        return response.json()

    return _perform
