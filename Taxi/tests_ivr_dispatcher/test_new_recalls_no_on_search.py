import datetime

import pytest

from tests_ivr_dispatcher import utils


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_first_call(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
):
    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert mock_octonode.octonode.times_called == 1  # call
    assert stq.ivr_status_call.times_called == 1  # heartbeat
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 1, 0, 0)


@pytest.mark.pgsql('ivr_api', files=['notifications_last_call_error.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_recall_allowed(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        pgsql,
):

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert mock_octonode.octonode.times_called == 1  # recall
    assert stq.ivr_status_call.times_called == 1  # heartbeat
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 1, 0, 0)


@pytest.mark.pgsql('ivr_api', files=['notifications_last_call_error.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 2,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_recall_not_allowed_by_attempts(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        pgsql,
):

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1
    assert not stq.ivr_status_call.times_called


@pytest.mark.pgsql('ivr_api', files=['notifications_last_call_error.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 600,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_recall_need_sleep_by_originate_retry_delay(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        pgsql,
):

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called
    assert not stq.ivr_sms_sending.times_called
    assert (
        stq.ivr_status_call.times_called == 1
    )  # reschedule, cause it's too early to call
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 9, 0, 0)


@pytest.mark.pgsql('ivr_api', files=['notifications_last_call_pending.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_HANGED_CONTEXTS_CUTOFF=3000,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 600,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_last_call_in_work(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        pgsql,
):

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called
    assert not stq.ivr_sms_sending.times_called
    assert stq.ivr_status_call.times_called == 1  # heartbeat
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 1, 0, 0)


@pytest.mark.pgsql('ivr_api', files=['notifications_last_call_pending.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_HANGED_CONTEXTS_CUTOFF=30,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 600,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_last_call_hanged(
        stq_runner,
        mock_order_core,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mongodb,
        stq,
        pgsql,
):

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.HANDLE_DRIVING,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1  # hanged call
    assert not stq.ivr_status_call.times_called
