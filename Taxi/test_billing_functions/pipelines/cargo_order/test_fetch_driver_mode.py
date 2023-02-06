from __future__ import annotations

import datetime

import pytest

from billing.docs import service as docs
from billing_models.generated import models

from billing_functions import consts
from billing_functions.functions import fetch_driver_mode_data
from billing_functions.repositories import driver_mode_settings
from billing_functions.repositories import driver_mode_subscriptions
from billing_functions.repositories import support_info
from billing_functions.stq.pipelines._cargo_order import (
    fetch_driver_mode as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.json_obj_hook(
    Query=fetch_driver_mode_data.Query,
    DriverMode=equatable.codegen(models.DriverMode),
    DriverFixModeSubscription=equatable.codegen(
        models.DriverFixModeSubscription,
    ),
    Doc=docs.Doc,
)
@pytest.mark.now('2022-04-01T00:00:00+00:00')
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    raw_doc = test_data['cargo_order']
    data = models.CargoOrder.deserialize(raw_doc.data)
    doc = docs.TypedDoc.from_doc(raw_doc, data)
    results = models.DriverMode(
        mode=consts.DriverMode.DRIVER_FIX,
        subscription=models.DriverFixModeSubscription(
            doc_id=0,
            rule_id='rule_id',
            shift_close_time='00:00:00+00:00',
            start=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        ),
    )

    actual_query = None

    async def _function(
            driver_mode_settings_repo: driver_mode_settings.Repository,
            subscriptions_repo: driver_mode_subscriptions.Repository,
            support_info_repo: support_info.Repository,
            query: fetch_driver_mode_data.Query,
    ) -> models.DriverMode:
        nonlocal actual_query
        actual_query = query
        return results

    actual_results = await handler.handle(stq3_context, doc, _function)
    assert actual_query == test_data['expected_query']
    assert actual_results == results
