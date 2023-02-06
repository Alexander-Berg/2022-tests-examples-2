import datetime

import pytz


async def test_fresh_not_deactivated(
        state_performer_found, run_tid_deactivator, get_performer_tid_info,
):
    """
        Check job does not deactivate active performers.
    """
    state = await state_performer_found()

    await run_tid_deactivator()

    tid_info = get_performer_tid_info('parkid1', 'driverid1')
    assert tid_info['tid'] in state.default_tids


async def test_old_on_order_courier_deactivated(
        state_performer_found,
        run_tid_deactivator,
        get_performer_tid_info,
        mocked_time,
):
    """
        Check job deactivate performers without fresh orders.
    """
    now = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    await state_performer_found()

    now = datetime.datetime(2022, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    await run_tid_deactivator()

    tid_info = get_performer_tid_info('parkid1', 'driverid1')
    assert tid_info['tid'] is None
