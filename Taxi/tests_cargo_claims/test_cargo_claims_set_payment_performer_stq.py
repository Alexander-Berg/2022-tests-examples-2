from testsuite.utils import matching


async def test_happy_path(
        enable_payment_on_delivery,
        mock_payments_check_token,
        create_segment_with_performer,
        get_segment,
        stq_runner,
        mock_payment_create,
        mock_payment_set_performer,
):
    """
        Check set-performer was called.
    """
    segment_info = await create_segment_with_performer(payment_method='card')
    segment = await get_segment(segment_info.id)

    await stq_runner.cargo_claims_set_payment_performer.call(
        task_id='test',
        kwargs={
            'segment_uuid': segment_info.id,
            'segment_revision': segment['claim_revision'],
        },
    )
    assert mock_payment_set_performer.requests == [
        {
            'payment_id': matching.AnyString(),
            'performer': {'driver_id': 'driver_id1', 'park_id': 'park_id1'},
            'performer_version': 1,
            'segment_revision': 2,
        },
        {
            'payment_id': matching.AnyString(),
            'performer': {'driver_id': 'driver_id1', 'park_id': 'park_id1'},
            'performer_version': 1,
            'segment_revision': 2,
        },
    ]


async def test_non_post_payment(
        create_segment_with_performer,
        get_segment,
        stq_runner,
        mock_payment_set_performer,
):
    """
        Check set-performer was not called for
        points without post payment.
    """
    segment_info = await create_segment_with_performer()
    segment = await get_segment(segment_info.id)

    await stq_runner.cargo_claims_set_payment_performer.call(
        task_id='test',
        kwargs={
            'segment_uuid': segment_info.id,
            'segment_revision': segment['claim_revision'],
        },
    )
    assert mock_payment_set_performer.handler.times_called == 0


async def test_reschedule_revision(
        create_segment_with_performer, stq_runner, stq,
):
    """
        Check stq is rescheduled if fetched old
        revision from slave.
    """
    segment_info = await create_segment_with_performer()

    await stq_runner.cargo_claims_set_payment_performer.call(
        task_id='test',
        kwargs={'segment_uuid': segment_info.id, 'segment_revision': 100500},
    )
    assert stq.cargo_claims_set_payment_performer.times_called == 1
