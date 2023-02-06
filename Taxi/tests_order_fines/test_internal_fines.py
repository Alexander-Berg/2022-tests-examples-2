import datetime

from dateutil import parser as dateparser
import pytest
import pytz

ORDER_ID = 'some_order_id'


async def _check_decision(response, expected_decision):
    decision = response['decision']
    last_modified_at = decision.pop('last_modified_at')
    # Check decision payload
    assert decision == expected_decision
    # Check decision updated time
    last_modified_at = dateparser.parse(last_modified_at)
    now = datetime.datetime.now(tz=pytz.timezone('UTC'))
    assert abs(last_modified_at - now) < datetime.timedelta(minutes=10)


async def test_no_fines_without_records(get_decision):
    decision = await get_decision()
    assert decision == {'decision': {'has_fine': False}}


async def test_can_change_decisions(save_decision, get_decision):
    assert (await get_decision()) == {'decision': {'has_fine': False}}

    first_decision = {'has_fine': True, 'fine_code': 'first'}
    await save_decision(first_decision, ORDER_ID)
    await _check_decision(await get_decision(), first_decision)

    cancel_fine = {'has_fine': False}
    await save_decision(cancel_fine, ORDER_ID)
    await _check_decision(await get_decision(), cancel_fine)

    second_decision = {'has_fine': True, 'fine_code': 'second'}
    await save_decision(second_decision, ORDER_ID)
    await _check_decision(await get_decision(), second_decision)


async def test_can_save_cancel_first(save_decision, get_decision):
    await save_decision({'has_fine': False}, ORDER_ID)
    await _check_decision(await get_decision(), {'has_fine': False})


@pytest.fixture(name='get_decision')
def _get_decision(taxi_order_fines):
    async def _wrapper():
        response = await taxi_order_fines.get(
            '/internal/order/fine', params={'order_id': ORDER_ID},
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper
