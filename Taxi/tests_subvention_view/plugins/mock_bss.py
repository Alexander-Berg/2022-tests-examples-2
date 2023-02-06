import pytest


class BillingSubventionsContext:
    def __init__(self):
        self.active_rules = []
        self.calls = 0
        self.rules_select_call_params = []
        self.by_driver_call_params = []
        self.by_driver_subventions = []
        self.by_driver_calls = 0
        self.rules_select_limit = -1
        self.rules_select_i = 0

        self.rules_select = None
        self.by_driver = None

    def add_rule(self, rule):
        self.active_rules.append(rule)

    def add_rules(self, rules):
        self.active_rules.extend(rules)

    def clean_rules(self):
        self.active_rules = []

    def add_by_driver_subvention(self, subv):
        self.by_driver_subventions.append(subv)

    def add_by_driver_subventions(self, subv):
        self.by_driver_subventions.extend(subv)

    def clean_by_driver_subvention(self):
        self.by_driver_subventions = []

    def set_rules_select_limit(self, limit):
        self.rules_select_limit = limit


@pytest.fixture(autouse=True)
def bss(mockserver):
    bss_context = BillingSubventionsContext()

    def _match_personal(rule, request):
        field = 'is_personal'
        if field in rule and field in request:
            return rule[field] == request[field]
        return True

    def _is_match(rule, request):
        return _match_personal(rule, request)

    def _rules_filtered(rules, request):
        return [rule for rule in rules if _is_match(rule, request)]

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        bss_context.calls += 1
        bss_context.rules_select_call_params.append(request.get_data())
        rules = _rules_filtered(bss_context.active_rules, request.json)
        if bss_context.rules_select_limit == -1:
            bss_context.rules_select_i = 0
            return {'subventions': rules}

        if bss_context.rules_select_i == -1:
            bss_context.rules_select_i = 0
            return {'subventions': []}
        left_end = bss_context.rules_select_i
        if (
                bss_context.rules_select_i + bss_context.rules_select_limit
                >= len(rules)
        ):
            right_end = len(rules)
            bss_context.rules_select_i = -1
        else:
            right_end = (
                bss_context.rules_select_i + bss_context.rules_select_limit
            )
            bss_context.rules_select_i = right_end
        return {'subventions': rules[left_end:right_end]}

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    def _get_by_driver(request):
        bss_context.by_driver_calls += 1
        bss_context.by_driver_call_params.append(request.get_data())
        print('subventions_data: {}'.format(bss_context.by_driver_subventions))
        return {'subventions': bss_context.by_driver_subventions}

    bss_context.rules_select = _mock_rules_select
    bss_context.by_driver = _get_by_driver
    return bss_context
