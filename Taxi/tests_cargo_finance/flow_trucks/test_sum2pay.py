import pytest


@pytest.mark.parametrize(
    'event_id',
    [
        pytest.param('dummy_init', id='dummy_init'),
        pytest.param('pay_shipping_contract_1', id='no_sum_at_the_beginning'),
        pytest.param('trucks_order_billing_context_1', id='first_sum2pay'),
        pytest.param(
            'pay_shipping_contract_2',
            id='no_sum_after_contract_version_changed',
        ),
        pytest.param(
            'trucks_order_billing_context_2',
            id='no_sum_cause_no_accurate_billing_context_version',
        ),
        pytest.param('trucks_order_billing_context_3', id='second_sum2pay'),
    ],
)
async def test_sum2pay_agains_events(
        get_events_up_to, get_expected_sum2pay, get_sum2pay, event_id,
):
    events = get_events_up_to('flow_trucks_events.json', event_id)
    result = await get_sum2pay(events)
    expected = get_expected_sum2pay('expected_sum2pays.json', event_id)
    assert result == expected


@pytest.fixture(name='get_sum2pay')
def _get_sum2pay(request_sum2pay):
    async def wrapper(events):
        response = await request_sum2pay(events)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_sum2pay')
def _request_sum2pay(taxi_cargo_finance, trucks_order_id):
    url = '/internal/cargo-finance/flow/trucks/func/sum2pay'

    async def wrapper(events):
        params = {'trucks_order_id': trucks_order_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper
