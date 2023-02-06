# pylint: disable=C0103
import pytest


ERROR_RESPONSE = {'code': 'error', 'message': 'error'}


@pytest.fixture(name='mock_driver_work_rules')
def _mock_driver_work_rules(mockserver):
    class Context:
        def __init__(self):
            self.rule_id = None
            self.returned_rule_id = None
            self.returned_rule_compatible_id = None
            self.park_id = None
            self.work_type = 'park'
            self.response_code = 200

        def set_data(
                self,
                rule_id=None,
                returned_rule_id=None,
                returned_rule_compatible_id=None,
                park_id=None,
                work_type=None,
                response_code=None,
        ):
            if rule_id is not None:
                self.rule_id = rule_id
            if returned_rule_id is not None:
                self.returned_rule_id = returned_rule_id
            if returned_rule_compatible_id is not None:
                self.returned_rule_compatible_id = returned_rule_compatible_id
            if park_id is not None:
                self.park_id = park_id
            if work_type is not None:
                self.work_type = work_type
            if response_code is not None:
                self.response_code = response_code

        def validate_get_rule_request(self, request):
            assert request.args['id'] == self.rule_id
            assert request.args['park_id'] == self.park_id

        def validate_rules_compatible_request(self, request):
            assert request.args['compatible_with_id'] == self.rule_id
            assert request.args['park_id'] == self.park_id
            assert request.args['client_type'] == 'external'

        def make_get_rule_response(self, rule_id):
            return {
                'id': rule_id,
                'commission_for_driver_fix_percent': '0.0',
                'commission_for_subvention_percent': '0.0',
                'commission_for_workshift_percent': '0.0',
                'is_commission_if_platform_commission_is_null_enabled': False,
                'is_commission_for_orders_cancelled_by_client_enabled': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': False,
                'is_enabled': False,
                'is_workshift_enabled': False,
                'name': 'test',
                'type': self.work_type,
            }

        def make_rules_compatible_response(self, rule_id):
            return {'work_rules': [self.make_get_rule_response(rule_id)]}

        @property
        def has_mock_get_rule_calls(self):
            return mock_get_rule.has_calls

        @property
        def has_mock_rules_compatible_calls(self):
            return mock_rules_compatible.has_calls

    context = Context()

    @mockserver.json_handler('/driver-work-rules/v1/work-rules')
    def mock_get_rule(request):
        assert request.method == 'GET'
        context.validate_get_rule_request(request)
        if context.response_code != 200:
            return mockserver.make_response(
                json=ERROR_RESPONSE, status=context.response_code,
            )
        rule_id = (
            context.rule_id
            if context.returned_rule_id is None
            else context.returned_rule_id
        )
        return context.make_get_rule_response(rule_id)

    @mockserver.json_handler(
        '/driver-work-rules/v1/work-rules/compatible/list',
    )
    def mock_rules_compatible(request):
        assert request.method == 'GET'
        context.validate_rules_compatible_request(request)
        rule_id = (
            context.rule_id
            if context.returned_rule_compatible_id is None
            else context.returned_rule_compatible_id
        )
        return context.make_rules_compatible_response(rule_id)

    return context
