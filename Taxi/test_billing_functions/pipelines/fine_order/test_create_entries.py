from __future__ import annotations

import pytest

from billing.accounts import service as accounts
from billing.docs import service as docs
from billing_models.generated import models
from taxi.util import dates

from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._fine_order import (
    create_entries as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json',
    ['same_fines.json', 'no_contract.json', 'different_fines.json'],
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
@pytest.mark.config(
    BILLING_SUBVENTIONS_COMMISSION_TEMPLATE_SUBSTITUTIONS={
        'hiring_tlog_detailed_products': {
            'commercial': 'gross_driver_hiring_commission_trips',
            'commercial_returned': 'commercial_returned',
            'commercial_with_rent': 'gross_driver_hiring_commission_trips',
        },
        'hiring_tlog_products': {
            'commercial': 'hiring_with_car',
            'commercial_returned': 'commercial_returned',
            'commercial_with_rent': 'hiring_with_car',
        },
        'hiring_type_sub_account': {'commercial_with_rent': 'hiring_with_car'},
    },
    BILLING_FUNCTIONS_ADD_TLOG_EXTERNAL_REF='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_ADD_TLOG_TARGET='2001-01-01T00:00:00+00:00',
    BILLING_FUNCTIONS_PRODUCE_AGGREGATOR_COMMISSION_SINCE=(
        '2001-01-01T00:00:00+00:00'
    ),
    BILLING_FUNCTIONS_ADD_IS_PLATFORM_COMMISSION_ENABLED_SINCE=(
        '2001-01-01T00:00:00+00:00'
    ),
)
async def test(
        test_data_json,
        *,
        mock_billing_commissions,
        stq3_context,
        load_py_json,
        mock_billing_components,
):
    mock_billing_commissions(
        categories=load_py_json('commission_categories.json'),
    )
    components = mock_billing_components(now=dates.utc_with_tz())
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['fine_order']
    data = models.FineOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_results = await handler.handle(stq3_context, doc)

    assert actual_results == test_data['expected_results']
    assert components.accounts.items == test_data['expected_accounts']
    assert components.journal.items == test_data['expected_journal']
