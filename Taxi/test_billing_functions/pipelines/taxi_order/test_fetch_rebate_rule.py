from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions import consts
from billing_functions.functions import fetch_rebate_rule_data
from billing_functions.repositories import migration_mode
from billing_functions.repositories import rebate_rates
from billing_functions.stq.pipelines._taxi_order import (
    fetch_rebate_rule as handler,
)
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.parametrize('test_data_json', ['data.json'])
@pytest.mark.json_obj_hook(
    Query=fetch_rebate_rule_data.Query,
    Doc=docs.Doc,
    RebateMigrationMode=migration_mode.Mode,
    RebateRule=equatable.codegen(models.RebateRule),
    PaymentType=consts.PaymentType,
)
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test(test_data_json, *, stq3_context, load_py_json, monkeypatch):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.taxi_order.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    monkeypatch.setattr(
        stq3_context, 'cities', mocks.Cities(test_data['cities'], {}),
    )

    actual_query = None

    async def _function(
            rebate: rebate_rates.Repository,
            query: fetch_rebate_rule_data.Query,
    ) -> models.RebateRule:
        del rebate  # unused
        nonlocal actual_query
        actual_query = query
        return test_data['results']

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['results']
