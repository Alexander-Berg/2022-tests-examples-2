import pytest

FLOW = 'claims'
ENTITY_ID = 'some-claim-id'
ITEM_ID = '{}/{}'.format(FLOW, ENTITY_ID)


async def test_send_sum2pay_by_flow(
        mock_procaas_create,
        procaas_extract_token,
        request_send_sum2pay_by_flow,
        load_json,
):
    event_id = 'some-event-id'
    sum2pay = load_json('sum2pay_no_sum.json')
    response = await request_send_sum2pay_by_flow(
        FLOW, ENTITY_ID, event_id, sum2pay,
    )
    assert response.status_code == 200

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')
    assert procaas_extract_token(request) == 'flow_sum2pay/{}'.format(event_id)
    assert request.query == {'item_id': ITEM_ID}
    assert request.json == {
        'kind': 'sum2pay_calculated_by_flow',
        'data': sum2pay,
    }


async def test_calc_new_sum2pay(calc_new_sum2pay, all_events, load_json):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event2':
            break

    expected_sum2pay = load_json('sum2pay_can_hold.json')
    expected_sum2pay['revision'] = len(events_to_hold)

    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay == expected_sum2pay


async def test_calc_only_when_sum2pay_changed(calc_new_sum2pay, all_events):
    events_to_race = []
    for event in all_events:
        events_to_race.append(event)
        if event['event_id'] == 'event4':
            break

    new_sum2pay = await calc_new_sum2pay(events_to_race)
    assert new_sum2pay is None


async def test_calc_sum2pay_accounts_service_completion(
        calc_new_sum2pay, all_events, new_card, load_json,
):
    expected_sum2pay = load_json('sum2pay_complete.json')

    expected_sum2pay['is_service_complete'] = True
    expected_sum2pay['revision'] = len(all_events)

    expected_sum2pay['client']['agent']['sum'] = '300.15'
    expected_sum2pay['client']['agent']['payment_methods']['card'] = new_card

    expected_sum2pay['taxi']['taxi_event']['type'] = 'order_amended'
    expected_sum2pay['taxi']['taxi_event']['data']['cost']['amount'] = '2.2'
    expected_sum2pay['taxi']['taxi_event']['data']['cost_for_driver'] = '2.2'
    expected_sum2pay['taxi']['taxi_event']['data']['driver_cost'] = 2.2
    expected_sum2pay['taxi']['taxi_event']['data']['park_ride_sum'] = '2.2'

    new_sum2pay = await calc_new_sum2pay(all_events)
    assert new_sum2pay == expected_sum2pay


@pytest.fixture(name='calc_new_sum2pay')
def _calc_new_sum2pay(request_calc_new_sum2pay):
    async def wrapper(events):
        response = await request_calc_new_sum2pay(FLOW, ENTITY_ID, events)
        assert response.status_code == 200
        return response.json().get('new_sum2pay')

    return wrapper


@pytest.fixture(name='all_events')
def _all_events(load_json):
    return load_json('cargo_finance_pay_order_events.json')
