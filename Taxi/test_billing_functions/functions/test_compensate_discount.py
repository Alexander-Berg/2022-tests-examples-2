import pytest

from billing_models.generated import models
from billing_models.generated.models import park_commission

from billing_functions.functions import compensate_discount
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.parametrize(
    'test_data_json',
    [
        'paid.json',
        'netted.json',
        'cargo_paid.json',
        'cargo_netted.json',
        'is_zero.json',
        'is_mqc.json',
        'need_dispatcher_acceptance.json',
        'unsuccessful_order.json',
        'no_marketing_contract.json',
        'disabled_by_tags.json',
    ],
)
@pytest.mark.json_obj_hook(
    Query=compensate_discount.Query,
    Contract=compensate_discount.Query.Contract,
    DiscountCompensation=equatable.codegen(models.DiscountCompensation),
    DiscountPayment=models.DiscountPayment,
    Money=models.Money,
    ParkCommissionRule=park_commission.BaseParkCommissionRule,
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'subvention/paid': 137,
        'subvention/netted': 111,
        'cargo_subvention/paid': 1164,
        'cargo_subvention/netted': 1161,
    },
)
async def test_compensate_discount(
        test_data_json, *, load_py_json, stq3_context,
):
    test_data = load_py_json(test_data_json)
    results = await compensate_discount.execute(
        mocks.Cities(test_data['cities'], {}),
        mocks.CurrencyRates(test_data['currency_rates']),
        stq3_context.service_ids,
        test_data['query'],
    )
    assert results == test_data['expected_results']
