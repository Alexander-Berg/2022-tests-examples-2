import pytest

from billing_models.generated import models

from billing_functions.functions import calculate_contract_payment
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=calculate_contract_payment.Query,
    Contract=calculate_contract_payment.Query.Contract,
    ShiftContractPayment=equatable.codegen(models.ShiftContractPayment),
    Money=models.Money,
)
@pytest.mark.parametrize('test_data_json', ['test_data.json'])
async def test_if_netted(test_data_json, *, stq3_context, load_py_json):
    test_data = load_py_json(test_data_json)
    payment = await calculate_contract_payment.execute(
        stq3_context.cities, stq3_context.currency_rates, test_data['query'],
    )
    assert payment == test_data['expected_payment']
