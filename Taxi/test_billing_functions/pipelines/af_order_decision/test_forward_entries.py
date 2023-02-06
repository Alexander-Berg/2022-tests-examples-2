from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from taxi.billing.util import dates

from billing_functions.functions import forward_entries
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq.pipelines._af_order_decision import (
    forward_entries as handler,
)
from test_billing_functions import equatable

_MOCK_NOW = '2021-03-01T00:00:00.000000+03:00'
_MOCK_NOW_DT = dates.parse_datetime(_MOCK_NOW)


@pytest.mark.json_obj_hook(
    Doc=docs.TypedDoc,
    AntifraudDecision=models.AntifraudDecision,
    Query=forward_entries.Query,
    LastEntries=equatable.codegen(models.LastEntries),
)
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(
    BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
        'by_zone': {
            '__default__': {
                'enabled': [{'since': '1991-06-18T07:15:00+03:00'}],
            },
        },
    },
)
async def test(stq3_context, load_py_json, mock_billing_components):
    components = mock_billing_components(now=_MOCK_NOW_DT)
    base_doc = docs.Doc(**load_py_json('taxi_order.json'))
    components.docs.items.append(base_doc)
    af_decision_doc = load_py_json('af_decision.json')
    expected_query = load_py_json('expected_query.json')

    actual_query = None

    async def _function(
            context: stq_context.Context, query: forward_entries.Query,
    ):
        del context  # unused
        nonlocal actual_query
        actual_query = query

    actual_results = await handler.handle(
        stq3_context, af_decision_doc, _function,
    )
    assert actual_query == expected_query
    assert actual_results is None
