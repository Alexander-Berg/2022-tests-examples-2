from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import compensate_discount
from billing_functions.repositories import cities
from billing_functions.repositories import currency_rates
from billing_functions.repositories import service_ids
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_order import (
    compensate_discount as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json', ['no_discount.json', 'discount_exists.json'],
)
@pytest.mark.json_obj_hook(
    Query=compensate_discount.Query,
    Contract=compensate_discount.Query.Contract,
    DiscountCompensation=equatable.codegen(models.DiscountCompensation),
    DiscountPayment=models.DiscountPayment,
    Money=models.Money,
    Results=pipeline.Results,
    Doc=docs.Doc,
    ParkCommissionRule=equatable.codegen(models.BaseParkCommissionRule),
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
            query: compensate_discount.Query,
    ) -> models.DiscountCompensation:
        del cities_repo  # unused
        del currency_rates_repo  # unused
        del service_ids_repo  # unused
        nonlocal actual_query
        actual_query = query
        return models.DiscountCompensation(
            is_compensated=False, skip_reason='function_called',
        )

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == test_data['expected_results']
