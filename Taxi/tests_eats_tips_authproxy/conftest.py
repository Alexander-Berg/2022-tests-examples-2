# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp
import pytest

from eats_tips_authproxy_plugins import *  # noqa: F403 F401

REQUEST_BODY: dict = {}
REMOTE_RESPONSE = {'sentinel': True}
URL_PATH = '1.0/test/123'


@pytest.fixture
def mock_remote(mockserver):
    def _wrapper(url_path=URL_PATH, response_code=200, response_body=None):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == REQUEST_BODY

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper
