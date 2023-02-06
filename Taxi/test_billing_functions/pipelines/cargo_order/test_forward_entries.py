from __future__ import annotations

import dataclasses

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import forward_entries
from billing_functions.generated.stq3 import stq_context
from billing_functions.stq.pipelines._cargo_order import (
    forward_entries as handler,
)


@dataclasses.dataclass(frozen=True)
class Description:
    doc: docs.Doc
    expected_query: forward_entries.Query


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.json_obj_hook(Query=forward_entries.Query, Doc=docs.Doc)
@pytest.mark.now('2022-04-01T00:00:00.000000+03:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = Description(**load_py_json(test_data_json))
    data = models.CargoOrder.deserialize(test_data.doc.data)
    doc = docs.TypedDoc.from_doc(test_data.doc, data)

    actual_query = None

    async def _function(
            context: stq_context.Context, query: forward_entries.Query,
    ) -> None:
        del context  # unused
        nonlocal actual_query
        actual_query = query

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data.expected_query
    assert actual_results is None
