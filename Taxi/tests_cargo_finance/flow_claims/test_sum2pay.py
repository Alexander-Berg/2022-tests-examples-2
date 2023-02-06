import pytest


@pytest.mark.parametrize(
    'event_id',
    [
        pytest.param('status_updated_1', id='no_sum_at_the_beginning'),
        pytest.param('status_updated_5', id='no_sum_before_contractor'),
        pytest.param(
            'contractor_billing_context_1', id='hold_when_contractor_known',
        ),
        pytest.param('status_updated_10', id='can_clear_when_finished'),
        pytest.param(
            'price_recalculated_123', id='change_sum_when_price_recaculated',
        ),
        pytest.param('pricing_billing_context_1', id='send_calc_id'),
        pytest.param('status_updated_11', id='finally_only_revision_changed'),
        pytest.param('taxi_order_billing_context_1', id='had_taxi_context'),
    ],
)
async def test_sum2pay_agains_events(
        get_events_up_to, get_expected_sum2pay, get_sum2pay, event_id,
):
    events = get_events_up_to('flow_claims/events.json', event_id)
    result = await get_sum2pay(events)
    expected = get_expected_sum2pay(
        'flow_claims/expected_sum2pays.json', event_id,
    )
    assert result == expected


async def test_s2p_taxi_billing_event(load_json, get_sum2pay):
    events = load_json('flow_claims/events.json')
    for event in events:
        if event['event_id'] == 'claim_billing_context_1':
            event['payload']['data']['has_billing_event_feature'] = True

    result = await get_sum2pay(events)
    expected_data = load_json('flow_claims/s2p_taxi_event.json')

    assert result['taxi']['taxi_event'] == expected_data


async def test_s2p_billing_cargo_claim(load_json, get_sum2pay):
    events = load_json('flow_claims/events.json')
    for event in events:
        if event['event_id'] == 'claim_billing_context_1':
            event['payload']['data'][
                'has_using_cargo_pipelines_feature'
            ] = True

    result = await get_sum2pay(events)
    expected_data = load_json('flow_claims/s2p_billing_cargo_claim.json')

    assert result['taxi']['claims_agent_payments'] == expected_data


@pytest.fixture(name='get_sum2pay')
def _get_sum2pay(request_sum2pay, claim_id):
    async def wrapper(events):
        response = await request_sum2pay(claim_id, events)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_sum2pay')
def _request_sum2pay(taxi_cargo_finance):
    url = '/internal/cargo-finance/flow/claims/func/sum2pay'

    async def wrapper(claim_id, events):
        params = {'claim_id': claim_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        return response

    return wrapper
