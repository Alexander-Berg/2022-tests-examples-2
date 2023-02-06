import pytest


@pytest.mark.config(
    AUTHPROXY_MANAGER_FW_MACRO_BY_PROXY_NAME={
        'passenger-authorizer': '_TAXI_',
    },
)
@pytest.mark.parametrize(
    'url,hostname,port',
    [
        ('zalogin.taxi.yandex.net', 'zalogin.taxi.yandex.net', 80),
        ('http://zalogin.taxi.yandex.net', 'zalogin.taxi.yandex.net', 80),
        ('ftp://zalogin.taxi.yandex.net', 'zalogin.taxi.yandex.net', 80),
        ('https://zalogin.taxi.yandex.ru', 'zalogin.taxi.yandex.ru', 443),
    ],
)
async def test_smoke(taxi_authproxy_manager, mockserver, url, hostname, port):
    @mockserver.json_handler('/clowny-perforator/v1/firewall/check')
    def mock(request):
        assert request.query == {}
        assert request.json == {
            'from': {'firewall-macro': '_TAXI_'},
            'to': {'l7-balancer-hostname': hostname},
            'port': port,
        }

        return {'rule-exists': False}

    response = await taxi_authproxy_manager.post(
        '/v1/hints/firewall-check',
        params={'proxy': 'passenger-authorizer', 'upstream-url': url},
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json() == {
        'rule-exists': False,
        'create-rule-url': (
            'https://puncher.yandex-team.ru/?create_sources=_TAXI_'
            f'&create_protocol=tcp&create_ports={port}&'
            f'create_destinations={hostname}'
        ),
    }
    assert mock.times_called == 1


@pytest.mark.config(
    AUTHPROXY_MANAGER_FW_MACRO_BY_PROXY_NAME={
        'passenger-authorizer': '_TAXI_',
    },
)
@pytest.mark.parametrize('exists', [True, False])
async def test_puncher_responses(taxi_authproxy_manager, mockserver, exists):
    @mockserver.json_handler('/clowny-perforator/v1/firewall/check')
    def mock(request):
        assert request.query == {}
        assert request.json == {
            'from': {'firewall-macro': '_TAXI_'},
            'to': {'l7-balancer-hostname': 'zalogin.taxi.yandex.net'},
            'port': 80,
        }
        return {'rule-exists': exists}

    response = await taxi_authproxy_manager.post(
        '/v1/hints/firewall-check',
        params={
            'proxy': 'passenger-authorizer',
            'upstream-url': 'zalogin.taxi.yandex.net',
        },
        headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    assert response.json()['rule-exists'] == exists
    assert mock.times_called == 1


async def test_proxy_not_found(taxi_authproxy_manager):
    response = await taxi_authproxy_manager.post(
        '/v1/hints/firewall-check',
        params={
            'proxy': 'passenger-authorizer',
            'upstream-url': 'zalogin.taxi.yandex.net',
        },
        headers={'content-type': 'application/json'},
    )
    assert response.status == 500
