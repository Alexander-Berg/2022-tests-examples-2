import pytest

import utils


AM_ROUTE_RULES = [
    utils.make_rule(
        {
            'input': {
                'prefix': '/smth',
                'priority': 300,
                'rule_name': '/smth',
            },
            'output': {'tvm_service': 'passport'},
            'proxy': {'proxy_401': True},
        },
    ),
]


@pytest.mark.parametrize('host', (None, 'invalid'))
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_set_x_forwarded_host(
        taxi_passenger_authorizer, blackbox_service, mockserver, host,
):
    @mockserver.json_handler('/smth')
    def _test(request):
        assert request.headers['X-Forwarded-Host'] == 'localhost:1180'
        return {'id': '123'}

    headers = {'X-Real-IP': '1.2.3.4', 'X-Remote-Ip': 'remote'}
    if host:
        headers['X-Forwarded-Host'] = 'invalid'
    response = await taxi_passenger_authorizer.post(
        'smth', bearer='test_token', headers=headers,
    )

    assert response.status == 200
    assert _test.times_called == 1
