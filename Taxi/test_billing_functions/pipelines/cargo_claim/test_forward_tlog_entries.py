from __future__ import annotations

import asyncio
from unittest import mock

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.stq.pipelines._cargo_claim import (
    forward_tlog_entries as cargo_claim_hadler,
)
from billing_functions.stq.pipelines._common import (
    forward_tlog_entries as _common_handler,
)


@pytest.mark.json_obj_hook(
    Doc=docs.Doc,
    CargoClaim=lambda **data: models.CargoClaim.deserialize(data),
)
@pytest.mark.config(BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new')
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test_do_nothing_if_dry_run(
        stq3_context, load_py_json, test_data_json='dry_run_doc.json',
):
    test_data = load_py_json(test_data_json)
    future = asyncio.Future()
    future.set_result(None)
    handler = mock.Mock(spec=_common_handler.handle, return_value=future)

    await cargo_claim_hadler.handle(stq3_context, test_data['doc'], handler)
    assert handler.call_args_list == []
