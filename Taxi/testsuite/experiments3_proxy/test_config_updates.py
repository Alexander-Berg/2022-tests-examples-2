import urllib.parse

import pytest


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
def test_unknown_consumer_nocheck(taxi_experiments3_proxy):
    """Proxy returns empty list of experiments for unknown consumer."""
    response = _request(taxi_experiments3_proxy)
    assert response.status_code == 200
    data = response.json()
    assert data == {'configs': []}


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=True)
def test_unknown_consumer(taxi_experiments3_proxy):
    """Proxy returns empty list if no configs are loaded."""
    response = _request(taxi_experiments3_proxy)
    assert response.status_code == 404
    data = response.json()
    assert data == {'error': {'text': 'consumer not found'}}


@pytest.mark.config(TVM_ENABLED=False, EXPERIMENTS3_PROXY_CHECK_CONSUMER=False)
def test_basic_happy_path(taxi_experiments3_proxy, mockserver, load_json):
    """Receiving of the existing config."""

    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def upstream(request):
        return load_json('good_config.json')

    taxi_experiments3_proxy.invalidate_caches()
    upstream.wait_call()

    response = _request(taxi_experiments3_proxy)
    assert response.status_code == 200
    data = response.json()
    assert len(data['configs']) == 1
    assert data['configs'][0]['name'] == 'ENABLED_CONFIG'
    assert data['configs'][0]['last_modified_at'] == 1
    assert data['configs'][0]['match']['enabled']


def _request(taxi_experiments3_proxy, newer_than=-1, limit=100):
    response = taxi_experiments3_proxy.get(
        _build_url(newer_than, limit, 'dummy'), headers={},
    )
    return response


def _build_url(newer_than=-1, limit=100, consumer='dummy'):
    params = {'newer_than': newer_than, 'limit': limit, 'consumer': consumer}
    return '/v1/configs/updates?%s' % urllib.parse.urlencode(params)
