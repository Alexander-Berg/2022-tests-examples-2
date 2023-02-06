async def test_stq_queued(
        state_payment_confirmed, payment_authorize_2can, stq,
):
    """
        Check stq is set on different statuses.
    """
    state = await state_payment_confirmed()

    await payment_authorize_2can(payment_id=state.payment_id)

    assert stq.cargo_payments_status_callbacks.times_called == 2

    # first call on confirmed
    args = stq.cargo_payments_status_callbacks.next_call()
    assert args['kwargs']['new_status'] == 'confirmed'

    # second call on authorized
    args = stq.cargo_payments_status_callbacks.next_call()
    assert args['kwargs']['new_status'] == 'authorized'


async def test_performer_data(
        state_payment_authorized, stq_runner, get_payment_performer,
):
    """
        Check performer's data was set.
    """
    state = await state_payment_authorized()

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'authorized'},
    )

    performer = get_payment_performer(state.payment_id)

    assert performer.is_payment_finished


async def test_agent_synced(state_payment_authorized, stq_runner, stq):
    """
        Check sync agent's status was initiated (stq was set)
    """
    state = await state_payment_authorized()
    stq.cargo_payments_sync_performer_agent.flush()
    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'authorized'},
    )

    assert stq.cargo_payments_sync_performer_agent.times_called == 1
    kwargs = stq.cargo_payments_sync_performer_agent.next_call()['kwargs']
    kwargs.pop('log_extra', None)

    assert kwargs == {
        'driver_id': state.performer.driver_id,
        'park_id': state.performer.park_id,
        'payment_id': state.payment_id,
        'performer_version': 1,
    }


async def test_cargo_notified_authorized(
        state_payment_authorized, stq, stq_runner,
):
    """
        Check cargo is notified on status change.
    """
    state = await state_payment_authorized()

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'authorized'},
    )

    assert stq.cargo_payment_status_changed.times_called == 1


async def test_cargo_notified_finished(
        state_payment_finished, stq, stq_runner,
):
    """
        Check cargo is notified on status change.
    """
    state = await state_payment_finished()

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={
            'payment_id': state.payment_id,
            'new_status': 'finished',
            'invoice_link': 'invoice_link',
        },
    )

    assert stq.cargo_payment_status_changed.times_called == 1


async def test_eats_notified_on_paid(
        state_payment_authorized, stq, stq_runner,
):
    """
       Check eats is notified on status change to paid.
    """
    state = await state_payment_authorized()

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'authorized'},
    )

    assert stq.eats_payments_postpayment_callback.times_called == 1


async def test_eats_not_notified_till_paid(
        state_payment_confirmed, stq, stq_runner,
):
    """
       Check eats is notified on status change to paid.
    """
    state = await state_payment_confirmed()

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'confirmed'},
    )

    assert stq.eats_payments_postpayment_callback.times_called == 0


async def test_eats_notified_only_on_eats_order(
        state_payment_authorized,
        stq,
        stq_runner,
        exp_cargo_payments_eats_callbacks,
):
    """
       Check eats is notified only if for eats's order.
    """
    state = await state_payment_authorized()
    # make sure this payment belongs to another virtual_client
    await exp_cargo_payments_eats_callbacks(
        eats_virtual_client_id='another_virtual_client_id',
    )

    await stq_runner.cargo_payments_status_callbacks.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'new_status': 'authorized'},
    )

    assert stq.eats_payments_postpayment_callback.times_called == 0
