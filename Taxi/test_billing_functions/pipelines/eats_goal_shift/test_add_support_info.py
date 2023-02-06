from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import build_goal_support_info
from billing_functions.stq.pipelines._eats_goal_shift import (
    add_support_info as handler,
)
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=build_goal_support_info.Query,
    GoalSupportInfo=equatable.codegen(models.GoalSupportInfo),
    SupportInfoData=models.GoalSupportInfoData,
    SupportInfoPayout=models.SupportInfoPayout,
    SupportInfoRule=models.SupportInfoRule,
    CalculatedValue=models.CalculatedValue,
    Calculation=models.Calculation,
    Money=models.Money,
    Doc=docs.Doc,
)
@pytest.mark.parametrize('doc_json', ['eats_goal_shift.json'])
async def test(doc_json, *, stq3_context, load_py_json):
    raw_doc = load_py_json(doc_json)
    data = models.EatsGoalShift.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    support_info = load_py_json('support_info.json')
    expected_query = load_py_json('expected_query.json')
    expected_results = load_py_json('expected_results.json')

    actual_query = None

    def _function(
            query: build_goal_support_info.Query,
    ) -> models.GoalSupportInfo:
        nonlocal actual_query
        actual_query = query
        return support_info

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == expected_query
    assert actual_results == expected_results
