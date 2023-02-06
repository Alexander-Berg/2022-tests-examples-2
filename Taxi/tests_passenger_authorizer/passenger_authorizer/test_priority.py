import pytest

import utils


AM_ROUTING_RULE = utils.make_rule(
    {
        'input': {'priority': 100},
        'proxy': {'proxy_401': True},
        'output': {'upstream': {'$mockserver': '/first'}},
    },
)

AM_ROUTING_RULE2 = utils.make_rule(
    {
        'input': {'priority': 101},
        'proxy': {'proxy_401': True},
        'output': {'upstream': {'$mockserver': '/second'}},
    },
)


@pytest.mark.parametrize(
    'rules',
    [[AM_ROUTING_RULE, AM_ROUTING_RULE2], [AM_ROUTING_RULE2, AM_ROUTING_RULE]],
)
async def test_priority_order(
        taxi_passenger_authorizer, mockserver, rules, routing_rules,
):
    routing_rules.set_rules(rules)

    @mockserver.json_handler('/first/4.0/proxy')
    def mock(request):
        return {}

    response = await taxi_passenger_authorizer.get('/4.0/proxy')
    assert response.status_code == 200

    assert mock.times_called == 1
