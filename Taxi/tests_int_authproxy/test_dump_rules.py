import pytest

import utils


@pytest.mark.routing_rules(utils.AM_RULES_SIMPLE)
@pytest.mark.config(
    TVM_ENABLED=False, INT_AUTHPROXY_ROUTE_RULES=utils.RULES_SIMPLE,
)
async def test_dump_rules(
        taxi_int_authproxy, taxi_int_authproxy_monitor, taxi_config,
):
    # dump-rules is not accessible from outside
    response = await taxi_int_authproxy.get('service/dump-rules')
    assert response.status_code == 404

    expected_rules = taxi_config.get('INT_AUTHPROXY_ROUTE_RULES')

    # dump-rules is accessible from localhost
    response = await taxi_int_authproxy_monitor.get('service/dump-rules')
    assert response.status_code == 200
    assert response.json() == expected_rules
