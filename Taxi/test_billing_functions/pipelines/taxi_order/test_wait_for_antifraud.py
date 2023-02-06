from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import check_in_antifraud
from billing_functions.functions import wait_for_antifraud
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_order import (
    wait_for_antifraud as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json',
    [
        'pay.json',
        'no_payment.json',
        'only_subvention.json',
        'only_discount.json',
        'subvention_and_discount.json',
    ],
)
@pytest.mark.json_obj_hook(
    Query=wait_for_antifraud.Query,
    CheckQuery=check_in_antifraud.CheckOrderQuery,
    Order=check_in_antifraud.CheckOrderQuery.Order,
    Driver=check_in_antifraud.CheckOrderQuery.Driver,
    Antifraud=equatable.codegen(models.Antifraud),
    Results=pipeline.Results,
    Doc=docs.Doc,
)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            context: stq_context.Context, query: wait_for_antifraud.Query,
    ) -> wait_for_antifraud.Response:
        del context  # unused
        nonlocal actual_query
        actual_query = query
        return wait_for_antifraud.Response(
            decision=models.Antifraud(
                antifraud_id='some_antifraud_id', decision='pay',
            ),
            eta=None,
        )

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
