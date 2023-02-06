import pytest


@pytest.fixture(name='bsx')
def mock_bsx(mockserver):
    class Context:
        def __init__(self):
            self.matched_rules = []
            self.mock_v2_rules_match = None

        def add_match_rule(self, matched_rule):
            self.matched_rules.append(matched_rule)

    context = Context()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    def _mock_v2_rules_match(request):
        matches = []
        for matched_rule in context.matched_rules:
            rule_type = matched_rule['type']
            if rule_type in request.json['rule_types']:
                matches.append(matched_rule)
        return {'matches': matches}

    context.mock_v2_rules_match = _mock_v2_rules_match

    return context
