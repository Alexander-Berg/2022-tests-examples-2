import datetime

import pytest

from tests_ivr_dispatcher import utils


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='clause_not_matched.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_not_matched(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
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

    assert stq.ivr_sms_sending.times_called == 1  # newbie


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='clause_matched_but_not_enabled.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_matched_disabled(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
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

    assert stq.ivr_sms_sending.times_called == 1  # newbie


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='clause_matched.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_matched(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
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

    assert stq.ivr_sms_sending.times_called == 2  # newbie
    args = stq.ivr_sms_sending.next_call()  # see on first
    args = args['kwargs']
    assert 'Через' in args['text']


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='override_text.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_matched_override(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
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

    assert stq.ivr_sms_sending.times_called == 2  # newbie
    args = stq.ivr_sms_sending.next_call()  # see on first
    args = args['kwargs']
    assert 'Условия' in args['text']


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.experiments3(filename='test_eta.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_eta(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
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

    assert stq.ivr_sms_sending.times_called == 2  # newbie
    args = stq.ivr_sms_sending.next_call()  # see on first
    assert args['eta'] == datetime.datetime(2019, 1, 1, 0, 0, 10, 0)


@pytest.mark.pgsql('ivr_api', files=['fill_notification_in_order.sql'])
@pytest.mark.filldb(
    callcenter_newbies='empty', ivr_disp_order_events='one_event',
)
@pytest.mark.parametrize(
    ('event', 'will_extra_be_sent'),
    (('handle_driving', False), ('handle_waiting', True)),
)
@pytest.mark.experiments3(filename='policy_unique_for_event.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:01')
async def test_unique_for_event(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
        will_extra_be_sent,
        event,
):

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': event,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 3, 0, 1, 0),
        },
    )

    assert stq.ivr_sms_sending.times_called == 1 + int(will_extra_be_sent)


@pytest.mark.pgsql('ivr_api', files=['fill_notification_in_order.sql'])
@pytest.mark.filldb(
    callcenter_newbies='empty', ivr_disp_order_events='one_event',
)
@pytest.mark.parametrize(
    ('event', 'will_extra_be_sent'),
    (('handle_driving', False), ('handle_waiting', False)),
)
@pytest.mark.experiments3(filename='policy_unique_for_order.json')
@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:01')
async def test_unique_for_order(
        mongodb,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        mock_driver_profiles,
        mock_cars_catalog,
        taxi_ivr_dispatcher,
        mock_fleet_parks,
        mock_tariffs,
        mock_octonode,
        load_json,
        mock_clck,
        stq,
        mock_personal,
        mock_user_api,
        mock_order_core,
        will_extra_be_sent,
        event,
):

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': event,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 3, 0, 1, 0),
        },
    )

    assert stq.ivr_sms_sending.times_called == 1 + int(will_extra_be_sent)
