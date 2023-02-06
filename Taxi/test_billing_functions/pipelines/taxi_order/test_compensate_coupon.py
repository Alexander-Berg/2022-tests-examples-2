from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from billing_models.generated.models import order_coupon_compensation

from billing_functions.functions import compensate_coupon
from billing_functions.repositories import cities
from billing_functions.repositories import currency_rates
from billing_functions.repositories import service_ids
from billing_functions.stq.pipelines._taxi_order import (
    compensate_coupon as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json', ['no_coupon.json', 'coupon_exists.json'],
)
@pytest.mark.json_obj_hook(
    Query=compensate_coupon.Query,
    Contract=compensate_coupon.Query.Contract,
    CouponCompensation=equatable.codegen(
        order_coupon_compensation.CouponCompensation,
    ),
    CouponPayment=order_coupon_compensation.CouponPayment,
    Money=models.Money,
    Doc=docs.Doc,
)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['taxi_order']
    data = models.TaxiOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            cities_repo: cities.Repository,
            currency_rates_repo: currency_rates.Repository,
            service_ids_repo: service_ids.Repository,
            query: compensate_coupon.Query,
    ) -> order_coupon_compensation.CouponCompensation:
        del cities_repo  # unused
        del currency_rates_repo  # unused
        del service_ids_repo  # unused
        nonlocal actual_query
        actual_query = query
        return order_coupon_compensation.CouponCompensation(
            is_compensated=False, skip_reason='function_called',
        )

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
