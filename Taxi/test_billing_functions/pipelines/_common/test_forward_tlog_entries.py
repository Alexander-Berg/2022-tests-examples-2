from __future__ import annotations

import asyncio
from unittest import mock

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions.functions import forward_tlog_entries
from billing_functions.stq.pipelines._common import (
    forward_tlog_entries as handler,
)


@pytest.mark.json_obj_hook(
    Query=forward_tlog_entries.Query,
    Doc=docs.Doc,
    AntifraudDecision=lambda **data: models.AntifraudDecision.deserialize(
        data,
    ),
    CargoClaim=lambda **data: models.CargoClaim.deserialize(data),
    TaxiOrder=lambda **data: models.TaxiOrder.deserialize(data),
    Fine=lambda **data: models.FineOrder.deserialize(data),
    TaxiGeoBookingShift=lambda **data: models.TaxiGeoBookingShift.deserialize(
        data,
    ),
    TaxiGoalShift=lambda **data: models.TaxiGoalShift.deserialize(data),
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'taxi_order.json',
        'af_order_decision.json',
        'taxi_goal_shift.json',
        'af_goal_decision.json',
        'taxi_geo_booking_shift.json',
        'af_geo_booking_decision.json',
        'cargo_claim.json',
        'af_cargo_claim_decision.json',
        'fine.json',
    ],
)
@pytest.mark.config(BILLING_FUNCTIONS_FORWARD_TLOG_ENTRIES_MODE='new')
@pytest.mark.now('1991-06-18T07:15:00+03:00')
async def test(stq3_context, load_py_json, test_data_json):
    test_data = load_py_json(test_data_json)
    future = asyncio.Future()
    future.set_result(None)
    func = mock.Mock(spec=forward_tlog_entries.execute, return_value=future)

    await handler.handle(stq3_context, test_data['doc'], func)
    assert func.call_args_list == [
        mock.call(stq3_context, test_data['expected_query']),
    ]
