from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import fetch_contracts
from billing_functions.repositories import contracts
from billing_functions.repositories import migration_mode
from billing_functions.stq.pipelines._fine_order import (
    fetch_contracts as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['no_waiting.json'])
@pytest.mark.json_obj_hook(
    Query=fetch_contracts.Query,
    Contracts=equatable.codegen(models.Contracts),
    ActiveContract=models.ActiveContract,
    ServiceToContract=models.ServiceToContract,
    WaitPolicy=fetch_contracts.WaitPolicy,
    Doc=docs.Doc,
)
@pytest.mark.config(
    BILLING_SUBVENTIONS_CONTRACT_DELAY=60,
    BILLING_SUBVENTIONS_CONTRACT_RETRY=10,
)
@pytest.mark.now('2021-05-18T00:00:00+00:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['fine_order']
    data = models.FineOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    results = fetch_contracts.Result.done(
        models.Contracts(
            items=[], service_to_contract=models.ServiceToContract({}),
        ),
    )

    actual_query = None

    async def _function(
            contracts_repo: contracts.Repository,
            migration_repo: migration_mode.Repository,
            query: fetch_contracts.Query,
    ) -> fetch_contracts.Result:
        del contracts_repo  # unused
        del migration_repo  # unused
        nonlocal actual_query
        actual_query = query
        return results

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == results.contracts
