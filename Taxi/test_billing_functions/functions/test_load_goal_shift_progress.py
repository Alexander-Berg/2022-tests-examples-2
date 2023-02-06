import pytest

from billing_models.generated.models import goal_shift

from billing_functions.functions import load_goal_progress
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=load_goal_progress.Query,
    GoalShiftProgress=equatable.codegen(goal_shift.GoalShiftProgress),
)
async def test_load_progress(
        stq3_context, load_py_json, do_mock_billing_accounts,
):
    test_data = load_py_json('test_data.json')
    do_mock_billing_accounts(existing_balances=test_data['balances'])
    actual_result = await load_goal_progress.execute(
        stq3_context.balances, test_data['query'],
    )
    assert actual_result == test_data['expected_result']
