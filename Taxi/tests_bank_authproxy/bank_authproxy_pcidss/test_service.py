import pytest

CONFIG = [
    {
        'input': {'http-path-prefix': '/unauth'},
        'output': {'upstream': {'$mockserver': ''}},
        'proxy': {'proxy-401': True, 'server-hosts': ['*']},
    },
]


async def test_do_smth_unauthorized(taxi_bank_authproxy_pcidss, mock_remote):
    backend = mock_remote('/do-smth')
    response = await taxi_bank_authproxy_pcidss.get('/do-smth')
    assert not backend.has_calls
    assert response.status_code == 401


async def test_pcidss_unauthorized(taxi_bank_authproxy_pcidss, mock_remote):
    backend = mock_remote('/pcidss-unauth')
    response = await taxi_bank_authproxy_pcidss.get('/pcidss-unauth')
    assert backend.has_calls
    assert response.status_code == 200


async def test_no_route(taxi_bank_authproxy_pcidss):
    response = await taxi_bank_authproxy_pcidss.get('/no-route')
    assert response.status_code == 404


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_uconfig_ignored(taxi_bank_authproxy_pcidss, mock_remote):
    backend = mock_remote('/unauth')
    response = await taxi_bank_authproxy_pcidss.get('/unauth')
    assert not backend.has_calls
    assert response.status_code == 404


def disable_pcidss_rules(config, config_vars):
    config['components_manager']['components']['handler-router'][
        'is_in_pcidss_scope'
    ] = False


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.uservice_oneshot(config_hooks=[disable_pcidss_rules])
async def test_disabled_pcidss(taxi_bank_authproxy_pcidss, mock_remote):
    backend = mock_remote('/unauth')
    response = await taxi_bank_authproxy_pcidss.get('/unauth')
    assert backend.has_calls
    assert response.status_code == 200
