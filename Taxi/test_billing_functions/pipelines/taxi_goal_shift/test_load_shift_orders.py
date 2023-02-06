import asyncio
from unittest import mock

import pytest

import billing.docs.service as docs
from billing_models.generated import models

from billing_functions.functions import load_shift_orders
from billing_functions.stq import pipeline
from billing_functions.stq.pipelines._taxi_goal_shift import (
    load_shift_orders as handler,
)
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ['test_data.json'])
@pytest.mark.config(BILLING_FUNCTIONS_MAX_ORDER_IDS_IN_SHIFT_DOC=2)
@pytest.mark.json_obj_hook(
    Query=load_shift_orders.Query,
    Account=load_shift_orders.Query.Account,
    ShiftOrders=equatable.codegen(models.ShiftOrders),
    Doc=docs.Doc,
    Data=lambda **kwargs: models.TaxiGoalShift.deserialize(kwargs),
    Results=pipeline.Results,
)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    result = models.ShiftOrders(order_ids=['1', '2'], count=2)

    future = asyncio.Future()
    future.set_result(result)
    func = mock.Mock(spec=load_shift_orders.execute, return_value=future)
    actual_result = await handler.handle(stq3_context, test_data['doc'], func)
    assert actual_result == result
    assert func.call_args_list == [
        mock.call(stq3_context.journal, test_data['expected_query']),
    ]
