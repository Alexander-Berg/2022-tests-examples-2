import pytest
from tests_processing.processing.bank import common

BUID = 'buid-1'
YUID = '8421'
PHONE_NUMBER = '+79037842423'

IP = '127.0.0.1'


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_anon_set_application_status_response_first_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS
    if error_type == '500':
        applications_mock.simpl_set_status.first_fail = True
    elif error_type == 'timeout':
        applications_mock.simpl_set_status.first_timeout = True
    else:
        assert False

    await helper.send_simpl_event()
    helper.check_application_status_calls(simpl_set_status=4, create_event=0)


async def test_bank_applications_good_simpl_poll_simpl_set_status_fail(
        processing,
        stq,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
):
    stq_name = 'bank_applications_simplified_status_polling'
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(
        set_application_status=common.SET_APPLICATIONS_PROCESSING,
    )
    await helper.create_simpl_application()
    helper.prepare_mocks()

    core_client_mock.application_status = common.STATUS_PENDING
    with stq.flushing():
        await helper.send_simpl_event(already_flushing_stq=True)
        assert stq[stq_name].times_called == 1
    helper.check_simpl_calls(default_value=1, get_application_data=0)
    helper.check_application_status_calls(
        default_value=1, simpl_set_status=3, create_event=0,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries, stq_fail', [(400, 1, True), (500, 3, True)],
)
async def test_bank_simpl_set_application_status_response_error(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_code,
        expected_tries,
        stq_fail,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS

    applications_mock.simpl_set_status.response_code = error_code
    await helper.send_simpl_event(stq_fail=True)

    helper.check_application_status_calls(
        simpl_set_status=expected_tries, create_event=0,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_simpl_delete_personal_data_failures(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS
    if error_type == '500':
        applications_mock.delete_personal_data.first_fail = True
    elif error_type == 'timeout':
        applications_mock.delete_personal_data.first_timeout = True
    else:
        assert False

    await helper.send_simpl_event()
    helper.check_delete_pd_calls(delete_data=2)
    helper.check_application_status_calls(simpl_set_status=3, create_event=0)


async def test_bank_simpl_delete_personal_data_ok(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS

    await helper.send_simpl_event()

    helper.check_delete_pd_calls(delete_data=1)
    helper.check_application_status_calls(simpl_set_status=3, create_event=0)


@pytest.mark.parametrize(
    'application_status_from_java, create_event_times_called',
    [(common.STATUS_FAILED, 1)],
)
async def test_bank_applications_set_fail_status(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        notifications_mock,
        agreements_mock,
        applications_mock,
        processing_mock,
        application_status_from_java,
        create_event_times_called,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(
        defaults_groups=[
            common.PROGRESS_DEFAULTS_GROUP,
            common.FAILED_DEFAULTS_GROUP,
        ],
        set_application_status=common.SET_APPLICATIONS_FAILED,
    )
    helper.prepare_mocks()
    await helper.create_simpl_application()
    core_client_mock.application_status = application_status_from_java
    await helper.send_simpl_event()
    assert not helper.processing_mock.received_events
