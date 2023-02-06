import pytest


async def test_not_found(request_applying_state):
    response = await request_applying_state('claims', 'unknown-id')
    assert response.status_code == 404


async def test_applying_state_example(
        load_json,
        inject_clear_sum,
        inject_paid_less,
        state_after_first_run,
        inject_transactions_in_progress,
        state_after_second_run,
):
    assert state_after_second_run == load_json('applying_state_example.json')


async def test_run_wont_fail_when_not_found(run_applying_stq):
    await run_applying_stq()


def test_setting_sum2pay_calls_stq(state_just_created, stq):
    assert stq.cargo_finance_pay_applying.times_called == 1


async def test_do_nothing_without_sum(
        state_just_created,
        run_applying_stq,
        flush_all,
        get_applying_state,
        stq,
        mock_procaas_create,
        mock_upsert,
        mock_debt,
        mock_retrieve,
):
    flush_all()
    await run_applying_stq()
    new_state = await get_applying_state()

    # state has not been changed
    assert state_just_created == new_state

    # no calls
    assert not mock_procaas_create.has_calls
    assert not mock_upsert.has_calls
    assert not mock_debt.has_calls
    assert not mock_retrieve.has_calls
    assert not stq.cargo_finance_pay_applying.has_calls


async def test_pay_debt_404(request_change_card, new_card):
    response = await request_change_card('unknown_claim_id', new_card)
    assert response.status_code == 404


def test_change_card(
        state_after_request_change_card,
        mock_procaas_create,
        procaas_extract_token,
        stq,
        claim_id,
        new_card,
):
    assert not stq.cargo_finance_pay_applying.has_calls
    assert not state_after_request_change_card['force_upsert']

    requested_sum2pay = state_after_request_change_card['requested_sum2pay']
    expected_token = 'new_card/{}'.format(requested_sum2pay['revision'])

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order/')
    assert request.query == {'item_id': 'claims/{}'.format(claim_id)}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'new_card', 'data': {'new_card': new_card}}


def test_pay_debt_with_same_card(
        state_after_request_change_old_card, mock_procaas_create, stq,
):
    assert not mock_procaas_create.has_calls
    assert stq.cargo_finance_pay_applying.times_called == 1
    assert state_after_request_change_old_card['force_upsert']


def test_upsert_call(state_after_unfinished_hold, mock_upsert, claim_id):
    assert mock_upsert.times_called == 1
    request = mock_upsert.next_call()['request']
    assert request.query == {'flow': 'claims', 'entity_id': claim_id}
    assert request.json == state_after_unfinished_hold['applying_sum2pay']


async def test_retrieve_call(
        state_after_unfinished_hold,
        flush_all,
        run_applying_stq,
        get_applying_state,
        mock_retrieve,
        claim_id,
):
    # second time retrieve must be called
    flush_all()
    await run_applying_stq()
    state = await get_applying_state()

    assert mock_retrieve.times_called == 1
    request = mock_retrieve.next_call()['request']
    assert request.query == {'flow': 'claims', 'entity_id': claim_id}
    assert request.json == state['applying_sum2pay']


def test_debt_call(state_after_call_debt, mock_debt, claim_id):
    assert state_after_call_debt['using_debt_collector']

    assert mock_debt.times_called == 1
    request = mock_debt.next_call()['request']
    assert request.query == {'flow': 'claims', 'entity_id': claim_id}
    assert request.json == state_after_call_debt['requested_sum2pay']


def test_call_upsert_until_real_debt(
        state_price_changed_after_clear, mock_upsert, mock_debt,
):
    assert not mock_debt.has_calls
    assert mock_upsert.times_called == 1


def test_notify_order_cycle(
        state_after_held, mock_procaas_create, procaas_extract_token, claim_id,
):
    # incremented during writing result to database
    # so we need value before increment
    counter_value = state_after_held['notification_revision'] - 1

    expected_token = 'payment_result/{}'.format(counter_value)

    assert mock_procaas_create.times_called == 2
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_claims_payments')
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {
        'kind': 'payment_result',
        'data': {'is_paid': True},
    }


def test_notify_payment_cycle(
        state_after_held, mock_procaas_create, procaas_extract_token, claim_id,
):
    # incremented during writing result to database
    # so we need value before increment
    counter_value = state_after_held['final_paid_sum_revision'] - 1

    expected_token = 'debt_sum_changed/{}'.format(counter_value)

    assert mock_procaas_create.times_called == 2
    request = mock_procaas_create.next_call()['request']
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order')
    assert request.query == {'item_id': 'claims/{}'.format(claim_id)}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {
        'kind': 'debt_sum_changed',
        'data': {'order_sum': '850.12', 'paid_sum': '850.12'},
    }


def test_skip_order_cycle_notify_if_not_finished(
        state_after_unfinished_hold, mock_procaas_create,
):
    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.json['kind'] == 'debt_sum_changed'


def test_skip_notify_if_payment_result_not_changed(
        state_after_clear_finished, mock_procaas_create,
):
    assert mock_procaas_create.times_called == 0


def test_notify_when_payment_result_changed(
        state_after_paid_less_on_clear, mock_procaas_create, claim_id,
):
    assert mock_procaas_create.times_called == 2
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_claims_payments')
    assert request.query == {'item_id': claim_id}
    assert request.json == {
        'kind': 'payment_result',
        'data': {'is_paid': False},
    }

    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_pay_order')
    assert request.query == {'item_id': 'claims/{}'.format(claim_id)}
    assert request.json == {
        'kind': 'debt_sum_changed',
        'data': {'order_sum': '1100.00', 'paid_sum': '850.12'},
    }


def test_paid_more_is_not_a_debt(
        state_after_paid_more_on_clear, mock_procaas_create,
):
    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.json['kind'] == 'debt_sum_changed'


def test_reschedule_stq_if_got_debt(state_after_paid_less_on_clear, stq):
    assert stq.cargo_finance_pay_applying.times_called == 1


def test_reschedule_stq_if_got_new_sum2pay(
        state_after_unfinished_hold,
        inject_clear_sum,
        inject_paid,
        state_after_second_run,
        stq,
):
    assert stq.cargo_finance_pay_applying.times_called == 1


def test_skip_rescheduling_otherwise(
        state_after_unfinished_hold, inject_paid, state_after_second_run, stq,
):
    assert not stq.cargo_finance_pay_applying.times_called


async def test_apply_compensation(
        state_after_compensation, mock_upsert, mock_debt,
):
    assert not mock_debt.has_calls
    assert mock_upsert.times_called == 1
    request = mock_upsert.next_call()['request']
    assert request.json == state_after_compensation['requested_sum2pay']


async def test_apply_compensation_after_debt(
        state_after_debt_compensation, mock_upsert, mock_debt, claim_id,
):
    assert not mock_upsert.has_calls
    assert mock_debt.times_called == 1
    request = mock_debt.next_call()['request']
    assert request.query == {'flow': 'claims', 'entity_id': claim_id}
    assert request.json == state_after_debt_compensation['requested_sum2pay']

    assert state_after_debt_compensation['applied_sum2pay_revision'] == 4
    assert 'applying_sum2pay' not in state_after_debt_compensation
    assert state_after_debt_compensation['final_result'] == {
        'client': {
            'agent': {'is_finished': True, 'paid_sum': '99'},
            'compensation': {'is_finished': True, 'paid_sum': '751.12'},
        },
    }


async def test_compensation_in_progress(
        state_after_compensation_in_progress, mock_debt, claim_id,
):
    assert (
        state_after_compensation_in_progress['applied_sum2pay_revision'] == 3
    )
    assert state_after_compensation_in_progress['applying_result'] == {
        'client': {
            'agent': {'is_finished': True, 'paid_sum': '99'},
            'compensation': {'is_finished': False, 'paid_sum': '0'},
        },
    }


#  #############################
#  System states with injections


@pytest.fixture(name='state_just_created')
async def _state_just_created(
        load_json, set_applying_sum2pay, get_applying_state,
):
    await set_applying_sum2pay(load_json('sum2pay_no_sum.json'))
    return await get_applying_state()


@pytest.fixture(name='state_after_first_run')
async def _state_after_first_run(
        flush_all, run_applying_stq, get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='state_after_second_run')
async def _state_after_second_run(
        state_after_first_run, flush_all, run_applying_stq, get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='state_after_unfinished_hold')
def _state_after_unfinished_hold(
        inject_hold_sum,
        inject_transactions_in_progress,
        state_after_first_run,
):
    return state_after_first_run


@pytest.fixture(name='state_after_held')
def _state_after_held(
        state_after_unfinished_hold, inject_paid, state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_after_clear_finished')
def _state_after_clear_finished(
        inject_hold_sum,
        inject_paid,
        state_after_first_run,
        inject_clear_sum,
        state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_after_paid_less_on_clear')
def _state_after_paid_less_on_clear(
        inject_hold_sum,
        inject_paid,
        state_after_first_run,
        inject_increased_clear_sum,
        state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_after_paid_more_on_clear')
def _state_after_paid_more_on_clear(
        inject_hold_sum,
        inject_paid,
        state_after_first_run,
        inject_clear_sum,
        inject_paid_more,
        state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_after_call_debt')
def _state_after_call_debt(
        inject_clear_sum,
        inject_paid_less,
        state_after_first_run,
        state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_price_changed_after_clear')
def _state_price_changed_after_clear(
        inject_clear_sum,
        inject_paid,
        state_after_first_run,
        inject_increased_clear_sum,
        state_after_second_run,
):
    return state_after_second_run


@pytest.fixture(name='state_after_request_change_card')
async def _state_after_request_change_card(
        state_after_call_debt,
        get_applying_state,
        flush_all,
        change_card,
        new_card,
):
    flush_all()
    await change_card(new_card)
    return await get_applying_state()


@pytest.fixture(name='state_after_request_change_old_card')
async def _state_after_request_change_old_card(
        state_after_call_debt,
        get_applying_state,
        flush_all,
        change_card,
        old_card,
):
    flush_all()
    await change_card(old_card)
    return await get_applying_state()


@pytest.fixture(name='inject_hold_sum')
async def _inject_hold_sum(load_json, set_applying_sum2pay):
    sum2pay = load_json('sum2pay_can_hold.json')
    await set_applying_sum2pay(sum2pay)


@pytest.fixture(name='inject_clear_sum')
async def _inject_clear_sum(load_json, set_applying_sum2pay):
    sum2pay = load_json('sum2pay_can_hold.json')
    sum2pay['revision'] += 1
    sum2pay['is_service_complete'] = True
    await set_applying_sum2pay(sum2pay)


@pytest.fixture(name='inject_increased_clear_sum')
async def _inject_increased_clear_sum(load_json, set_applying_sum2pay):
    sum2pay = load_json('sum2pay_can_hold.json')
    sum2pay['revision'] += 2
    sum2pay['is_service_complete'] = True
    sum2pay['client']['agent']['sum'] = '1100.00'
    await set_applying_sum2pay(sum2pay)


@pytest.fixture(name='inject_compensation')
async def _inject_compensation(load_json, set_applying_sum2pay):
    sum2pay = load_json('sum2pay_can_hold.json')
    sum2pay['revision'] += 2
    sum2pay['client']['compensation'] = load_json(
        'sum2pay_compensation_context.json',
    )
    await set_applying_sum2pay(sum2pay)


@pytest.fixture(name='state_after_compensation')
async def _state_after_compensation(
        state_after_clear_finished,
        inject_compensation,
        inject_paid_compensated,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='state_after_debt_compensation')
async def _state_after_debt_compensation(
        state_after_call_debt,
        inject_compensation,
        inject_paid_less_compensated,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


@pytest.fixture(name='state_after_compensation_in_progress')
async def _state_after_compensation_in_progress(
        state_after_call_debt,
        inject_compensation,
        inject_paid_less_compensation_in_progress,
        flush_all,
        run_applying_stq,
        get_applying_state,
):
    flush_all()
    await run_applying_stq()
    return await get_applying_state()


#  ##############################
#  Target handlers with shortcuts


#  #################
#  External handlers
