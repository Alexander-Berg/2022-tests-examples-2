import pytest

FLOW = 'claims'
ENTITY_ID = 'some-claim-id'


async def test_no_compensation_before_request(calc_new_sum2pay, all_events):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event6':
            break

    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert 'compensation' not in new_sum2pay['client']


async def test_compensation_with_debt(
        calc_new_sum2pay, all_events, compensation_context,
):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event8':
            break

    compensation_context['sum'] = '249.88'
    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay['client']['compensation'] == compensation_context


async def test_zero_compensation_after_paying_debt(
        calc_new_sum2pay, all_events, compensation_context,
):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event9':
            break

    compensation_context['sum'] = '0'
    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay['client']['compensation'] == compensation_context


async def test_extra_compensation(
        calc_new_sum2pay, all_events, compensation_context,
):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event10':
            break

    compensation_context['sum'] = '100'
    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay['client']['compensation'] == compensation_context


async def test_overpayed_compensation_with_extra(
        calc_new_sum2pay, all_events, compensation_context,
):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event11':
            break

    compensation_context['sum'] = '100'
    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay['client']['compensation'] == compensation_context


async def test_declined_compensation(
        calc_new_sum2pay, all_events, compensation_context,
):
    events_to_hold = []
    for event in all_events:
        events_to_hold.append(event)
        if event['event_id'] == 'event13':
            break

    compensation_context['sum'] = '0'
    new_sum2pay = await calc_new_sum2pay(events_to_hold)
    assert new_sum2pay['client']['compensation'] == compensation_context


@pytest.fixture(name='all_events')
def _all_events(load_json):
    return load_json('cargo_finance_pay_order_events.json')


@pytest.fixture(name='compensation_context')
def _compensation_context(load_json):
    return load_json('sum2pay_compensation_context.json')


@pytest.fixture(name='calc_new_sum2pay')
def _calc_new_sum2pay(request_calc_new_sum2pay):
    async def wrapper(events):
        response = await request_calc_new_sum2pay(FLOW, ENTITY_ID, events)
        assert response.status_code == 200
        return response.json().get('new_sum2pay')

    return wrapper
