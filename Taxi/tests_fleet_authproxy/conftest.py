# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
from fleet_authproxy_plugins import *  # noqa: F403 F401
import pytest


REQUEST_BODY = {'request': 'what'}
REMOTE_RESPONSE = {'response': 42}


@pytest.fixture
async def _request(taxi_fleet_authproxy):
    async def _wrapper(
            url_path, request_body=None, headers=None, method='POST',
    ):
        if request_body is None:
            request_body = REQUEST_BODY
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['Origin'] = 'localhost'
        elif headers['Origin'] is None:
            del headers['Origin']

        if method == 'POST':
            response = await taxi_fleet_authproxy.post(
                url_path, json=request_body, headers=headers,
            )
        elif method == 'GET':
            response = await taxi_fleet_authproxy.get(
                url_path, params=request_body, headers=headers,
            )
        else:
            raise Exception('Undefined method in fixture_request')
        return response

    return _wrapper


@pytest.fixture
def _mock_remote(mockserver):
    def _wrapper(
            url_path, response_code=200, response_body=None, method='POST',
    ):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            if method == 'POST':
                assert request.json == REQUEST_BODY
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper
