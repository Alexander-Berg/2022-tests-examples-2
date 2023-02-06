import pytest

from tests_cc_sf_cti import helpers
from tests_cc_sf_cti import ivr_notice_requests as ivr_requests


CC_FLOW = {'+74992296622': {'cc_sf_flow_name': 'default_flow'}}


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_initiate_call(
        mocked_time,
        _mock_sf_data_load,
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='outgoing')
    await call_notifier.originate(
        ivr_requests.ABONENT_NUMBER, helpers.YANDEX_UID,
    )
    response = await call_notifier.send(['forward'])
    assert (
        response.json()['actions'][0]['forward']['yandex_uid']
        == helpers.YANDEX_UID
    )

    time_checker.mock_time(helpers.TimeChecker.CALL_START_TIME)

    await call_notifier.answer_forward()

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(['hangup'])
    await call_notifier.send([])

    helpers.check_sf_request(helpers.WORK_PHONE, 'outgoing', 'answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_abonent_no_answer(
        mocked_time,
        _mock_sf_data_load,
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='outgoing')
    await call_notifier.originate(
        ivr_requests.ABONENT_NUMBER, helpers.YANDEX_UID,
    )

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send([], status=ivr_requests.NO_ANSWER_STATUS)

    helpers.check_sf_request(helpers.WORK_PHONE, 'outgoing', 'no_answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_manager_missed_outgoing(
        mocked_time,
        _mock_sf_data_load,
        _mock_ivr_create_call,
        _mock_staff_api,
        taxi_cc_sf_cti,
):
    time_checker = helpers.TimeChecker(mocked_time)
    time_checker.mock_time(helpers.TimeChecker.CALL_INIT_TIME)

    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='outgoing')
    await call_notifier.originate(
        ivr_requests.ABONENT_NUMBER, helpers.YANDEX_UID,
    )

    await call_notifier.send(['forward'])

    time_checker.mock_time(helpers.TimeChecker.CALL_END_TIME)

    await call_notifier.send(
        ['playback', 'hangup'], status=ivr_requests.NO_ANSWER_STATUS,
    )
    await call_notifier.skip_intermediate()
    await call_notifier.send([])

    helpers.check_sf_request(helpers.WORK_PHONE, 'outgoing', 'no_answer')
    assert time_checker.check()


@pytest.mark.config(CC_SF_CTI_PHONE_TO_FLOW_MAP_CONFIG=CC_FLOW)
@pytest.mark.config(CC_SF_CTI_FLOW_CONFIG=helpers.CC_FLOWS_CONFIG)
async def test_originate_failed(
        _mock_ivr_create_call, _mock_staff_api, taxi_cc_sf_cti,
):
    call_notifier = helpers.CallNotifier(taxi_cc_sf_cti, direction='outgoing')
    await call_notifier.originate(
        ivr_requests.ABONENT_NUMBER, helpers.YANDEX_UID,
    )

    await call_notifier.send([], status=ivr_requests.OTHER_ERROR_STATUS)
