from __future__ import annotations

import pytest

from billing.accounts import service as accounts
from billing.docs import service as docs
from billing_models.generated import models
from taxi.util import dates

from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._cargo_order import (
    create_entries as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json',
    ['test_data.json', 'test_data_with_claims.json', 'driver_fix.json'],
)
@pytest.mark.json_obj_hook(
    LastEntries=equatable.codegen(models.LastEntries),
    Money=models.Money,
    Results=pipeline.Results,
    Doc=docs.Doc,
    Account=accounts.Account,
    AppendedEntry=accounts.AppendedEntry,
)
@pytest.mark.now('2021-05-18T00:00:00+00:00')
async def test(
        test_data_json, *, stq3_context, load_py_json, mock_billing_components,
):
    components = mock_billing_components(now=dates.utc_with_tz())
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['cargo_order']
    data = models.CargoOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_results = await handler.handle(stq3_context, doc)
    assert actual_results == test_data['expected_results']
    assert components.accounts.items == test_data['expected_accounts']
    assert components.journal.items == test_data['expected_journal']
