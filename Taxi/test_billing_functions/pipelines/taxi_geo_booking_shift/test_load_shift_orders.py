import asyncio
from unittest import mock

import pytest

import billing.docs.service as docs
from billing_models.generated import models

from billing_functions.functions import load_shift_orders
from billing_functions.stq.pipelines._taxi_geo_booking_shift import (
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
    Data=lambda **kwargs: models.TaxiGeoBookingShift.deserialize(kwargs),
)
async def test(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    expected_result = models.ShiftOrders(order_ids=['1', '2'], count=2)

    future = asyncio.Future()
    future.set_result(expected_result)
    func = mock.Mock(spec=load_shift_orders.execute, return_value=future)
    result = await handler.handle(stq3_context, test_data['doc'], func)
    assert result == expected_result
    assert func.call_args_list == [
        mock.call(stq3_context.journal, test_data['expected_query']),
    ]
