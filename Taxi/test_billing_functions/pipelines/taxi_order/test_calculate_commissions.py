from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from billing_models.generated.models import park_commission

from billing_functions.functions import calculate_commission
from billing_functions.functions.core.commissions import call_center
from billing_functions.functions.core.commissions import (
    models as commission_models,
)
from billing_functions.repositories import commission_agreements
from billing_functions.repositories import currency_rates
from billing_functions.repositories import migration_mode
from billing_functions.repositories import service_ids
from billing_functions.repositories import support_info
from billing_functions.stq.pipelines._taxi_order import (
    calculate_commission as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json', ['data.json', 'data_no_rebate_rule.json'],
)
@pytest.mark.json_obj_hook(
    Query=calculate_commission.Query,
    Component=commission_models.Component,
    Commission=commission_models.Commission,
    Contract=calculate_commission.Query.Contract,
    Driver=calculate_commission.Query.Driver,
    Order=calculate_commission.Query.Order,
    DriverPromocode=calculate_commission.Query.DriverPromocode,
    HiringInfo=calculate_commission.Query.Driver.HiringInfo,
    ParkCommissionRule=equatable.codegen(
        park_commission.OrderParkCommissionRule,
    ),
    CallCenter=call_center.CallCenter,
    Doc=docs.Doc,
    RebateMigrationMode=migration_mode.Mode,
    RebateRule=equatable.codegen(models.RebateRule),
)
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test(test_data_json, *, stq3_context, load_py_json, monkeypatch):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.taxi_order.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            currency_rates_repo: currency_rates.Repository,
            service_ids_repo: service_ids.Repository,
            commissions_repo: commission_agreements.Repository,
            support_info_repo: support_info.Repository,
            query: calculate_commission.Query,
    ) -> models.RebateRule:
        del currency_rates_repo  # unused
        del service_ids_repo  # unused
        del commissions_repo  # unused
        del support_info_repo  # unused
        nonlocal actual_query
        actual_query = query
        return test_data['results']

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['results']
