import datetime

import pytest

from tests_ivr_dispatcher import utils


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180, 300, 420],
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_first_call(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert (
        not mock_octonode.octonode.times_called
    )  # on_search dont call immediately
    assert stq.ivr_status_call.times_called == 1  # reschedule itself
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 3, 0, 0)


@pytest.mark.filldb(ivr_disp_order_events='on_search_filled')
@pytest.mark.pgsql('ivr_api', files=['notifications_first_attempt_failed.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180, 300, 420],
    },
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_recall(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert mock_octonode.octonode.times_called == 1  # recall on first attempt
    assert stq.ivr_status_call.times_called == 1  # hearbeat
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 1, 0, 0)


@pytest.mark.filldb(ivr_disp_order_events='on_search_filled')
@pytest.mark.pgsql('ivr_api', files=['notifications_first_attempt_failed.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180, 300, 420],
    },
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 2,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_recall_prohibited(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_status_call.times_called == 1  # heartbeat
    assert stq.ivr_sms_sending.times_called == 1
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(2019, 1, 1, 0, 1, 0, 0)


@pytest.mark.filldb(ivr_disp_order_events='on_search_filled')
@pytest.mark.pgsql('ivr_api', files=['notifications_first_attempt_ok.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180, 300, 420],
    },
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_second_call_to_early_to_call(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert not mock_octonode.octonode.times_called == 1
    assert stq.ivr_status_call.times_called == 1  # schedule new on_search
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(
        2019, 1, 1, 0, 4, 0, 0,
    )  # must be 23:59 + 5


@pytest.mark.filldb(ivr_disp_order_events='on_search_filled')
@pytest.mark.pgsql('ivr_api', files=['notifications_first_attempt_ok.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180],
    },
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_short_wake_up_intervals_array(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert not mock_octonode.octonode.times_called == 1
    assert stq.ivr_status_call.times_called == 1  # schedule new on_search
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(
        2019, 1, 1, 0, 2, 0, 0,
    )  # must be 23:59 + 3


@pytest.mark.filldb(ivr_disp_order_events='on_search_filled')
@pytest.mark.pgsql('ivr_api', files=['notifications_first_attempt_ok.sql'])
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NOTIFY_RESCHEDULING=60,
    IVR_DISPATCHER_NEW_SEARCH_NOTIFY_CONFIG={
        'enabled': True,
        'wake_up_intervals': [180, 300, 420],
    },
    IVR_DISPATCHER_OIW_SETTINGS={
        'originate_attempts': 3,
        'originate_retry_delay': 60,
        'sufficient_speak_time': 4,
        'speed': {'__default__': 0.9, 'partner_menu': 1.0},
    },
)
@pytest.mark.now('2019-01-01T00:10:00')
async def test_second_call(
        stq_runner,
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
        mockserver,
        load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['status'] = 'pending'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()

    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': None,
            'event_reason': utils.CREATE_REASON,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    assert mock_octonode.octonode.times_called == 1
    assert stq.ivr_status_call.times_called == 1  # heartbeat
    assert not stq.ivr_sms_sending.times_called
    stq_call = stq.ivr_status_call.next_call()
    assert stq_call['eta'] == datetime.datetime(
        2019, 1, 1, 0, 11, 0, 0,
    )  # now + 1
