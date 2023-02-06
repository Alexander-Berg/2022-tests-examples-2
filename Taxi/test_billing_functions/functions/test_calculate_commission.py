import pytest

from billing_models.generated.models import park_commission
from testsuite.utils import ordered_object

from billing_functions.functions import calculate_commission
from billing_functions.functions.core.commissions import call_center
from test_billing_functions import mocks


@pytest.mark.parametrize(
    'test_data_json',
    (
        'driver_fix_mode.json',
        'mqc.json',
        'happy_path.json',
        'cargo.json',
        'with_driver_promocode.json',
        'with_driver_workshift.json',
        'with_promocode_and_rebate.json',
        'with_rebate.json',
        'no_billing_client_id_zone.json',
        'call_center_with_cost.json',
        'ignore_driver_promocode.json',
        'not_billable.json',
        'zero_cost_old.json',
        'zero_cost_new.json',
        'expired_new.json',
        'need_dispatcher_acceptance.json',
    ),
)
@pytest.mark.json_obj_hook(
    Query=calculate_commission.Query,
    Contract=calculate_commission.Query.Contract,
    Driver=calculate_commission.Query.Driver,
    Order=calculate_commission.Query.Order,
    DriverPromocode=calculate_commission.Query.DriverPromocode,
    HiringInfo=calculate_commission.Query.Driver.HiringInfo,
    ParkCommissionRule=park_commission.OrderParkCommissionRule,
    CallCenter=call_center.CallCenter,
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'commission/card': 128,
        'commission/cash': 111,
        'cargo_commission/card': 1163,
        'cargo_commission/cash': 1161,
    },
    BILLING_FUNCTIONS_CREATE_COMMISSION_SUPPORT_INFO_DOC=True,
)
async def test_calculate_commission(
        test_data_json,
        *,
        load_py_json,
        stq3_context,
        mock_billing_commissions,
):
    test_data = load_py_json(test_data_json)
    support_info_items_to_save = test_data['support_info_items_to_save']

    billing_commissions = mock_billing_commissions(
        agreements=load_py_json('agreements.json'),
    )
    support_info_repo_mock = mocks.SupportInfo()
    commission = await calculate_commission.execute(
        mocks.CurrencyRates(test_data['currency_rates']),
        stq3_context.service_ids,
        stq3_context.commission_agreements,
        support_info_repo_mock,
        test_data['query'],
    )

    actual = commission.serialize()
    expected = test_data['expected']
    ordered_object.assert_eq(
        actual.pop('fee', {}).pop('items', []),
        expected.pop('fee', {}).pop('items', []),
        ['', 'group'],
    )
    assert actual == expected
    if support_info_items_to_save:
        assert len(support_info_repo_mock.queries) == 1
        actual_info = support_info_repo_mock.queries[0]
        expected_info = support_info_items_to_save
        ordered_object.assert_eq(
            actual_info,
            expected_info,
            ['', 'data.agreements', 'data.agreements.kind', 'kind'],
        )
    else:
        assert not support_info_repo_mock.queries

    actual_billing_types = [
        r['billing_type'] for r in billing_commissions.rules_match_requests
    ]
    assert actual_billing_types == test_data['expected_billing_types']
