from __future__ import annotations

import datetime

import pytest

from billing.accounts import service as accounts_models
from billing.docs import service as docs_models
from billing.docs import topics
from billing_models.generated import models
from taxi.util import dates

from billing_functions.functions import create_entries
from billing_functions.functions import generate_reversal_entries
from test_billing_functions import equatable

_DOC_ID = 18061991
_MOCK_NOW = '2020-12-31T23:59:59.999999+03:00'
_JSON_OBJ_HOOKS = dict(
    Query=create_entries.Query,
    Entries=create_entries.Query.Entries,
    Template=create_entries.Query.Template,
    VersionedDocRefDoc=topics.VersionedDocRefDoc,
    VersionedDocRef=topics.VersionedDocRef,
    Account=accounts_models.Account,
    AppendedEntry=accounts_models.AppendedEntry,
    Doc=docs_models.Doc,
    LastEntries=equatable.codegen(models.LastEntries),
    TLogV1Customizer=generate_reversal_entries.TlogV1Customizer,
    TLogV2Customizer=generate_reversal_entries.TlogV2Customizer,
    DriverIncomeCustomizer=generate_reversal_entries.DriverIncomeCustomizer,
    SubventionAnalyticalCustomizer=(
        generate_reversal_entries.SubventionAnalyticalCustomizer
    ),
)


@pytest.mark.json_obj_hook(**_JSON_OBJ_HOOKS)
@pytest.mark.parametrize(
    'query_json, expected_accounts_json, expected_entries_json',
    [
        (
            'wait_for_antifraud.json',
            'expected_delay_accounts.json',
            'expected_delay_entries.json',
        ),
        (
            'pay.json',
            'expected_pay_accounts.json',
            'expected_pay_entries.json',
        ),
        (
            'block.json',
            'expected_no_accounts.json',
            'expected_no_entries.json',
        ),
        (
            'no_antifraud.json',
            'expected_no_accounts.json',
            'expected_no_entries.json',
        ),
        (
            'pay_old_event.json',
            'expected_pay_accounts_without_income.json',
            'expected_pay_entries_without_income.json',
        ),
        (
            'pay_with_park_commission.json',
            'expected_pay_accounts_with_park_commission.json',
            'expected_pay_entries_with_park_commission.json',
        ),
    ],
)
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(BILLING_OLD_JOURNAL_LIMIT_DAYS=10)
async def test_create_entries(
        query_json,
        expected_accounts_json,
        expected_entries_json,
        *,
        mock_billing_components,
        load_py_json,
        stq3_context,
):
    billing_components = mock_billing_components(dates.utc_with_tz())
    expected_accounts = load_py_json(expected_accounts_json)
    expected_entries = load_py_json(expected_entries_json)
    query = load_py_json(query_json)
    response = await create_entries.execute(
        stq3_context.docs,
        stq3_context.accounts,
        stq3_context.entities,
        stq3_context.journal,
        query,
    )
    assert response
    assert response.entry_ids == [e.id for e in expected_entries]

    assert billing_components.accounts.items == expected_accounts
    assert billing_components.journal.items == expected_entries


@pytest.mark.json_obj_hook(**_JSON_OBJ_HOOKS)
@pytest.mark.config(
    BILLING_OLD_JOURNAL_LIMIT_DAYS=10,
    BILLING_DOCS_REPLICATION_LAG_MS=100,
    BILLING_ACCOUNTS_JOURNAL_REPLICATION_LAG_MS=100,
)
@pytest.mark.dontfreeze
async def test_wait_for_replication(
        mock_billing_components, load_py_json, stq3_context,
):
    mock_billing_components(dates.utc_with_tz())
    query = load_py_json('pay.json')
    was = dates.utc_with_tz()
    await create_entries.execute(
        stq3_context.docs,
        stq3_context.accounts,
        stq3_context.entities,
        stq3_context.journal,
        query,
    )
    now = dates.utc_with_tz()
    assert now - was >= datetime.timedelta(milliseconds=200)


@pytest.mark.json_obj_hook(**_JSON_OBJ_HOOKS)
@pytest.mark.parametrize(
    'test_data_json',
    (
        'amend_prev_doc_with_last_entries.json',
        'revert_prev_doc_with_last_entries.json',
        'revert_prev_doc_without_last_entries.json',
    ),
)
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(BILLING_OLD_JOURNAL_LIMIT_DAYS=10)
async def test_reverse_previous_doc(
        test_data_json, *, mock_billing_components, load_py_json, stq3_context,
):
    test_data = load_py_json(test_data_json)
    bcomponents = mock_billing_components(dates.utc_with_tz())
    bcomponents.docs.items.extend(
        [test_data['doc']] + test_data['history_docs'],
    )
    bcomponents.accounts.items.extend(test_data['accounts'])
    bcomponents.journal.items.extend(test_data['entries'])
    results = await create_entries.execute(
        stq3_context.docs,
        stq3_context.accounts,
        stq3_context.entities,
        stq3_context.journal,
        test_data['query'],
    )
    assert results == test_data['expected_results']
