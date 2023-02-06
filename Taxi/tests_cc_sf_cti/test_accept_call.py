import pytest

from tests_cc_sf_cti import helpers
from tests_cc_sf_cti import ivr_notice_requests as ivr_requests


CC_FLOW = {'+74992296622': {'cc_sf_flow_name': 'default_flow'}}
CC_QUEUES = {
    'salesforce': {
        'short_number': '11111',
        'ivr_route': 'cc_sf_internal_call_route',
    },
    'support': {
        'short_number': '22222',
        'ivr_route': 'cc_sf_internal_call_route',
    },
}


async def imitate_scenario_until_forward(call_notifier: helpers.CallNotifier):
    await call_notifier.send(['answer'])
    response = await call_notifier.send(['ask'])
    assert response.json()['actions'][0]['ask']['input_mode'] == 'dtmf'
    ask_status = {
        'state': 'completed',
        'input_value': {'text': helpers.WORK_PHONE},
    }
    response = await call_notifier.send(['forward'], status=ask_status)
    assert (
        response.json()['actions'][0]['forward']['yandex_uid']
        == helpers.YANDEX_UID
    )
    return response


async def imitate_manager_misses_call(call_notifier: helpers.CallNotifier):
    await imitate_scenario_until_forward(call_notifier)
    response = await call_notifier.send(
        ['playback', 'forward'], status=ivr_requests.NO_ANSWER_STATUS,
    )
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['salesforce']['short_number']
    )
    await call_notifier.skip_intermediate()
    return response


async def imitate_managers_queue_miss(call_notifier: helpers.CallNotifier):
    await imitate_manager_misses_call(call_notifier)
    response = await call_notifier.send(
        ['playback', 'forward'], status=ivr_requests.NO_ANSWER_STATUS,
    )
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['support']['short_number']
    )
    await call_notifier.skip_intermediate()
    return response


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_accept_call(
        _mock_sf_data_load, taxi_cc_sf_cti, _mock_staff_api,
):
    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_scenario_until_forward(call_notifier)
    await call_notifier.answer_forward()
    await call_notifier.send(['hangup'])
    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_sf_call_info(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_scenario_until_forward(call_notifier)

    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)

    await call_notifier.answer_forward()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(['hangup'])
    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    assert time_checker.check()
    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_sf_call_info_on_hangup(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_scenario_until_forward(call_notifier)

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)
    await call_notifier.send([], status=ivr_requests.ABONENT_HANGUP_STATUS)

    helpers.check_sf_request(helpers.WORK_PHONE, 'incoming', 'answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_missed_call_sales_answered(
        _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_manager_misses_call(call_notifier)
    await call_notifier.answer_forward()
    await call_notifier.send(['hangup'])
    helpers.check_sf_request('salesforce', 'incoming', 'answer')
    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_missed_call_support_answered(
        _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_managers_queue_miss(call_notifier)
    await call_notifier.answer_forward()
    await call_notifier.send(['hangup'])
    helpers.check_sf_request('support', 'incoming', 'answer')
    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_totally_missed_call(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await imitate_managers_queue_miss(call_notifier)

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(
        ['playback', 'hangup'], status=ivr_requests.NO_ANSWER_STATUS,
    )

    helpers.check_sf_request('support', 'incoming', 'no_answer')
    assert time_checker.check()

    await call_notifier.skip_intermediate()
    await call_notifier.send([])


@pytest.mark.config(CC_SF_CTI_QUEUES_CONFIG=CC_QUEUES)
@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_free_person(
        mocked_time, _mock_sf_data_load, _mock_staff_api, taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    await call_notifier.send(['answer'])
    await call_notifier.send(['ask'])
    ask_status = {'state': 'completed', 'input_value': {'text': ''}}
    response = await call_notifier.send(
        ['playback', 'forward'], status=ask_status,
    )
    assert (
        response.json()['actions'][1]['forward']['phone_number']
        == CC_QUEUES['salesforce']['short_number']
    )
    await call_notifier.skip_intermediate()  # doing playback

    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)

    await call_notifier.answer_forward()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(['hangup'])
    await call_notifier.send([])
    helpers.check_sf_request('salesforce', 'incoming', 'answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_unexpected_service_number(_mock_staff_api, taxi_cc_sf_cti):
    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='incoming')
    call_notifier.current_request['service_number'] = 'not_a_number'
    response = await call_notifier.send(None, expected_code=400)
    assert response.json()['code'] == 'UNEXPECTED_SERVICE_NUMBER'
