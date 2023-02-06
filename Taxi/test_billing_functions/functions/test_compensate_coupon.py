import pytest

from billing_models.generated import models
from billing_models.generated.models import order_coupon_compensation

from billing_functions.functions import compensate_coupon
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.parametrize(
    'test_data_json',
    [
        'paid.json',
        'limited_by_order_cost.json',
        'netted.json',
        'cargo_paid.json',
        'cargo_netted.json',
        'is_mqc.json',
        'is_zero.json',
        'need_dispatcher_acceptance.json',
        'unsuccessful_order.json',
        'no_marketing_contract.json',
    ],
)
@pytest.mark.json_obj_hook(
    Query=compensate_coupon.Query,
    Contract=compensate_coupon.Query.Contract,
    CouponCompensation=equatable.codegen(
        order_coupon_compensation.CouponCompensation,
    ),
    CouponPayment=order_coupon_compensation.CouponPayment,
    Money=models.Money,
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'coupon/paid': 137,
        'coupon/netted': 111,
        'cargo_coupon/paid': 1164,
        'cargo_coupon/netted': 1161,
    },
)
async def test_compensate_coupon(
        test_data_json, *, load_py_json, stq3_context,
):
    test_data = load_py_json(test_data_json)
    results = await compensate_coupon.execute(
        mocks.Cities(test_data['cities'], {}),
        mocks.CurrencyRates(test_data['currency_rates']),
        stq3_context.service_ids,
        test_data['query'],
    )
    assert results == test_data['expected_results']
