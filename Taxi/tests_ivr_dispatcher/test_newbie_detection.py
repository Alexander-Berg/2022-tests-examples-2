import datetime

import bson
import pytest

from tests_ivr_dispatcher import utils


def _fetch_newbie(mongodb, phone_id):
    return mongodb.callcenter_newbies.find_one(
        {'_id': bson.ObjectId(phone_id)},
    )


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEWBIES_TTL_BY_APPLICATION={
        '__default__': 15811200,
        utils.DEFAULT_APPLICATION: 15811200,
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_new_detection_not_newbie_by_time(
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
        stq,
):
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
    # he is not newbie
    assert mock_octonode.octonode.times_called
    assert not stq.ivr_sms_sending.times_called


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEWBIES_TTL_BY_APPLICATION={
        '__default__': 15811200,  # try to test __default__
    },
)
@pytest.mark.filldb(callcenter_newbies='old_user')
@pytest.mark.now('2019-01-01T00:00:00')
async def test_new_detection_newbie_by_time(
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
        stq,
        mock_order_core,
):
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
    # he is newbie
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called


@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        'call_center': 'common_brand',
        'some_app': 'common_brand',
    },
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEWBIES_TTL_BY_APPLICATION={'__default__': 15811200},
)
@pytest.mark.filldb(callcenter_newbies='some_app')
@pytest.mark.now('2019-01-01T00:00:00')
async def test_new_detection_newbie_by_brand(
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
        stq,
        mock_order_core,
):
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
    # he is newbie
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called
