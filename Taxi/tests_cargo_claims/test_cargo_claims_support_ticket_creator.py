async def test_stq(
        state_controller,
        stq_runner,
        stq,
        changedestinations,
        create_segment_with_performer,
):
    changedestinations(taxi_order_id='taxi_order_id')
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickuped', fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    await stq_runner.cargo_claims_support_ticket_creator.call(
        task_id=f'{claim_id}_delay_policy_pickuped_2',
        args=[],
        kwargs={
            'claim_uuid': claim_id,
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'point_id': 2,
            'target_claim_status': 'pickuped',
        },
    )

    queue = stq.support_info_cargo_eda_callback_on_cancel
    assert queue.times_called == 1
    call = queue.next_call()
    kwargs = call['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == {
        'request_id': 'taxi_order_id_+70000000000_pd_pickuped_2',
        'driver_phone_id': '+70000000000_pd',
        'taxi_order_id': 'taxi_order_id',
    }
