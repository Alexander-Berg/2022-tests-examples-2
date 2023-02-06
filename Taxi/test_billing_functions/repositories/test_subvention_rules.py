import pytest

from billing_functions.repositories import subvention_rules


@pytest.mark.json_obj_hook(
    Query=subvention_rules.MatchQuery,
    SingleRideRule=subvention_rules.SingleRideRule,
    SingleOnTopRule=subvention_rules.SingleOnTopRule,
    GoalRule=subvention_rules.GoalRule,
    GoalRuleWindow=subvention_rules.GoalRule.Window,
    GoalRuleStep=subvention_rules.GoalRule.Step,
)
async def test_match_smart(
        load_py_json, mock_billing_subventions_x, stq3_context,
):
    test_data = load_py_json('test_match_smart.json')
    mock_billing_subventions_x([], test_data['match_responses'])
    repo = stq3_context.subvention_rules
    rules = await repo.match_smart(test_data['query'])

    actual_requests = mock_billing_subventions_x.v2_rules_match_requests
    expected_requests = test_data['expected_match_requests']
    assert actual_requests == expected_requests

    assert rules == test_data['expected_rules']


@pytest.mark.json_obj_hook(
    Query=subvention_rules.MatchQuery,
    NmfgRule=subvention_rules.NmfgRule,
    GeoBookingRule=subvention_rules.GeoBookingRule,
    DoXGetYRule=subvention_rules.DoXGetYRule,
)
async def test_match_legacy(
        load_py_json, mock_billing_subventions_x, stq3_context,
):
    test_data = load_py_json('test_match_legacy.json')
    mock_billing_subventions_x(test_data['match_responses'], [])
    repo = stq3_context.subvention_rules
    rules = await repo.match_legacy(test_data['query'])

    actual_requests = mock_billing_subventions_x.v1_rules_match_requests
    expected_requests = test_data['expected_match_requests']
    assert actual_requests == expected_requests

    assert rules == test_data['expected_rules']
