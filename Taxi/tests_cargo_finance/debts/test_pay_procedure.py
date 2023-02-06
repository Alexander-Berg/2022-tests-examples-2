import datetime

import pytest

LOCK_TTL_SECONDS = 120


def test_dont_pay_without_bound_card(
        state_after_run_without_bound_cards, mock_change_card,
):
    assert not mock_change_card.has_calls


def test_dont_reschedule_stq_without_bound_card(
        state_after_run_without_bound_cards, stq,
):
    assert not stq.cargo_finance_debts_pay.has_calls


def test_remove_lock_without_bound_card(state_after_binding_card):
    assert 'token' in state_after_binding_card['actions']['pay_debts']


def test_nothing_to_pay_if_no_debts(
        state_after_run_without_debts, mock_change_card,
):
    assert not mock_change_card.has_calls


def test_remove_lock_if_no_debts(state_after_new_debts):
    assert 'token' in state_after_new_debts['actions']['pay_debts']


def test_reschedule_stq_after_pay_debts(state_after_pay_debts, stq, now):
    eta = now + datetime.timedelta(seconds=LOCK_TTL_SECONDS)
    second = datetime.timedelta(seconds=1)

    assert stq.cargo_finance_debts_pay.times_called == 1
    next_call = stq.cargo_finance_debts_pay.next_call()
    assert eta - second <= next_call['eta'] <= eta + second


def test_run_in_two_minutes_just_cleanup_everything(
        state_after_cleanup, stq, mock_debt_list, mock_corp_card_list,
):
    assert not stq.cargo_finance_debts_pay.has_calls

    # just one time for get_b2b_state
    assert mock_debt_list.times_called == 1
    assert mock_corp_card_list.times_called == 1

    # can try to pay again
    assert 'token' in state_after_cleanup['actions']['pay_debts']


@pytest.fixture(name='state_lock_is_set')
async def _state_lock_is_set(
        state_has_debts, get_b2b_state, pay_debts, flush_all,
):
    operation_token = state_has_debts['actions']['pay_debts']['token']
    await pay_debts(operation_token)

    flush_all()
    new_state = await get_b2b_state()
    error_code = new_state['actions']['pay_debts']['disable_reason']['code']
    assert error_code == 'paying_attempt_in_progress'

    return new_state


@pytest.fixture(name='state_after_run_without_bound_cards')
async def _state_after_run_without_bound_cards(
        state_lock_is_set,
        inject_no_bound_cards,
        get_b2b_state,
        run_stq,
        flush_all,
):
    flush_all()
    await run_stq()
    return await get_b2b_state()


@pytest.fixture(name='state_after_binding_card')
async def _state_after_binding_card(
        state_after_run_without_bound_cards,
        inject_default_card,
        get_b2b_state,
        flush_all,
):
    flush_all()
    return await get_b2b_state()


@pytest.fixture(name='state_after_run_without_debts')
async def _state_after_run_without_debts(
        state_lock_is_set, inject_no_debts, get_b2b_state, run_stq, flush_all,
):
    flush_all()
    await run_stq()
    return await get_b2b_state()


@pytest.fixture(name='state_after_new_debts')
async def _state_after_new_debts(
        state_after_run_without_debts, set_debts, get_b2b_state, flush_all,
):
    set_debts()
    flush_all()
    return await get_b2b_state()


@pytest.fixture(name='state_after_pay_debts')
async def _state_after_pay_debts(
        state_has_debts, get_b2b_state, run_stq, flush_all,
):
    flush_all()
    await run_stq()
    return await get_b2b_state()


@pytest.fixture(name='state_after_cleanup')
async def _state_after_cleanup(
        state_after_pay_debts,
        taxi_cargo_finance,
        get_b2b_state,
        run_stq,
        flush_all,
        mocked_time,
):
    epsilon = 3  # because of lags in tests
    mocked_time.sleep(LOCK_TTL_SECONDS + epsilon)
    await taxi_cargo_finance.invalidate_caches()

    flush_all()
    await run_stq()
    return await get_b2b_state()
