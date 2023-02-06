from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import forward_entries
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq.pipelines._taxi_goal_shift import (
    forward_entries as handler,
)


@pytest.mark.json_obj_hook(
    Query=forward_entries.Query,
    Doc=docs.Doc,
    Data=lambda **kwargs: models.TaxiGoalShift.deserialize(kwargs),
)
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test_do_nothing_if_reconciliation(stq3_context, load_py_json):
    doc = load_py_json('doc.json')

    async def _function(
            context: stq_context.Context, query: forward_entries.Query,
    ) -> None:
        del context  # unused
        del query  # unused
        pytest.fail('must not be here')

    await handler.handle(stq3_context, doc, _function)
