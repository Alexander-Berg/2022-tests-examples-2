from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import score_cash_payment
from billing_functions.stq.pipelines._shuttle_order import (
    score_cash_payment as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['cash.json', 'card.json'])
@pytest.mark.json_obj_hook(
    Query=score_cash_payment.Query,
    CashPayment=equatable.codegen(models.CashPayment),
    Money=models.Money,
    Doc=docs.Doc,
)
@pytest.mark.now('2021-05-18T00:00:00+00:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['shuttle_order']
    data = models.ShuttleOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    def _function(query: score_cash_payment.Query) -> models.CashPayment:
        nonlocal actual_query
        actual_query = query
        return models.CashPayment(order_cost='0.0')

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
