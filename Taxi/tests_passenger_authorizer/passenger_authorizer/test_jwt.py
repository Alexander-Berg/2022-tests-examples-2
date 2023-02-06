import collections

import aiohttp
import pytest

PUSH_URL_PATH = 'api/v1/geolocation/push'
UNAUTHORIZED_URL_PATH = 'api/v1/geolocation/push/unauthorized'
REQUEST_BODY = {'sentinel': 'request'}
REMOTE_RESPONSE = {'sentinel': True}

VALID_DATE = '2020-04-19T00:00:00+0300'


@pytest.mark.now(VALID_DATE)
async def test_happy_path(_load_jwts, _mock_remote, _request):
    jwts = _load_jwts('user_id_string')
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert handler.has_calls
    assert handler.next_call()['request'].headers['X-YaEda-CourierId'] == '123'
    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE


@pytest.mark.now('2020-04-18T00:00:00+0300')
async def test_token_issued_in_future(_load_jwts, _mock_remote, _request):
    jwts = _load_jwts('user_id_string')
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert response.status_code == 401
    assert not handler.has_calls


@pytest.mark.now('2021-04-18T00:00:00+0300')
async def test_token_expired(_load_jwts, _mock_remote, _request):
    jwts = _load_jwts('user_id_string')
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert response.status_code == 401
    assert not handler.has_calls


@pytest.mark.now(VALID_DATE)
async def test_do_convert_int_to_str(_load_jwts, _mock_remote, _request):
    jwts = _load_jwts('user_id_integer')
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert handler.has_calls
    assert handler.next_call()['request'].headers['X-YaEda-CourierId'] == '13'
    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE


@pytest.mark.now(VALID_DATE)
@pytest.mark.parametrize(
    'jwts_key',
    [
        'user_id_invalid_type',
        'missing_exp',
        'missing_iat',
        'missing_user_id',
        'invalid_sign',
    ],
)
async def test_unauthorized_cases(
        jwts_key, _load_jwts, _mock_remote, _request,
):
    jwts = _load_jwts(jwts_key)
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert response.status_code == 401
    assert not handler.has_calls


@pytest.mark.now(VALID_DATE)
@pytest.mark.parametrize('jwts_key', ['missing_user_id', 'invalid_sign'])
async def test_proxy_401(jwts_key, _load_jwts, _mock_remote, _request):
    jwts = _load_jwts(jwts_key)
    handler = _mock_remote(url_path=UNAUTHORIZED_URL_PATH)

    response = await _request(url_path=UNAUTHORIZED_URL_PATH, token=jwts.token)

    # Invalid jwt doesn't prevent proxy with "proxy-401: true"
    assert response.status_code == 200
    assert handler.times_called == 1

    # But header is skipped
    request = handler.next_call()['request']
    assert 'X-YaEda-CourierId' not in request.headers


@pytest.mark.now(VALID_DATE)
@pytest.mark.parametrize(
    'header_name', ['X-API-TOKEN', 'x-api-token', 'x-API-token'],
)
async def test_skip_x_api_token_header(
        header_name, _load_jwts, _mock_remote, _request,
):
    jwts = _load_jwts('user_id_string')
    handler = _mock_remote()

    response = await _request(token=jwts.token)

    assert handler.has_calls
    request = handler.next_call()['request']
    assert header_name not in request.headers

    assert response.status_code == 200
    assert header_name not in response.headers


# JWT is generated using python, e.g.:
#
# import jwt
# jwt.encode({'id': '123'}, 'secret', algorithm='HS512')
@pytest.fixture
def _load_jwts(load_json):
    def _wrapper(key):
        static = load_json('hardcoded_jwt.json')
        kwargs = static[key]
        jwts_class = collections.namedtuple('Jwts', 'token payload secret')
        return jwts_class(**kwargs)

    return _wrapper


@pytest.fixture
async def _request(taxi_passenger_authorizer):
    async def _wrapper(url_path=PUSH_URL_PATH, request_body=None, token=None):
        if request_body is None:
            request_body = REQUEST_BODY
        headers = {}
        if token is not None:
            headers = {'X-API-TOKEN': token}
        response = await taxi_passenger_authorizer.post(
            url_path, json=request_body, headers=headers,
        )
        return response

    return _wrapper


@pytest.fixture
def _mock_remote(mockserver):
    def _wrapper(
            url_path=PUSH_URL_PATH, response_code=200, response_body=None,
    ):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper
