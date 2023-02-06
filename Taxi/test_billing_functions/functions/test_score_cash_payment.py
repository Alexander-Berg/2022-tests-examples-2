import pytest

from billing_models.generated import models

from billing_functions.functions import score_cash_payment
from test_billing_functions import equatable


@pytest.mark.parametrize(
    'test_data_json',
    ['cash.json', 'toll_road.json', 'coupon.json', 'round.json'],
)
@pytest.mark.json_obj_hook(
    # query
    Query=score_cash_payment.Query,
    CashPayment=equatable.codegen(models.CashPayment),
)
async def test_score_cash_payment(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    results = score_cash_payment.execute(test_data['query'])
    assert results == test_data['expected_results']
