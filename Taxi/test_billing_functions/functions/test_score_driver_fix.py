import pytest

from billing_functions.functions import score_driver_fix
from billing_functions.repositories import driver_fix_rules
from test_billing_functions import mocks


@pytest.mark.json_obj_hook(
    Query=score_driver_fix.Query,
    Driver=score_driver_fix.Query.Driver,
    Order=score_driver_fix.Query.Order,
    Subscription=score_driver_fix.Query.Subscription,
    # rule
    Rule=driver_fix_rules.Rule,
    RateInterval=driver_fix_rules.Rule.RateInterval,
    RateIntervalEndpoint=driver_fix_rules.Rule.RateIntervalEndpoint,
)
@pytest.mark.now('2020-03-09T00:00:00+03:00')
@pytest.mark.parametrize(
    'test_data_json',
    [
        'with_coupon_and_discounts.json',
        'without_coupon_and_discounts.json',
        'old_amended_order.json',
        'old_original_order.json',
        'start_eq_to_end.json',
    ],
)
async def test_score_driver_fix(
        test_data_json, *, load_py_json, mock_open_shift, stq3_context,
):
    test_data = load_py_json(test_data_json)

    if test_data.get('expect_raises'):
        with pytest.raises(ValueError):
            await score_driver_fix.execute(
                mocks.DriverFixRules(test_data['rule']),
                stq3_context.clients.billing_subventions,
                test_data['query'],
            )
    else:
        response = await score_driver_fix.execute(
            mocks.DriverFixRules(test_data['rule']),
            stq3_context.clients.billing_subventions,
            test_data['query'],
        )
        assert test_data['expected_response'] == response.serialize()
        assert test_data['expected_open_shift_requests'] == mock_open_shift


@pytest.fixture(name='mock_open_shift')
def _mock_open_shift(mockserver):
    requests = []

    @mockserver.json_handler('/billing_subventions/v1/shifts/open')
    def _rules_select(request):
        requests.append(request.json)
        return {'doc_id': 18061991}

    return requests
