import pytest

from billing_functions.repositories import driver_fix_rules


@pytest.mark.json_obj_hook(
    Rule=driver_fix_rules.Rule,
    RateInterval=driver_fix_rules.Rule.RateInterval,
    RateIntervalEndpoint=driver_fix_rules.Rule.RateIntervalEndpoint,
)
async def test_fetch(load_py_json, stq3_context, mock_billing_subventions_x):
    test_data = load_py_json('test_data.json')
    mock_billing_subventions_x(test_data['responses'], [])
    repo = stq3_context.driver_fix_rules
    rule = await repo.fetch(**test_data['query'])
    assert rule == test_data['expected_rule']
