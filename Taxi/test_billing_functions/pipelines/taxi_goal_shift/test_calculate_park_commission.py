from typing import Optional

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import calculate_park_commission_value
from billing_functions.stq.pipelines._taxi_goal_shift import (
    calculate_park_commission as pipeline_handler,
)
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Data=lambda **json: models.taxi_goal_shift.TaxiGoalShift.deserialize(json),
    Query=calculate_park_commission_value.Query,
    ParkCommission=equatable.codegen(models.ParkCommissionValue),
    ParkCommissionRule=models.BaseParkCommissionRule,
    ParkCommissionRules=equatable.codegen(models.ParkCommissionRules),
)
@pytest.mark.parametrize(
    'test_data_json', ['test_data.json', 'per_contract.json'],
)
async def test_taxi_goal_shift_calculate_park_commission(
        test_data_json, stq3_context, load_py_json,
):
    test_data = load_py_json(test_data_json)
    actual_query = None

    def _function(
            query: calculate_park_commission_value.Query,
    ) -> Optional[models.ParkCommission]:
        nonlocal actual_query
        actual_query = query
        return test_data['park_commission']

    actual_results = await pipeline_handler.handle(
        stq3_context, test_data['doc'], _function,
    )
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['park_commission']
