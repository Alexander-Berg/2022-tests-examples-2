# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_authproxy_pcidss_plugins import *  # noqa: F403 F401

import aiohttp
import pytest


@pytest.fixture
def mock_remote(mockserver):
    def _func(
            url_path, request_body=None, response_code=200, response_body=None,
    ):
        if response_body is None:
            response_body = {}

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        @mockserver.json_handler(url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == request_body

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _func
