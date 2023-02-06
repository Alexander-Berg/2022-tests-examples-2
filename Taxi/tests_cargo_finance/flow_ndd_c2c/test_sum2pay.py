import pytest


@pytest.mark.parametrize(
    'event_id',
    [
        pytest.param('payment_initiated', id='no_sum_at_the_beginning'),
        pytest.param('billing_context', id='has_context'),
        pytest.param(
            'price_recalculated_1', id='change_sum_when_price_recaculated',
        ),
        pytest.param('payment_finished', id='can_clear_when_finished'),
        pytest.param('price_recalculated_2', id='change_sum_after_clear'),
    ],
)
async def test_sum2pay_agains_events(
        get_events_up_to, get_expected_sum2pay, get_sum2pay, event_id,
):
    events = get_events_up_to('flow_ndd_c2c_events.json', event_id)
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
def _request_sum2pay(taxi_cargo_finance, ndd_order_id):
    url = '/internal/cargo-finance/flow/ndd-c2c/func/sum2pay'

    async def wrapper(events):
        params = {'ndd_order_id': ndd_order_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper
