import pytest
from tests_processing.processing.bank import common

BUID = 'buid-1'
YUID = '8421'
PHONE_NUMBER = '+79037842423'

STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING'

CORE_BANKING_REQUEST_ID = 'some_javist_id'
APPLICATION_ID = '123456789abcdefgh'

IP = '127.0.0.1'


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_anon_set_application_status_response_first_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_type,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS
    if error_type == '500':
        applications_mock.set_status.first_fail = True
    elif error_type == 'timeout':
        applications_mock.set_status.first_timeout = True
    else:
        assert False

    await helper.send_anon_event()
    await helper.send_update_buid_event()
    assert helper.applications_mock.set_status.handler.times_called == 2
    helper.check_application_status_calls(set_status=2, create_event=1)


async def test_bank_applications_good_anon_poll_set_status_fail(
        processing,
        stq,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
):
    stq_name = 'bank_applications_registration_status_polling'
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    with stq.flushing():
        await helper.send_anon_event(already_flushing_stq=True)
        assert stq[stq_name].times_called == 1
    helper.check_anon_calls(default_value=1)
    core_client_mock.application_status = STATUS_SUCCESS
    applications_mock.set_status.response_code = 400
    await helper.send_update_buid_event(stq_fail=True)
    helper.check_update_buid_calls(update_buid_status=1, update_app_status=1)


@pytest.mark.parametrize(
    'error_code, expected_tries, stq_fail', [(400, 1, True), (500, 2, True)],
)
async def test_bank_anon_set_application_status_response_error(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_code,
        expected_tries,
        stq_fail,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS

    applications_mock.set_status.response_code = error_code
    await helper.send_anon_event()

    await helper.send_update_buid_event(stq_fail)
    assert (
        helper.applications_mock.set_status.handler.times_called
        == expected_tries
    )


@pytest.mark.parametrize(
    'application_status_from_java, create_event_times_called',
    [(STATUS_FAILED, 1)],
)
async def test_bank_applications_set_fail_status(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        application_status_from_java,
        create_event_times_called,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = application_status_from_java
    await helper.send_anon_event()
    assert len(helper.processing_mock.received_events) == 1
    assert helper.processing_mock.received_events[0] == {
        'buid': BUID,
        'kind': 'update',
        'core_banking_request_id': CORE_BANKING_REQUEST_ID,
        'type': 'application_status_result',
        'status': 'FAILED',
        'errors': ['0:no errors'],
    }


@pytest.mark.parametrize('error_code, expected_tries', [(409, 1)])
async def test_bank_anon_set_bank_phone_response_error(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_code,
        expected_tries,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    userinfo_mock.set_bank_phone.response_code = error_code

    await helper.send_anon_event()
    helper.check_anon_calls(
        get_application_data=1,
        get_antifraud_info_check=1,
        risk_phone_check=1,
        set_bank_phone=expected_tries,
        create_event=1,
    )
    assert len(helper.processing_mock.received_events) == 1
    assert helper.processing_mock.received_events[0] == {
        'buid': BUID,
        'kind': 'update',
        'core_banking_request_id': None,
        'type': 'application_status_result',
        'status': 'FAILED',
        'errors': ['409:phone already use'],
    }
