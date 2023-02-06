from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from generated.clients import billing_subventions

from billing_functions.functions import score_driver_fix
from billing_functions.repositories import driver_fix_rules
import billing_functions.stq.pipelines._taxi_order.score_driver_fix as handler
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json', ['not_a_driver_fix.json', 'driver_fix.json'],
)
@pytest.mark.json_obj_hook(
    Query=score_driver_fix.Query,
    Driver=score_driver_fix.Query.Driver,
    Subscription=score_driver_fix.Query.Subscription,
    Order=score_driver_fix.Query.Order,
    #
    DriverFix=equatable.codegen(models.DriverFix),
    BalancesChange=models.DriverFixBalancesChange,
    #
    Doc=docs.Doc,
)
@pytest.mark.now('2020-12-22T08:48:39.046000+00:00')
@pytest.mark.config(BILLING_SUBVENTIONS_SHIFT_OPEN_MAX_REQUEST_AGE_HRS=1)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            driver_fix_rules_repo: driver_fix_rules.Repository,
            subventions_client: billing_subventions.BillingSubventionsClient,
            query: score_driver_fix.Query,
    ) -> models.DriverFix:
        del driver_fix_rules_repo  # unused
        del subventions_client  # unused
        nonlocal actual_query
        actual_query = query
        return models.DriverFix(
            agreement_id='agreement_id',
            balances_change=models.DriverFixBalancesChange(
                guarantee='0',
                intervals=[],
                minutes_on_order='0',
                income='0',
                coupon='0',
                discount='0',
            ),
            shift_ended_doc_id=12345,
        )

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
