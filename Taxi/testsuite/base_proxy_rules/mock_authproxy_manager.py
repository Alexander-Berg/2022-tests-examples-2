import pytest


_ROUTING_RULES_MARKER = 'routing_rules'
# Usage: @pytest.mark.routing_rules([rule1, rule2, ...])


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_ROUTING_RULES_MARKER}: authproxy-manager routing rules',
    )


@pytest.fixture(scope='function', name='routing_rules')
def _routing_rules(load_json, request, object_substitute):
    class Wrapper:
        def __init__(self):
            marker = request.node.get_closest_marker(_ROUTING_RULES_MARKER)
            if marker is None:
                self.rules = load_json('routing-rules.json')
            else:
                self.rules = object_substitute(marker.args[0])

        def set_rules(self, rules):
            self.rules = object_substitute(rules)

        def get_rules(self):
            return self.rules

    return Wrapper()


@pytest.fixture(scope='function')
def mock_authproxy_manager(am_proxy_name, mockserver, routing_rules):
    @mockserver.json_handler('/authproxy-manager/v1/rules')
    async def _mock_v1_rules(request):
        assert request.query.get('proxy') == am_proxy_name
        return {'rules': routing_rules.get_rules()}

    return _mock_v1_rules
