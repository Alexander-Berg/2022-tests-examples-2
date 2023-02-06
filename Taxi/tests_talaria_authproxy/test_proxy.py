import pytest


ALLOWED_IP = '192.168.1.1'
NOT_ALLOWED_IP = '192.168.1.2'

ALLOWED_API_KEY = 'talaria_api_key'
NOT_ALLOWED_API_KEY = 'bad_api_key'

ROUTING_RULES = [
    {
        'input': {
            'http-path-prefix': '/talaria/check-ip-and-api-key',
            'ip-whitelist': [ALLOWED_IP],
            'api-key-authorization-enabled': True,
        },
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'mock',
            'attempts': 2,
        },
        'proxy': {'server-hosts': ['*'], 'proxy-401': False},
    },
    {
        'input': {
            'http-path-prefix': '/talaria/check-ip',
            'ip-whitelist': [ALLOWED_IP],
            'api-key-authorization-enabled': False,
        },
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'mock',
            'attempts': 2,
        },
        'proxy': {'server-hosts': ['*'], 'proxy-401': False},
    },
    {
        'input': {
            'http-path-prefix': '/talaria/no-auth',
            'ip-whitelist': [ALLOWED_IP],
            'api-key-authorization-enabled': True,
        },
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'mock',
            'attempts': 2,
        },
        'proxy': {'server-hosts': ['*'], 'proxy-401': True},
    },
]


@pytest.fixture(name='make_talaria_mock')
def make_talaria_mock_fixture(mockserver):
    def _make_talaria_mock(url, response_status=200):
        @mockserver.handler(url)
        def _mock(request):
            headers = request.headers
            assert 'X-Api-Key' not in headers
            assert headers['X-Some-Header'] == 'some-header-data'
            assert request.json == {'body_param': 'body_param_value'}
            assert request.args == {'query_param': 'query_param_value'}
            return mockserver.make_response(
                status=response_status,
                json={'response_param': 'response_param_value'},
            )

        return _mock

    return _make_talaria_mock


@pytest.fixture(name='make_request')
def make_request_fixture(taxi_talaria_authproxy):
    async def _make_request(url, x_api_key=None, real_ip=ALLOWED_IP):
        headers = {'X-Some-Header': 'some-header-data', 'X-Real-IP': real_ip}
        if x_api_key:
            headers['X-Api-Key'] = x_api_key
        params = {'query_param': 'query_param_value'}
        body = {'body_param': 'body_param_value'}
        response = await taxi_talaria_authproxy.post(
            url, params=params, json=body, headers=headers,
        )
        return response

    return _make_request


@pytest.mark.parametrize('response_status', [200, 400, 500])
@pytest.mark.parametrize(
    ['url', 'real_ip', 'x_api_key'],
    [
        (
            '/talaria/check-ip-and-api-key/endpoint',
            ALLOWED_IP,
            ALLOWED_API_KEY,
        ),
        ('/talaria/no-auth/endpoint', NOT_ALLOWED_IP, NOT_ALLOWED_API_KEY),
    ],
)
@pytest.mark.config(TALARIA_AUTHPROXY_ROUTING_RULES=ROUTING_RULES)
async def test_proxy(
        make_talaria_mock,
        make_request,
        response_status,
        url,
        real_ip,
        x_api_key,
):
    mock = make_talaria_mock(url=url, response_status=response_status)
    response = await make_request(
        url=url, real_ip=real_ip, x_api_key=x_api_key,
    )
    assert response.status == response_status
    assert response.json() == {'response_param': 'response_param_value'}

    if response_status == 500:
        assert mock.times_called == 2
    else:
        assert mock.times_called == 1


@pytest.mark.parametrize(
    ['url', 'real_ip', 'x_api_key', 'expected_status'],
    [
        (
            '/talaria/check-ip-and-api-key/endpoint',
            ALLOWED_IP,
            NOT_ALLOWED_API_KEY,
            401,
        ),
        ('/talaria/check-ip-and-api-key/endpoint', ALLOWED_IP, None, 401),
        ('/talaria/check-ip/endpoint', NOT_ALLOWED_IP, ALLOWED_API_KEY, 401),
        ('/talaria/undefined-rule/endpoint', ALLOWED_IP, ALLOWED_API_KEY, 404),
    ],
)
@pytest.mark.config(TALARIA_AUTHPROXY_ROUTING_RULES=ROUTING_RULES)
async def test_no_proxy(
        make_talaria_mock,
        make_request,
        url,
        real_ip,
        x_api_key,
        expected_status,
):
    mock = make_talaria_mock(url=url)
    response = await make_request(
        url=url, real_ip=real_ip, x_api_key=x_api_key,
    )
    assert response.status == expected_status
    assert mock.times_called == 0
