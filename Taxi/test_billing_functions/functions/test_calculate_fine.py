import pytest

from testsuite.utils import ordered_object

from billing_functions.functions import calculate_fine
from test_billing_functions import mocks


@pytest.mark.parametrize('test_data_json', ('cargo.json',))
@pytest.mark.json_obj_hook(
    Query=calculate_fine.Query,
    Contract=calculate_fine.Query.Contract,
    Order=calculate_fine.Query.Order,
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
async def test_calculate_fine(
        test_data_json,
        *,
        load_py_json,
        stq3_context,
        mock_billing_commissions,
):
    test_data = load_py_json(test_data_json)

    billing_commissions = mock_billing_commissions(
        agreements=load_py_json('agreements.json'),
    )
    support_info_repo_mock = mocks.SupportInfo()
    fine = await calculate_fine.execute(
        mocks.CurrencyRates(test_data['currency_rates']),
        stq3_context.service_ids,
        stq3_context.commission_agreements,
        support_info_repo_mock,
        test_data['query'],
    )
    assert [fine.serialize() for fine in fine.items] == test_data['expected']
    assert len(support_info_repo_mock.queries) == 1
    actual_info = support_info_repo_mock.queries[0]
    ordered_object.assert_eq(
        actual_info,
        test_data['support_info_items_to_save'],
        ['', 'data.agreements', 'data.agreements.kind', 'kind'],
    )

    actual_billing_types = [
        r['billing_type'] for r in billing_commissions.rules_match_requests
    ]
    assert actual_billing_types == test_data['expected_billing_types']
