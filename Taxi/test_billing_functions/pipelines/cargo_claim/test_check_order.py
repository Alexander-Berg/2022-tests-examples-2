from __future__ import annotations

from typing import Optional

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import check_order
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._cargo_claim import check_order as handler
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json', ['test_data.json', 'test_data_postponed.json'],
)
@pytest.mark.json_obj_hook(
    Query=check_order.Query,
    ProcessingInfo=equatable.codegen(models.ProcessingInfo),
    Money=models.Money,
    Results=pipeline.Results,
    Doc=docs.Doc,
)
@pytest.mark.now('2021-05-18T03:00:00+03:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['cargo_claim']
    data = models.CargoClaim.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            context: stq_context.Context, query: check_order.Query,
    ) -> Optional[models.ProcessingInfo]:
        nonlocal actual_query
        actual_query = query
        return None

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
