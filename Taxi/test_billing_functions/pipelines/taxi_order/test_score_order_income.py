from __future__ import annotations

from typing import Optional

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import score_order_income
from billing_functions.stq.pipelines._taxi_order import (
    score_order_income as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.json_obj_hook(
    Query=score_order_income.Query,
    Order=score_order_income.Query.Order,
    OrderIncome=equatable.codegen(models.OrderIncome),
    Money=models.Money,
    Doc=docs.Doc,
)
@pytest.mark.now('2021-05-18T00:00:00+00:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    results = models.OrderIncome(
        driver_balance_change=models.Money(amount='272.0', currency='RUB'),
        num_orders=1,
        num_orders_completed=1,
    )

    actual_query = None

    def _function(
            query: score_order_income.Query,
    ) -> Optional[models.OrderIncome]:
        nonlocal actual_query
        actual_query = query
        return results

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == results
