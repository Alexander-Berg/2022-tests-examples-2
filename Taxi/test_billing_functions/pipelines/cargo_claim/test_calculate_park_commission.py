from typing import Optional

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import calculate_park_commission
from billing_functions.stq.pipelines._cargo_claim import (
    calculate_park_commission as handler,
)
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Query=calculate_park_commission.Query,
    Subvention=calculate_park_commission.Query.Subvention,
    ParkCommissionRules=equatable.codegen(models.ParkCommissionRules),
    BaseParkCommissionRule=models.BaseParkCommissionRule,
    ParkCommission=equatable.codegen(models.ParkCommission),
    ParkCommissionValue=equatable.codegen(models.ParkCommissionValue),
)
async def test_taxi_order_calculate_park_commission(
        stq3_context, load_py_json,
):
    test_data = load_py_json('data.json')
    raw_doc = test_data['cargo_claim']
    data = models.CargoClaim.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    def _function(
            query: calculate_park_commission.Query,
    ) -> Optional[models.ParkCommission]:
        nonlocal actual_query
        actual_query = query
        return test_data['results']

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['results']
