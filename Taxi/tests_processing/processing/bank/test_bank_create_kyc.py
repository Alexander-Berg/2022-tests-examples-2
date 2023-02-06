import pytest

from tests_processing.processing.bank import common
from tests_processing.processing.bank import kyc_helper


@pytest.mark.parametrize(
    'application_status_from_java, expected_create_event_count, '
    'expected_defaults_groups, notifications_sended, set_applications',
    [
        (
            common.STATUS_SUCCESS,
            0,
            [common.PROGRESS_DEFAULTS_GROUP, common.SUCCESS_DEFAULTS_GROUP],
            2,
            common.SET_APPLICATIONS_SUCCESS,
        ),
        (
            common.STATUS_FAILED,
            0,
            [common.PROGRESS_DEFAULTS_GROUP, common.FAILED_DEFAULTS_GROUP],
            2,
            common.SET_APPLICATIONS_FAILED,
        ),
        (
            common.STATUS_PENDING,
            0,
            [common.PROGRESS_DEFAULTS_GROUP],
            1,
            common.SET_APPLICATIONS_PROCESSING,
        ),
    ],
)
async def test_bank_applications_good_kyc(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,  # noqa
        processing_mock,
        notifications_mock,
        agreements_mock,
        application_status_from_java,
        expected_create_event_count,
        expected_defaults_groups,
        notifications_sended,
        set_applications,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=set_applications)
    await helper.create_kyc_application()
    helper.prepare_mocks()
    helper.core_client_mock.application_status = application_status_from_java
    helper.notifications_mock.defaults_groups = expected_defaults_groups
    await helper.send_kyc_event()
    helper.check_kyc_calls(
        create_event=expected_create_event_count,
        kyc_get_application_data=1,
        kyc_upgrade=1,
        set_core_banking_request_id=1,
        notifications_sended=notifications_sended,
        accept_agreement=1,
    )


