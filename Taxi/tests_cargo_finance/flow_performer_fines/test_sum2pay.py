import pytest


@pytest.mark.parametrize(
    'event_id, events_source_path',
    [
        pytest.param('1_request', 'processing_events.json', id='last_event'),
        pytest.param(
            '1_request_cancel', 'cancelled_fine_events.json', id='cancel',
        ),
    ],
)
async def test_sum2pay_events(
        get_events_up_to,
        get_expected_sum2pay,
        get_sum2pay,
        event_id,
        get_event,
        events_source_path,
):
    context = get_event('order_billing_context', path=events_source_path)[
        'payload'
    ]['data']
    events = get_events_up_to(events_source_path, event_id)
    result = await get_sum2pay(events, context)
    expected = get_expected_sum2pay('expected_sum2pays.json', event_id)
    assert result == expected


@pytest.fixture(name='get_sum2pay')
def _get_sum2pay(request_sum2pay):
    async def wrapper(events, order_context):
        response = await request_sum2pay(events, order_context)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_sum2pay')
def _request_sum2pay(taxi_cargo_finance, trucks_order_id):
    url = '/internal/cargo-finance/flow/performer/fines/func/sum2pay'

    async def wrapper(events, order_context):
        params = {'taxi_alias_id': 'alias_id_1'}
        data = {
            'operation_id': '1',
            'events': events,
            'order_context': order_context,
        }
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper
