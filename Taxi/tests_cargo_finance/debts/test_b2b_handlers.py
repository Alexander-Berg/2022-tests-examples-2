import pytest


def test_all_paid(state_all_paid, load_json):
    assert state_all_paid == load_json('state_all_paid.json')


def test_has_debts(state_has_debts, load_json):
    assert state_has_debts == load_json('state_has_debts.json')


def test_request_pay_debts_calls_stq(state_after_request_pay_debts, stq):
    assert stq.cargo_finance_debts_pay.times_called == 1


def test_have_to_wait_until_finish_of_paying_attempty(
        state_after_request_pay_debts,
):
    assert state_after_request_pay_debts['actions']['pay_debts'] == {
        'disable_reason': {
            'code': 'paying_attempt_in_progress',
            'message': 'Trying to pay for debts. Please, wait.',
            'details': {},
        },
    }


def test_cant_pay_debts_without_bound_cards(
        inject_no_bound_cards, state_has_debts, load_json,
):
    assert state_has_debts == load_json('state_no_bound_cards.json')


def test_no_debts_even_if_procedure_unfinished(
        state_debts_suddenly_disappeared, load_json,
):
    assert state_debts_suddenly_disappeared == load_json('state_all_paid.json')


@pytest.fixture(name='state_after_request_pay_debts')
async def _state_after_request_pay_debts(
        state_has_debts, get_b2b_state, pay_debts, flush_all,
):
    flush_all()
    operation_token = state_has_debts['actions']['pay_debts']['token']
    await pay_debts(operation_token)
    return await get_b2b_state()


@pytest.fixture(name='state_debts_suddenly_disappeared')
async def _state_debts_suddenly_disappeared(
        state_after_request_pay_debts,
        inject_no_debts,
        get_b2b_state,
        flush_all,
):
    flush_all()
    return await get_b2b_state()
