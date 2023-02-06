from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import check_in_antifraud
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq.pipelines._cargo_claim import (
    check_subvention_in_antifraud as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.json_obj_hook(
    Query=check_in_antifraud.CheckOrderQuery,
    Order=check_in_antifraud.CheckOrderQuery.Order,
    Driver=check_in_antifraud.CheckOrderQuery.Driver,
    Antifraud=equatable.codegen(models.Antifraud),
    Doc=docs.Doc,
)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['cargo_claim']
    data = models.CargoClaim.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    results = models.Antifraud(
        antifraud_id='some_antifraud_id', decision='pay',
    )

    actual_query = None

    async def _function(
            context: stq_context.Context, query: check_in_antifraud.Query,
    ) -> check_in_antifraud.Result:
        del context  # unused
        nonlocal actual_query
        actual_query = query
        return results

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == results
