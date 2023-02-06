from __future__ import annotations

import asyncio
from unittest import mock

import pytest

from billing.docs import service as docs
from billing_models.generated.models import taxi_goal_shift
from taxi.billing.util import dates

from billing_functions.functions import create_entries
from billing_functions.functions import generate_reversal_entries
from billing_functions.stq import converters
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_goal_shift import (
    create_antifraud_entries,
)
from billing_functions.stq.pipelines._taxi_goal_shift import (
    create_payment_entries,
)
from test_billing_functions import equatable

_DOC_ID = 18061991
_MOCK_NOW = '2020-12-31T23:59:59.999999+03:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)
_HOOKS = dict(
    Query=create_entries.Query,
    Template=create_entries.Query.Template,
    Results=pipeline.Results,
    Doc=docs.Doc,
    Data=lambda **json: taxi_goal_shift.TaxiGoalShift.deserialize(json),
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


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.json_obj_hook(**_HOOKS)
@pytest.mark.now(_MOCK_NOW)
def test_make_query(stq3_context, taxi_shift_doc, load_py_json):
    query = converters.create_goal_entries_query(
        stq3_context.config,
        taxi_shift_doc.id,
        taxi_shift_doc,
        _MOCK_NOW_DT,
        pay_per_contract=False,
    )
    expected_query = load_py_json('expected_query.json')
    assert query == expected_query


@pytest.fixture(name='taxi_shift_doc')
def _make_taxi_shift(
        load_py_json,
) -> docs.TypedDoc[taxi_goal_shift.TaxiGoalShift]:
    doc = docs.Doc(**load_py_json('doc.json'))
    data = taxi_goal_shift.TaxiGoalShift.deserialize(doc.data)
    return docs.TypedDoc.from_doc(doc, data)


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.json_obj_hook(**_HOOKS)
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.parametrize(
    'taxi_shift_doc_json, expected_query_json',
    [
        ('doc.json', 'expected_query.json'),
        (
            'doc_with_park_commission.json',
            'expected_query_with_park_commission.json',
        ),
        (
            'doc_with_zero_park_commission.json',
            'expected_query_with_zero_park_commission.json',
        ),
        (
            'doc_with_park_commission_block.json',
            'expected_query_with_park_commission_block.json',
        ),
        (
            'doc_with_park_commission_delay.json',
            'expected_query_with_park_commission_delay.json',
        ),
    ],
)
def test_make_query_with_park_commission(
        stq3_context, taxi_shift_doc_json, expected_query_json, load_py_json,
):
    doc = docs.Doc(**load_py_json(taxi_shift_doc_json))
    data = taxi_goal_shift.TaxiGoalShift.deserialize(doc.data)
    taxi_shift_doc = docs.TypedDoc.from_doc(doc, data)
    query = converters.create_goal_entries_query(
        stq3_context.config,
        taxi_shift_doc.id,
        taxi_shift_doc,
        _MOCK_NOW_DT,
        pay_per_contract=False,
    )
    expected_query = load_py_json(expected_query_json)
    assert query == expected_query


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.parametrize(
    'test_data_json', ['per_contract.json', 'per_contract_test.json'],
)
@pytest.mark.json_obj_hook(**_HOOKS)
@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
async def test_create_payment_entries(
        test_data_json, *, stq3_context, load_py_json,
):
    test_data = load_py_json(test_data_json)
    future = asyncio.Future()
    future.set_result(None)
    func = mock.Mock(spec=create_entries.execute, return_value=future)
    await create_payment_entries.handle(stq3_context, test_data['doc'], func)
    assert func.call_args_list == [
        mock.call(
            stq3_context.docs,
            stq3_context.accounts,
            stq3_context.entities,
            equatable.by_type(test_data['expected_journal_repo_type'])(),
            test_data['expected_query'],
        ),
    ]


@pytest.mark.config(
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
)
@pytest.mark.parametrize(
    'test_data_json', ['per_contract.json', 'per_contract_test.json'],
)
@pytest.mark.json_obj_hook(**_HOOKS)
@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
async def test_create_antifraud_entries(
        test_data_json, *, stq3_context, load_py_json,
):
    test_data = load_py_json(test_data_json)
    future = asyncio.Future()
    future.set_result(None)
    func = mock.Mock(spec=create_entries.execute, return_value=future)
    await create_antifraud_entries.handle(stq3_context, test_data['doc'], func)
    assert func.call_args_list == [
        mock.call(
            stq3_context.docs,
            stq3_context.accounts,
            stq3_context.entities,
            equatable.by_type(test_data['expected_journal_repo_type'])(),
            test_data['expected_query'],
        ),
    ]
