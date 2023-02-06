"""
Mocks for driver-work-rules.
"""
import pytest

V1_WORK_RULES_LIST = '/driver-work-rules/v1/work-rules/list'
V1_WORK_RULES_GET = '/driver-work-rules/v1/work-rules'


class DriverWorkRulesContext:
    def __init__(self):
        self.calls = {}

    def add_calls(self, handler):
        self.calls[handler] = self.calls.get(handler, 0) + 1

    def has_calls(self, handler=None):
        times_called = 0
        if handler is None:
            times_called = sum(self.calls.values())
        else:
            times_called = self.calls.get(handler, 0)
        return times_called > 0


@pytest.fixture
def driver_work_rules(mockserver, load_json):
    context = DriverWorkRulesContext()

    @mockserver.json_handler(V1_WORK_RULES_LIST)
    def _mock_work_rules_list(request):
        context.add_calls(V1_WORK_RULES_LIST)

        work_rules = load_json('driver_work_rules.json')['work_rules']
        work_rule_ids = request.json['query']['park']['work_rule'].get(
            'ids', None,
        )
        if work_rule_ids is not None:
            return {
                'work_rules': [
                    work_rule
                    for work_rule in work_rules
                    if work_rule['id'] in work_rule_ids
                ],
            }

        return {'work_rules': work_rules}

    @mockserver.json_handler(V1_WORK_RULES_GET)
    def _mock_work_rules_get(request):
        context.add_calls(V1_WORK_RULES_GET)

        work_rules = load_json('driver_work_rules.json')['work_rules']
        for work_rule in work_rules:
            if work_rule['id'] == request.args['id']:
                return work_rule
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Work rule was not found'},
        )

    return context
