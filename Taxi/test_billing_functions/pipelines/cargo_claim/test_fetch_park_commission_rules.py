import pytest

from billing.docs import service as docs
from billing_models.generated import models
from generated.clients import driver_work_modes as dwm_client

from billing_functions.functions import fetch_park_commission_rules
from billing_functions.stq.pipelines._cargo_claim import (
    fetch_park_commission_rules as handler,
)
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    Query=fetch_park_commission_rules.Query,
    QueryOrder=fetch_park_commission_rules.Query.Order,
    ParkCommissionRules=equatable.codegen(models.ParkCommissionRules),
    ParkCommissionRule=models.BaseParkCommissionRule,
)
async def test_taxi_goal_shift_fetch_park_commission_rule(
        stq3_context, load_py_json,
):
    test_data = load_py_json('data.json')
    raw_doc = test_data['cargo_claim']
    data = models.cargo_claim.CargoClaim.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            driver_work_modes_client: dwm_client.DriverWorkModesClient,
            query: fetch_park_commission_rules.Query,
    ) -> models.ParkCommissionRules:
        del driver_work_modes_client  # unused
        nonlocal actual_query
        actual_query = query
        return test_data['park_commission_rules']

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['park_commission_rules']
