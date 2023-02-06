import pytest

from billing_models.generated import models

from billing_functions.functions import check_in_antifraud
from billing_functions.functions import wait_for_antifraud
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    CheckDriverQuery=check_in_antifraud.CheckDriverQuery,
    DriverInfo=check_in_antifraud.CheckDriverQuery.Driver,
    RuleInfo=check_in_antifraud.CheckDriverQuery.Rule,
    ShiftOrders=check_in_antifraud.CheckDriverQuery.ShiftOrders,
    CheckResponse=equatable.codegen(models.Antifraud),
    Query=wait_for_antifraud.Query,
    Response=wait_for_antifraud.Response,
)
@pytest.mark.now('2020-03-09T00:00:00+03:00')
@pytest.mark.parametrize(
    'query_json, af_response_json, response_json',
    [
        ('wait.json', 'af_pay.json', 'expected_for_wait.json'),
        ('check.json', 'af_pay.json', 'expected_for_check.json'),
        (
            'check_and_wait.json',
            'af_delay.json',
            'expected_for_check_and_wait.json',
        ),
    ],
)
async def test_wait_for_antifraud(
        query_json,
        af_response_json,
        response_json,
        *,
        load_py_json,
        load_json,
        mock_antifraud,
        stq3_context,
        patch,
):
    query = load_py_json(query_json)
    expected_response = load_py_json(response_json)
    mock_antifraud([load_json(af_response_json)])
    response = await wait_for_antifraud.execute(stq3_context, query)
    assert expected_response == response
