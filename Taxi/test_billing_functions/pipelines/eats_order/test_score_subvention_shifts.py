from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions.core import events
from billing_functions.functions.subventions import score_goal
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._eats_order import (
    score_subvention_shifts as handler,
)

_MOCK_NOW = '2021-01-01T00:00:00.000+00:00'


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.json_obj_hook(
    Query=score_goal.Query,
    Order=score_goal.Query.Order,
    Driver=score_goal.Query.Driver,
    ShiftsConfig=score_goal.Query.ShiftsConfig,
    Doc=docs.Doc,
    Results=pipeline.Results,
)
@pytest.mark.config(PROCESS_SHIFT_ENDED_MIN_MSK_TIME='04:00')
@pytest.mark.now(_MOCK_NOW)
async def test(
        test_data_json,
        *,
        stq3_context,
        load_py_json,
        mock_billing_subventions_x,
):
    test_data = load_py_json(test_data_json)
    mock_billing_subventions_x(
        test_data['bsx_v1_rules_match_responses'],
        test_data['bsx_v2_rules_match_responses'],
    )

    raw_doc = test_data['eats_order']
    data = models.EatsOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            shift_scheduler: events.Scheduler, query: score_goal.Query,
    ):
        del shift_scheduler  # unused
        nonlocal actual_query
        actual_query = query
        return None

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results is None
