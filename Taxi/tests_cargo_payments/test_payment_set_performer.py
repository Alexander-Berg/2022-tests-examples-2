import datetime

import pytz


async def test_performer_data(state_performer_found, get_payment_performer):
    """
        Check performer's data was set.
    """
    state = await state_performer_found()

    performer = get_payment_performer(state.payment_id)

    assert performer.park_id == state.performer.park_id
    assert performer.driver_id == state.performer.driver_id
    assert performer.performer_version == 1
    assert performer.segment_revision == 1
    assert not performer.is_payment_finished


async def test_agent_synced(state_performer_found, stq):
    """
        Check sync agent's status was initiated (stq was set)
    """
    state = await state_performer_found()

    assert stq.cargo_payments_sync_performer_agent.times_called == 1
    kwargs = stq.cargo_payments_sync_performer_agent.next_call()['kwargs']
    kwargs.pop('log_extra', None)

    assert kwargs == {
        'driver_id': state.performer.driver_id,
        'park_id': state.performer.park_id,
        'payment_id': state.payment_id,
        'performer_version': 1,
    }


async def test_set_performer_with_old_version(
        state_performer_found, set_payment_performer, get_payment_performer,
):
    """
        Check behavior on performer_version races.
        /set-performer for second courier may be called before/after first one.
    """
    state = await state_performer_found()

    performer = get_payment_performer(state.payment_id)

    await set_payment_performer(
        payment_id=state.payment_id,
        park_id='parkid2',
        driver_id='driverid2',
        segment_revision=performer.segment_revision - 1,
    )

    same_performer = get_payment_performer(state.payment_id)
    assert performer == same_performer


async def test_set_performer_with_new_version(
        state_performer_found,
        set_payment_performer,
        get_payment_performer,
        new_park_id='parkid2',
        new_driver_id='driverid2',
):
    """
        Check behavior on performer_version races.
        /set-performer for second courier may be called before/after first one.
    """
    state = await state_performer_found()

    performer = get_payment_performer(state.payment_id)

    # new segment_revision, update performer
    await set_payment_performer(
        payment_id=state.payment_id,
        park_id=new_park_id,
        driver_id=new_driver_id,
        segment_revision=performer.segment_revision + 1,
    )

    new_performer = get_payment_performer(state.payment_id)
    assert new_performer.park_id == new_park_id
    assert new_performer.driver_id == new_driver_id
    assert new_performer.segment_revision == performer.segment_revision + 1


async def test_previous_driver_is_synced(
        state_performer_found,
        set_payment_performer,
        get_payment_performer,
        stq,
        new_park_id='parkid2',
        new_driver_id='driverid2',
):
    """
        Check previous driver's agent will be blocked.
        This will happen on reorders.
    """
    state = await state_performer_found()

    performer = get_payment_performer(state.payment_id)

    stq.cargo_payments_sync_performer_agent.flush()
    # new performer_version, update performer
    await set_payment_performer(
        payment_id=state.payment_id,
        park_id=new_park_id,
        driver_id=new_driver_id,
        performer_version=performer.performer_version + 1,
    )
    assert stq.cargo_payments_sync_performer_agent.times_called == 2

    synced_drivers = set()
    while stq.cargo_payments_sync_performer_agent.has_calls:
        synced_drivers.add(
            stq.cargo_payments_sync_performer_agent.next_call()['kwargs'][
                'driver_id'
            ],
        )

    assert synced_drivers == {'driverid1', 'driverid2'}


async def test_tid_activated(
        state_context,
        state_performer_found,
        get_performer_tid_info,
        mocked_time,
        stq,
):
    """
        Check agent's terminal activated on new payment.
        1) tid was not stored
        2) last_order_ts is set
        3) stq cargo_payments_update_agent_tid was called
    """
    now = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    # tid is updated only for couriers with NFC
    state_context.is_diagnostics_confirmed = True

    state = await state_performer_found()

    tid_info = get_performer_tid_info('parkid1', 'driverid1')
    assert tid_info['last_order_ts'] == now

    assert stq.cargo_payments_update_agent_tid.times_called == 1
    kwargs = stq.cargo_payments_update_agent_tid.next_call()['kwargs']
    assert kwargs['ibox_login'] == state.performer.agent.login


async def test_idempotency(
        state_performer_found,
        set_payment_performer,
        get_payment_performer,
        testpoint,
):
    """
        Check handler is idempotent.
    """
    state = await state_performer_found()

    performer = get_payment_performer(state.payment_id)

    @testpoint('set_same_performer')
    def _testpoint_same_performer(data):
        pass

    # new performer_version, update performer
    await set_payment_performer(
        payment_id=state.payment_id,
        park_id=performer.park_id,
        driver_id=performer.driver_id,
        performer_version=performer.performer_version,
    )

    assert _testpoint_same_performer.has_calls
