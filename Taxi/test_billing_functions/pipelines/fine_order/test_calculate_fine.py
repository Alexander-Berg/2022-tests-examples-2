from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import calculate_fine
from billing_functions.repositories import commission_agreements
from billing_functions.repositories import currency_rates
from billing_functions.repositories import service_ids
from billing_functions.repositories import support_info
from billing_functions.stq.pipelines._fine_order import (
    calculate_fine as handler,
)


@pytest.mark.parametrize('test_data_json', ['data.json', 'no_fine_code.json'])
@pytest.mark.json_obj_hook(
    Query=calculate_fine.Query,
    FineCommission=lambda **kwargs: models.FineCommission.deserialize(kwargs),
    Contract=calculate_fine.Query.Contract,
    Order=calculate_fine.Query.Order,
    Doc=docs.Doc,
)
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test(test_data_json, *, stq3_context, load_py_json, monkeypatch):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['fine_order']
    data = models.fine_order.FineOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            currency_rates_repo: currency_rates.Repository,
            service_ids_repo: service_ids.Repository,
            commissions_repo: commission_agreements.Repository,
            support_info_repo: support_info.Repository,
            query: calculate_fine.Query,
    ) -> models.FineCommission:
        del currency_rates_repo  # unused
        del service_ids_repo  # unused
        del commissions_repo  # unused
        del support_info_repo  # unused
        nonlocal actual_query
        actual_query = query
        return test_data['results']

    actual_results = await handler.handle(stq3_context, doc, _function)

    assert actual_query == test_data['expected_query']
    assert (
        actual_results.serialize() == test_data['expected_results'].serialize()
    )
