import datetime as dt

import pytest

from billing_models.generated import models
from taxi.billing.util import dates

from billing_functions.functions.subventions import score_goal
from billing_functions.repositories import subvention_rules
from billing_functions.stq import events
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['regular_eats_order.json'])
@pytest.mark.json_obj_hook(
    Query=score_goal.Query,
    Driver=score_goal.Query.Driver,
    Order=score_goal.Query.Order,
    ShiftsConfig=score_goal.Query.ShiftsConfig,
    Subventions=equatable.codegen(models.Subventions),
    AntifraudPrecheck=models.AntifraudPrecheck,
    EatsSubventionShifts=models.EatsSubventionShifts,
    SubventionShift=models.SubventionShift,
    GoalRuleShift=models.GoalRuleShift,
    GoalRule=subvention_rules.GoalRule,
    GoalRuleStep=subvention_rules.GoalRule.Step,
    GoalRuleWindow=subvention_rules.GoalRule.Window,
)
@pytest.mark.now('2021-01-01T00:00:00+00:00')
async def test_calculate_subventions(
        test_data_json,
        *,
        load_py_json,
        stq3_context,
        do_mock_billing_docs,
        patched_stq_queue,
):
    test_data = load_py_json(test_data_json)
    billing_docs = do_mock_billing_docs()

    scheduler = events.Scheduler(
        stq3_context.docs,
        stq3_context.stq,
        no_jitter,
        dates.utc_now_with_tz,
        enabled=True,
    )
    results = await score_goal.execute(
        events_scheduler=scheduler, query=test_data['query'],
    )

    assert results.serialize() == test_data['expected_results'].serialize()
    assert billing_docs.created_docs == test_data['expected_docs']
    assert patched_stq_queue.pop_calls() == test_data['expected_stq_calls']


def no_jitter(seed: str) -> dt.timedelta:
    del seed  # unused
    return dt.timedelta()
