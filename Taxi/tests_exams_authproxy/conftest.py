# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import aiohttp.web
import pytest

from exams_authproxy_plugins import *  # noqa: F403 F401

DEFAULT_REQUEST_BODY = {'request': True}
DEFAULT_RESPONSE_BODY = {'response': True}
ROUTE_VALIDATE_TOKEN = '/exams-training-platform/web_api/auth/validate_token'
EXAMS_TRAINING_RESPONSE = 'exams_training_response.json'
EXAMS_TRAINING_HEADERS = {
    'access-token',
    'client',
    'expiry',
    'uid',
    'token-type',
    'X-Forwarded-Host',
}


@pytest.fixture
def am_proxy_name():
    return 'exams-authproxy'


@pytest.fixture
def _mock_exams_training(mockserver, load_json):
    def _wrapper(response_code):
        @mockserver.json_handler(ROUTE_VALIDATE_TOKEN)
        async def _check_auth(request, **kwargs):
            for key in EXAMS_TRAINING_HEADERS:
                assert request.headers[key], f'Missing key [{key}] in request'
            body = None
            if response_code == 200:
                body = load_json(EXAMS_TRAINING_RESPONSE)
            return aiohttp.web.json_response(status=response_code, data=body)

        return _check_auth

    return _wrapper


@pytest.fixture
def _mock_remote(mockserver):
    def _wrapper(
            url_path,
            request_body=None,
            response_code=200,
            response_body=None,
            exclude_headers=None,
            existing_headers=None,
    ):
        if not request_body:
            request_body = DEFAULT_REQUEST_BODY
        if not response_body:
            response_body = DEFAULT_RESPONSE_BODY

        @mockserver.json_handler('%s' % url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == request_body

            if exclude_headers:
                assert not set(exclude_headers).intersection(
                    set(request.headers),
                )
            if existing_headers:
                for key, value in existing_headers.items():
                    assert request.headers[key] == value
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper


@pytest.fixture
async def _request_exams_authproxy(taxi_exams_authproxy):
    async def _wrapper(
            url_path, headers=None, request_body=None, method='post',
    ):
        if not request_body:
            request_body = DEFAULT_REQUEST_BODY
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['origin'] = 'localhost'
        if method == 'post':
            response = await taxi_exams_authproxy.post(
                url_path, json=request_body, headers=headers,
            )
        elif method == 'get':
            response = await taxi_exams_authproxy.get(
                url_path, headers=headers,
            )
        else:
            assert False
        return response

    return _wrapper


def _check_uapi_keys_request(request):
    headers = request.headers
    assert headers['X-API-Key']
    assert request.json['consumer_id'] == 'exams-authproxy'
    assert request.json['entity_id'] == ''
    assert request.json['permission_ids']


@pytest.fixture
def _uapi_keys(mockserver):
    def _wrapper(response_code):
        @mockserver.handler('/uapi-keys/v2/authorization')
        def _mock(request):
            if response_code == 403:
                body = {
                    'code': 'unauthorized',
                    'message': 'Authorization failed',
                }
            elif response_code == 500:
                body = {
                    'code': 'internal_server_error',
                    'message': 'Internal server error',
                }
            else:
                _check_uapi_keys_request(request)
                body = {'key_id': 'some_key_id'}
            return mockserver.make_response(status=response_code, json=body)

        return _mock

    return _wrapper
