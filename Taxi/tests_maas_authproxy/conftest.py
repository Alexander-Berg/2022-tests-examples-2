# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from maas_authproxy_plugins import *  # noqa: F403 F401


URL = '/v1/payment/status'
API_KEY_HASH = (
    '8c284055dbb54b7f053a2dc612c3727c7aa36354361055f2110f4903ea8ee29c'
)


def _check_uapi_keys_request(request):
    headers = request.headers
    assert headers['X-API-Key'] == API_KEY_HASH
    assert request.json['consumer_id'] == 'maas-authproxy'
    assert request.json['client_id'] == 'vtb'
    assert request.json['entity_id'] == ''
    assert request.json['permission_ids'] == [URL + ':POST']


@pytest.fixture
def uapi_keys_fail(mockserver):
    def _setup_uapi_keys(response_status):
        @mockserver.handler('/uapi-keys/v2/authorization')
        def _mock(request):
            _check_uapi_keys_request(request)

            if response_status == 403:
                body = {
                    'code': 'unauthorized',
                    'message': 'Authorization failed',
                }
            else:
                body = {
                    'code': 'internal_server_error',
                    'message': 'Internal server error',
                }
            return mockserver.make_response(status=response_status, json=body)

        return _mock

    return _setup_uapi_keys


@pytest.fixture
def uapi_keys_ok(mockserver):
    @mockserver.handler('/uapi-keys/v2/authorization')
    def _mock(request):
        _check_uapi_keys_request(request)

        return mockserver.make_response(json={'key_id': 'some_key_id'})

    return _mock


def _check_maas_request(request):
    headers = request.headers
    assert 'X-Api-Key' not in headers
    assert headers['X-Some-Header'] == 'some-header-data'
    assert request.json == {'status': 'success'}
    assert request.args['param1'] == 'data'


@pytest.fixture
def maas(mockserver):
    def _setup_maas(response_status=200):
        @mockserver.handler(URL)
        def _mock(request):
            _check_maas_request(request)

            if response_status == 200:
                return mockserver.make_response(json={})
            body = {'code': 'some_maas_problem'}
            return mockserver.make_response(status=response_status, json=body)

        return _mock

    return _setup_maas


@pytest.fixture
def maas_ok(mockserver):
    @mockserver.handler(URL)
    def _mock(request):
        _check_maas_request(request)

        return mockserver.make_response(json={})

    return _mock


@pytest.fixture
async def metrics_checker(taxi_maas_authproxy_monitor):
    class MetricsChecker:
        def __init__(self, approves, rejects):
            self.init_approves = approves
            self.init_rejects = rejects

        async def check_metrics(self, expected_approves=0, expected_rejects=0):
            statistics = await taxi_maas_authproxy_monitor.get_metric('auth')
            approves = statistics['apikey-ok'] - self.init_approves
            rejects = statistics['apikey-fail'] - self.init_rejects
            assert approves == expected_approves
            assert rejects == expected_rejects

    statistics = await taxi_maas_authproxy_monitor.get_metric('auth')
    init_approves = statistics['apikey-ok']
    init_rejects = statistics['apikey-fail']

    return MetricsChecker(init_approves, init_rejects)


@pytest.fixture
def make_request(taxi_maas_authproxy):
    async def _make_request(url=URL, x_api_key=None, has_auth_header=True):
        headers = {
            'X-Some-Header': 'some-header-data',
            'X-Real-IP': '192.68.0.5',
        }
        if has_auth_header:
            if x_api_key is None:
                x_api_key = 'vtb:api-key'
            headers['X-Api-Key'] = x_api_key
        params = {'param1': 'data'}
        body = {'status': 'success'}
        response = await taxi_maas_authproxy.post(
            url, params=params, json=body, headers=headers,
        )
        return response

    return _make_request