@pytest.mark.config(
    BANK_APPLICATIONS_KYC_NOTIFICATION_PROCESSING_ENABLED=False,  # noqa
)
async def test_bank_applications_good_kyc_notification(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    await helper.send_kyc_event()
    helper.check_kyc_calls(
        default_value=1,
        create_event=0,
        notifications_sended=0,
        get_application_data=0,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries, stq_fail, ', [(400, 1, True), (500, 3, True)],
)
async def test_bank_kyc_get_application_data_response_error(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_code,
        expected_tries,
        stq_fail,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    applications_mock.kyc_get_application_data.response_code = error_code

    await helper.send_kyc_event(stq_fail=stq_fail)
    helper.check_kyc_calls(
        kyc_get_application_data=expected_tries, notifications_sended=1,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_kyc_get_application_data_response_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_kyc_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS
    if error_type == '500':
        applications_mock.kyc_get_application_data.first_fail = True
    elif error_type == 'timeout':
        applications_mock.kyc_get_application_data.first_timeout = True
    else:
        assert False

    await helper.send_kyc_event()
    helper.check_kyc_calls(
        default_value=1,
        kyc_get_application_data=2,
        create_event=0,
        get_application_data=0,
        notifications_sended=2,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries, stq_fail, create_event',
    [(400, 1, True, 0), (500, 2, True, 0)],
)
async def test_bank_kyc_create_response_error(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_code,
        expected_tries,
        stq_fail,
        create_event,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    core_client_mock.kyc_request_upgrade.response_code = error_code

    await helper.send_kyc_event(stq_fail=stq_fail)
    helper.check_kyc_calls(
        default_value=1,
        kyc_upgrade=expected_tries,
        set_core_banking_request_id=0,
        create_event=create_event,
        get_application_data=0,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_kyc_create_response_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_kyc_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS
    if error_type == '500':
        core_client_mock.request_create.first_fail = True
    elif error_type == 'timeout':
        core_client_mock.request_create.first_timeout = True
    else:
        assert False

    await helper.send_kyc_event()
    helper.check_kyc_calls(
        default_value=1,
        create_event=0,
        get_application_data=0,
        notifications_sended=2,
    )


@pytest.mark.parametrize('error_code, expected_tries', [(400, 1), (500, 2)])
async def test_bank_kyc_set_core_banking_request_id_response_error(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_code,
        expected_tries,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    applications_mock.set_core_request_id.response_code = error_code

    await helper.send_kyc_event(stq_fail=True)
    helper.check_kyc_calls(
        default_value=1,
        set_core_banking_request_id=expected_tries,
        create_event=0,
        get_application_data=0,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_kyc_set_core_banking_request_id_response_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    if error_type == '500':
        applications_mock.set_core_request_id.first_fail = True
    elif error_type == 'timeout':
        applications_mock.set_core_request_id.first_timeout = True
    else:
        assert False

    await helper.send_kyc_event()
    helper.check_kyc_calls(
        default_value=1,
        set_core_banking_request_id=2,
        create_event=0,
        get_application_data=0,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_kyc_notifications_response_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    if error_type == '500':
        notifications_mock.send_notification.first_fail = True
    elif error_type == 'timeout':
        notifications_mock.send_notification.first_timeout = True
    else:
        assert False

    await helper.send_kyc_event()
    helper.check_kyc_calls(
        default_value=1,
        set_core_banking_request_id=1,
        create_event=0,
        notifications_sended=2,
        get_application_data=0,
    )


@pytest.mark.parametrize('error_type', ['first_fail', 'timeout'])
async def test_bank_kyc_set_application_status_response_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_type,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values(set_application_status=common.SET_APPLICATIONS_SUCCESS)
    await helper.create_kyc_application()
    helper.prepare_mocks()
    core_client_mock.application_status = common.STATUS_SUCCESS
    if error_type == 'first_fail':
        applications_mock.kyc_set_status.first_fail = True
    elif error_type == 'timeout':
        applications_mock.kyc_set_status.first_timeout = True
    else:
        assert False

    await helper.send_kyc_event()
    helper.check_application_status_calls(kyc_set_status=3, create_event=0)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {},
            'none',
            {
                'agreement_version': 1,
                'application_data': {
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'patronymic': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'inn': common.INN,
                    'snils': common.SNILS,
                    'sex': common.SEX,
                    'id_doc_number': common.PASSPORT_NUMBER,
                    'id_doc_issued': common.ID_DOC_ISSUED,
                    'birth_place_info': common.BIRTH_PLACE_INFO,
                    'id_doc_issued_by': common.ID_DOC_ISSUED_BY,
                    'id_doc_department_code': common.ID_DOC_DEPARTAMENT_CODE,
                    'address_registration': common.ADDRESS_REGISTRATION,
                    'address_actual': common.ADDRESS_REGISTRATION,
                },
                'is_error': False,
                'errors': None,
            },
            1,
        ),
        (
            {},
            'one_fail',
            {
                'agreement_version': 1,
                'application_data': {
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'patronymic': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'inn': common.INN,
                    'snils': common.SNILS,
                    'sex': common.SEX,
                    'id_doc_number': common.PASSPORT_NUMBER,
                    'id_doc_issued': common.ID_DOC_ISSUED,
                    'birth_place_info': common.BIRTH_PLACE_INFO,
                    'id_doc_issued_by': common.ID_DOC_ISSUED_BY,
                    'id_doc_department_code': common.ID_DOC_DEPARTAMENT_CODE,
                    'address_registration': common.ADDRESS_REGISTRATION,
                    'address_actual': common.ADDRESS_REGISTRATION,
                },
                'is_error': False,
                'errors': None,
            },
            2,
        ),
        (
            {},
            'one_timeout',
            {
                'agreement_version': 1,
                'application_data': {
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'patronymic': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'inn': common.INN,
                    'snils': common.SNILS,
                    'sex': common.SEX,
                    'id_doc_number': common.PASSPORT_NUMBER,
                    'id_doc_issued': common.ID_DOC_ISSUED,
                    'birth_place_info': common.BIRTH_PLACE_INFO,
                    'id_doc_issued_by': common.ID_DOC_ISSUED_BY,
                    'id_doc_department_code': common.ID_DOC_DEPARTAMENT_CODE,
                    'address_registration': common.ADDRESS_REGISTRATION,
                    'address_actual': common.ADDRESS_REGISTRATION,
                },
                'is_error': False,
                'errors': None,
            },
            2,
        ),
    ],
)
async def test_bank_kyc_stage_get_application_data(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
):
    helper = kyc_helper.KycHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_kyc_application()
    helper.prepare_mocks()
    if error_type == 'one_fail':
        applications_mock.kyc_get_application_data.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.kyc_get_application_data.first_timeout = True
    await helper.start_single_stage(
        'kyc-get-application-data-stage-id',
        started_shared,
        expected_shared=expected_shared,
    )

    helper.check_kyc_calls(kyc_get_application_data=expected_tries)


async def test_start_kyc_status_stq_polling_stage(
        processing,
        mockserver,
        stq,
        processing_mock,
        core_client_mock,
        applications_mock,
        notifications_mock,
        agreements_mock,
):
    stq_name = 'bank_applications_kyc_status_polling'
    with stq.flushing():
        helper = kyc_helper.KycHelper(
            core_client_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            agreements_mock,
            processing,
        )
        helper.set_values()
        await helper.create_kyc_application()
        helper.prepare_mocks()
        event_id = await helper.send_kyc_event(already_flushing_stq=True)

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        assert call['kwargs']['buid'] == common.BUID
        assert call['kwargs']['idempotency_token'] == event_id
        assert call['kwargs']['request_id'] == common.CORE_BANKING_REQUEST_ID
        assert call['kwargs']['application_id'] == common.APPLICATION_ID
        helper.check_kyc_calls(
            default_value=1, create_event=0, get_application_data=0,
        )
