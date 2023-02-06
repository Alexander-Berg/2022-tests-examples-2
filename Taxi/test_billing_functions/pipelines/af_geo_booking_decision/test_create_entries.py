from __future__ import annotations

import dataclasses
from typing import Optional

import pytest

from billing.accounts import service as accounts
from billing.docs import service as docs
from billing_models.generated import models
from taxi.billing.util import dates

from billing_functions.functions import create_entries
from billing_functions.functions import generate_reversal_entries
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._af_geo_booking_decision import (
    create_entries as handler,
)
from test_billing_functions import equatable

_MOCK_NOW = '2021-03-01T00:00:00.000000+03:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)


@dataclasses.dataclass(frozen=True)
class Description:
    af_decision_doc: docs.TypedDoc[models.AntifraudDecision]
    base_doc: docs.Doc
    expected_query: create_entries.Query
    expected_results: pipeline.Results


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.json_obj_hook(
    Query=create_entries.Query,
    Template=create_entries.Query.Template,
    Results=pipeline.Results,
    LastEntries=equatable.codegen(models.LastEntries),
    Doc=docs.Doc,
    AntifraudDecision=models.AntifraudDecision,
    TLogV1Customizer=equatable.by_type(
        generate_reversal_entries.TlogV1Customizer,
    ),
    TLogV2Customizer=equatable.by_type(
        generate_reversal_entries.TlogV2Customizer,
    ),
    DriverIncomeCustomizer=equatable.by_type(
        generate_reversal_entries.DriverIncomeCustomizer,
    ),
)
@pytest.mark.now(_MOCK_NOW)
async def test(stq3_context, load_py_json, mock_billing_components):
    components = mock_billing_components(now=_MOCK_NOW_DT)

    test_data = Description(**load_py_json('test_data.json'))
    components.docs.items.append(test_data.base_doc)

    actual_query = None

    async def _function(
            docs_repo: docs.Docs,
            accounts_repo: accounts.Accounts,
            entities_repo: accounts.Entities,
            journal_repo: accounts.Journal,
            query: create_entries.Query,
    ) -> Optional[models.LastEntries]:
        del docs_repo  # unused
        del accounts_repo  # unused
        del entities_repo  # unused
        del journal_repo  # unused
        nonlocal actual_query
        actual_query = query
        return models.LastEntries(
            entry_ids=[1, 2], reversal_entry_ids=[3, 4], adopted_entry_ids=[],
        )

    actual_results = await handler.handle(
        stq3_context, test_data.af_decision_doc, _function,
    )
    assert actual_query == test_data.expected_query
    assert actual_results == test_data.expected_results
