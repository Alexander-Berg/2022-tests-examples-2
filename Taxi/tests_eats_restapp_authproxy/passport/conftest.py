# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest


DEFAULT_URL = 'auth'


@pytest.fixture(name='mock_remote')
def _mock_remote(mockserver):
    def do_mock_remote(url=DEFAULT_URL, response_code=200):
        @mockserver.json_handler('%s' % url)
        def handler(request):
            return mockserver.make_response(status=response_code)

        return handler

    return do_mock_remote


@pytest.fixture(name='request_proxy')
def _request_proxy(taxi_eats_restapp_authproxy):
    async def do_request_proxy(url=DEFAULT_URL, token=None, headers=None):
        await taxi_eats_restapp_authproxy.invalidate_caches()

        basic_headers = {'X-Real-IP': '1.2.3.4', 'Origin': 'localhost'}
        if headers:
            basic_headers.update(headers)
        if not basic_headers['Origin']:
            del basic_headers['Origin']

        extra = {'headers': basic_headers}
        if token:
            extra['bearer'] = token

        return await taxi_eats_restapp_authproxy.post(
            url, data=json.dumps({}), **extra,
        )

    return do_request_proxy
