from typing import Iterable
from typing import List
from unittest import mock

import asynctest
import pytest

from billing.accounts import entries
from billing.accounts import service as accounts
from billing.generated.models import entries as entries_models
from testsuite.utils import ordered_object

from billing_functions.functions import generate_reversal_entries
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=generate_reversal_entries.Query,
    JournalEntryDraft=equatable.codegen(entries.JournalEntryDraft),
    SelectedEntry=accounts.SelectedEntry,
    TLogV1Customizer=generate_reversal_entries.TlogV1Customizer,
    TLogV2Customizer=generate_reversal_entries.TlogV2Customizer,
    DriverIncomeCustomizer=generate_reversal_entries.DriverIncomeCustomizer,
    SubventionAnalyticalCustomizer=(
        generate_reversal_entries.SubventionAnalyticalCustomizer
    ),
)
@pytest.mark.parametrize(
    'test_data_json', ['test_data.json', 'no_antifraud.json'],
)
async def test_generate_entries(test_data_json, *, context, load_py_json):
    data = load_py_json(test_data_json)
    context.journal.select_by_id_or_die.return_value = data['existing_entries']

    actual_entries = await generate_reversal_entries.execute(
        context.journal, data['query'],
    )
    assert_entries_equal(
        data['expected_entries'],
        [reversal.reversed for reversal in actual_entries],
    )


@pytest.fixture(name='context')
def make_context(stq3_context, load_py_json):
    context = mock.Mock(
        spec=stq3_context, journal=asynctest.Mock(spec=accounts.Journal),
    )
    return context


def assert_entries_equal(
        lhs: Iterable[entries_models.JournalEntryDraft],
        rhs: Iterable[entries_models.JournalEntryDraft],
):
    ordered_object.assert_eq(_normalize(lhs), _normalize(rhs), ['details'])


def _normalize(
        items: Iterable[entries_models.JournalEntryDraft],
) -> List[dict]:
    ordered = sorted(items, key=lambda e: e.idempotency_key)
    return [item.serialize() for item in ordered]
