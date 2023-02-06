import datetime

import bson
import pytest

from tests_ivr_dispatcher import utils

ON_ASSIGNED_SMS_AZ = {
    'intent': 'taxi_intent',
    'personal_phone_id': '9cc9e88b3aec4e699eb19c1cd54f23bc',
    'sender': 'taxi_sender',
    'text': 'AZ: blue_az Audi A8 A666MP77\nIn a few minutes_az\n+79998887766',
}


def _fetch_newbie(mongodb, phone_id):
    return mongodb.callcenter_newbies.find_one(
        {'_id': bson.ObjectId(phone_id)},
    )


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_FORCE_SEND_SMS_INSTEAD_OF_CALL=True,
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_force_sms_enabler_workflow(
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
    # send sms
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_FORCE_SEND_SMS_INSTEAD_OF_CALL=True,
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_force_sms_workflow(
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
        mockserver,
        load_json,
        stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['application'] = 'arm_call_center'
        return response

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
    # send sms
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1


@pytest.mark.filldb(callcenter_newbies='empty')
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEWBIES_TTL_BY_APPLICATION={
        '__default__': 15811200,  # try to test __default__
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_newbie_workflow(
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
    assert _fetch_newbie(mongodb, utils.DEFAULT_PHONE_ID) is None
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
    # send sms
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1

    newbie = _fetch_newbie(mongodb, utils.DEFAULT_PHONE_ID)
    assert newbie
    assert newbie.get('applications')
    assert newbie['applications'].get('call_center')
    assert newbie['applications']['call_center'] == datetime.datetime(
        2019, 1, 1, 0, 0, 0, 0,
    )


@pytest.mark.filldb(callcenter_newbies='old_user')
@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_DISPATCHER_NEWBIES_TTL_BY_APPLICATION={
        '__default__': 15811200,  # try to test __default__
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_old_newbie(
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
    assert _fetch_newbie(mongodb, utils.DEFAULT_PHONE_ID)
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
    # send sms
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1

    newbie = _fetch_newbie(mongodb, utils.DEFAULT_PHONE_ID)
    assert newbie
    assert newbie.get('applications')
    assert newbie['applications'].get('call_center')
    assert newbie['applications']['call_center'] == datetime.datetime(
        2019, 1, 1, 0, 0, 0, 0,
    )


ALTERNATIVE_PHONE_ID = utils.DEFAULT_PHONE_ID[:-1] + '1'


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_status_flow_az(
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
        mockserver,
        load_json,
        stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['application'] = 'uber_az_call_center'
        return response

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_status_call.call(
        task_id=utils.DEFAULT_STQ_TASK_ID,
        kwargs={
            'order_id': utils.DEFAULT_ORDER_ID,
            'event_key': utils.ON_ASSIGNED,
            'event_reason': None,
            'event_index': 0,
            'event_created': datetime.datetime(2019, 1, 1, 0, 0, 0, 0),
        },
    )
    # create session
    assert not mock_octonode.octonode.times_called  # call
    assert stq.ivr_sms_sending.times_called == 1

    args = stq.ivr_sms_sending.next_call()
    args = args['kwargs']
    assert args['text'] == ON_ASSIGNED_SMS_AZ['text']


@pytest.mark.config(
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
    IVR_FORCE_SEND_SMS_INSTEAD_OF_CALL=True,
    IVR_DISPATCHER_SMS_SENDING_SETTINGS={
        '__default__': {
            'max_attempts': 1,
            'sleep_period': 1,
            'hanged_cutoff': 30,
            'eta': 10,
        },
    },
)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_eta(
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
        mockserver,
        load_json,
        stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order']['application'] = 'arm_call_center'
        return response

    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _retrieve_personal_id(request):
        data = request.json
        return {
            'id': data['id'],
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
        }

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
    # send sms
    assert not mock_octonode.octonode.times_called
    assert stq.ivr_sms_sending.times_called == 1
    args = stq.ivr_sms_sending.next_call()
    assert args['eta'] == datetime.datetime(2019, 1, 1, 0, 0, 10, 0)
