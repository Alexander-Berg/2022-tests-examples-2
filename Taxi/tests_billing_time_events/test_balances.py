import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'test_data_json',
    [
        'honor_rule_end.json',
        'honor_event_at_range.json',
        'honor_subscription_end.json',
    ],
)
@pytest.mark.pgsql('billing_time_events@0', files=['events.sql'])
async def test_balances(
        test_data_json, *, load_json, taxi_billing_time_events, mockserver,
):
    test_data = load_json(test_data_json)
    request = test_data['request']
    subscriptions = test_data['subscriptions']
    expected_response = test_data['expected_response']

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    def _billing_docs_v1_docs_search(_):
        return mockserver.make_response(json=subscriptions, status=200)

    response = await taxi_billing_time_events.post('v1/balances', json=request)
    response_json = response.json()
    ordered_object.assert_eq(response_json, expected_response, ['balances'])
