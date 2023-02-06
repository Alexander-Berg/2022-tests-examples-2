import json

import pytest


class BillingSubventionsContext:
    def __init__(self):
        self.active_rules = []
        self.drivers_onorder_activity = []
        self.calls = 0
        self.rules_select_subventions_call_params = []
        self.by_driver_subventions_call_params = []
        self.by_driver_subventions = []
        self.by_driver_calls = 0
        self.rules_select_limit = -1
        self.rules_select_i = 0

    def add_rule(self, rule):
        self.active_rules.append(rule)

    def add_driver_onorder_activity(self, driver_id, onorder_seconds=0):
        self.drivers_onorder_activity.append(
            {
                'unique_driver_id': driver_id,
                'on_order_seconds': onorder_seconds,
            },
        )

    def clean_rules(self):
        self.active_rules = []

    def add_by_driver_subvention(self, subv):
        self.by_driver_subventions.append(subv)

    def clean_by_driver_subvention(self):
        self.by_driver_subventions = []

    def set_rules_select_limit(self, limit):
        self.rules_select_limit = limit


@pytest.fixture(autouse=True)
def bss(mockserver):
    bss_context = BillingSubventionsContext()

    @mockserver.json_handler('/bss/v1/rules/select')
    def _mock_rules_select(request):
        bss_context.calls += 1
        bss_context.rules_select_subventions_call_params.append(
            request.get_data(),
        )
        if bss_context.rules_select_limit == -1:
            bss_context.rules_select_i = 0
            return {'subventions': bss_context.active_rules}
        else:
            if bss_context.rules_select_i == -1:
                bss_context.rules_select_i = 0
                return {'subventions': []}
            left_end = bss_context.rules_select_i
            if (
                    bss_context.rules_select_i + bss_context.rules_select_limit
                    >= len(bss_context.active_rules)
            ):
                right_end = len(bss_context.active_rules)
                bss_context.rules_select_i = -1
            else:
                right_end = (
                    bss_context.rules_select_i + bss_context.rules_select_limit
                )
                bss_context.rules_select_i = right_end
            return {
                'subventions': bss_context.active_rules[left_end:right_end],
            }

    @mockserver.json_handler('/bss/v1/driver_geoarea_activity')
    def _get_driver_onorder_activity(request):
        data = json.loads(request.get_data())
        return {
            'geoarea': data['geoarea'],
            'as_of_time': data['as_of_time'],
            'drivers': bss_context.drivers_onorder_activity,
        }

    @mockserver.json_handler('/bss/v1/by_driver')
    def _get_by_driver(request):
        bss_context.by_driver_calls += 1
        bss_context.by_driver_subventions_call_params.append(
            request.get_data(),
        )
        return {'subventions': bss_context.by_driver_subventions}

    return bss_context
