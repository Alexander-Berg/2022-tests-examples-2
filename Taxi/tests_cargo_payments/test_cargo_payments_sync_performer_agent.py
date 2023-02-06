async def test_agent_is_not_blocked(
        state_agent_unblocked, default_ibox_id, mock_web_api_agent_update,
):
    """
        Check agent is unblocked on order start.
    """
    await state_agent_unblocked()

    assert not mock_web_api_agent_update.agent_statuses[
        default_ibox_id
    ].is_blocked


async def test_agent_is_blocked_on_reorder(
        state_agent_unblocked,
        get_payment_performer,
        stq_runner,
        set_payment_performer,
        default_ibox_id,
        mock_web_api_agent_update,
        new_park_id='parkid2',
        new_driver_id='driverid2',
        new_agent_ibox_id=11112,
):
    """
        Check agent is blocked after reorder start.
    """
    state = await state_agent_unblocked()

    performer = get_payment_performer(state.payment_id)

    # new performer_version, update performer
    await set_payment_performer(
        payment_id=state.payment_id,
        park_id=new_park_id,
        driver_id=new_driver_id,
        performer_version=performer.performer_version + 1,
    )

    # Check old performer's agent is disabled
    await stq_runner.cargo_payments_sync_performer_agent.call(
        task_id='test',
        kwargs={
            'payment_id': state.payment_id,
            'park_id': state.performer.park_id,
            'driver_id': state.performer.driver_id,
            'performer_version': 0,
        },
    )
    assert mock_web_api_agent_update.agent_statuses[default_ibox_id].is_blocked

    # Check new performer's agent is active
    await stq_runner.cargo_payments_sync_performer_agent.call(
        task_id='test',
        kwargs={
            'payment_id': state.payment_id,
            'park_id': new_park_id,
            'driver_id': new_driver_id,
            'performer_version': 0,
        },
    )
    assert not mock_web_api_agent_update.agent_statuses[
        new_agent_ibox_id
    ].is_blocked


async def test_web_api_update(
        state_agent_unblocked, mock_web_api_agent_update,
):
    """
        Check web-api update request.
    """
    await state_agent_unblocked()

    assert mock_web_api_agent_update.last_request.json == {'State': 1}
    assert mock_web_api_agent_update.last_pos_id == '11111'


async def test_deactivation_disabled(
        state_performer_found,
        mock_web_api_agent_update,
        exp_cargo_payments_sync_performer_agent,
        stq_runner,
):
    """
        Check deactivation is disabled by exp.
    """
    state = await state_performer_found()

    await exp_cargo_payments_sync_performer_agent(enabled=False)

    mock_web_api_agent_update.handler.flush()
    await stq_runner.cargo_payments_sync_performer_agent.call(
        task_id='test',
        kwargs={
            'payment_id': state.payment_id,
            'park_id': state.performer.park_id,
            'driver_id': state.performer.driver_id,
            'performer_version': 0,
        },
    )
    assert not mock_web_api_agent_update.handler.times_called
