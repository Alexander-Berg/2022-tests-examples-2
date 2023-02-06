import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from corp_authproxy_plugins import *  # noqa: F403 F401


@pytest.fixture
def am_proxy_name():
    return 'corp-authproxy'


@pytest.fixture
def mock_remote(mockserver):
    def _func(
            url_path,
            request_body=None,
            response_code=200,
            response_body=None,
            request_headers=None,
    ):
        if response_body is None:
            response_body = {}

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        @mockserver.json_handler(url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == request_body
            if request_headers is not None:
                for header, header_value in request_headers.items():
                    assert request.headers[header] == header_value
            return mockserver.make_response(
                status=response_code, json=response_body,
            )

        return handler

    return _func
