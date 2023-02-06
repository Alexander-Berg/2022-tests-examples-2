import dataclasses

import pytest

from billing_models.generated import models

from billing_functions.functions import check_in_antifraud
from test_billing_functions import equatable

TEST_DOC_ID = 18061991


@dataclasses.dataclass(frozen=True)
class Description:
    query: check_in_antifraud.Query
    af_response: dict
    expected_af_requests: list
    expected_result: models.Antifraud


@pytest.mark.parametrize(
    'test_data_json',
    [
        'check_goal_if_pay.json',
        'check_goal_if_block.json',
        'check_goal_if_delay.json',
        #
        'check_order_if_pay.json',
        'check_order_if_block.json',
        'check_order_if_delay.json',
    ],
)
@pytest.mark.json_obj_hook(
    CheckDriverQuery=check_in_antifraud.CheckDriverQuery,
    DriverInfo=check_in_antifraud.CheckDriverQuery.Driver,
    RuleInfo=check_in_antifraud.CheckDriverQuery.Rule,
    ShiftOrders=check_in_antifraud.CheckDriverQuery.ShiftOrders,
    #
    CheckOrderQuery=check_in_antifraud.CheckOrderQuery,
    CheckOrderQueryOrder=check_in_antifraud.CheckOrderQuery.Order,
    CheckOrderQueryDriver=check_in_antifraud.CheckOrderQuery.Driver,
    #
    Antifraud=equatable.codegen(models.Antifraud),
)
async def test_check_in_antifraud(
        test_data_json, *, load_py_json, mock_antifraud, stq3_context,
):
    test_data = Description(**load_py_json(test_data_json))
    mock_antifraud = mock_antifraud([test_data.af_response])
    results = await check_in_antifraud.execute(stq3_context, test_data.query)

    assert results == test_data.expected_result
    assert mock_antifraud.requests == test_data.expected_af_requests
