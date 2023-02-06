from __future__ import annotations

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import create_order_subvention_support_info
from billing_functions.repositories import support_info
from billing_functions.stq.pipelines._cargo_claim import (
    create_subvention_support_info as handler,
)


@pytest.mark.parametrize(
    'test_data_json',
    ['has_subvention_and_discount.json', 'no_subvention_no_discount.json'],
)
@pytest.mark.json_obj_hook(
    Query=create_order_subvention_support_info.Query, Doc=docs.Doc,
)
@pytest.mark.now('2022-04-13T00:00:00+00:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['cargo_claim']
    data = models.CargoClaim.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)

    actual_query = None

    async def _function(
            support_info_repo: support_info.Repository,
            query: create_order_subvention_support_info.Query,
    ):
        del support_info_repo  # unused
        nonlocal actual_query
        actual_query = query

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results is None
