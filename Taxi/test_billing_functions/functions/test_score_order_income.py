import pytest

from billing_models.generated import models

from billing_functions.functions import score_order_income
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json',
    (
        'successful_order.json',
        'driver_fix.json',
        'paid_cancel.json',
        'unsuccessful_order.json',
        'corp_order_no_park_corp_vat.json',
    ),
)
@pytest.mark.json_obj_hook(
    # query
    Query=score_order_income.Query,
    Order=score_order_income.Query.Order,
    OrderIncome=equatable.codegen(models.OrderIncome),
    Money=models.Money,
)
async def test_score_order_income(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    results = score_order_income.execute(test_data['query'])
    assert results == test_data['expected_results']
