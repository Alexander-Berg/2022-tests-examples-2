import pytest
from tests_processing.processing.bank import common


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'none_success',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'application_status': common.STATUS_SUCCESS,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'none_failed',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_FAILED,
                'application_status': common.STATUS_FAILED,
            },
            1,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'none_pending',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_PENDING,
                'application_status': common.STATUS_CORE_BANKING,
            },
            1,
        ),
        (
            {'is_error': True, 'errors': ['']},
            'fail_before',
            {'is_error': True, 'errors': ['']},
            0,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'one_fail',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            2,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'one_timeout',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            2,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'none_success_errors_list',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors', '1:but in lines'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'snils': common.SNILS,
                },
            },
            'only_snils',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                },
            },
            'only_inn',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
            },
            'none_success_empty_errors_list',
            {
                'application_data': {
                    'phone': common.PHONE_NUMBER,
                    'first_name': common.FIRST_NAME,
                    'last_name': common.LAST_NAME,
                    'middle_name': common.MIDDLE_NAME,
                    'birthday': common.BIRTHDAY,
                    'passport_number': common.PASSPORT_NUMBER,
                    'inn': common.INN,
                    'snils': common.SNILS,
                },
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
                'core_banking_status': common.STATUS_SUCCESS,
                'application_status': common.STATUS_SUCCESS,
            },
            1,
        ),
    ],
)
async def test_bank_simpl_stage_simplified_upgrade(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
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

    if error_type == 'only_inn':
        helper.set_values(snils=None)
    elif error_type == 'only_snils':
        helper.set_values(inn=None)
    else:
        helper.set_values()
    await helper.create_simpl_application()
    helper.prepare_mocks()
    if error_type == 'none_failed':
        core_client_mock.application_status = common.STATUS_FAILED
    elif error_type in ['none_success', 'only_inn', 'only_snils']:
        core_client_mock.application_status = common.STATUS_SUCCESS
    elif error_type == 'none_pending':
        core_client_mock.application_status = common.STATUS_PENDING
    elif error_type == '500':
        core_client_mock.request_upgrade.response_code = 500
    elif error_type == 'one_fail':
        core_client_mock.request_upgrade.first_fail = True
        core_client_mock.application_status = common.STATUS_SUCCESS
    elif error_type == 'one_timeout':
        core_client_mock.request_upgrade.first_timeout = True
        core_client_mock.application_status = common.STATUS_SUCCESS
    elif error_type == 'none_success_errors_list':
        core_client_mock.request_upgrade.errors_list = True
        core_client_mock.application_status = common.STATUS_SUCCESS
    elif error_type == 'none_success_empty_errors_list':
        core_client_mock.request_upgrade.empty_errors_list = True
        core_client_mock.application_status = common.STATUS_SUCCESS
    await helper.start_single_stage(
        'create-simplified-stage', started_shared, expected_shared,
    )
    helper.check_simpl_calls(simplified_upgrade=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            'none',
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            1,
        ),
        (
            {'core_banking_request_id': None},
            'null',
            {'core_banking_request_id': None},
            0,
        ),
        (
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            'one_fail',
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            2,
        ),
        (
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            'one_timeout',
            {'core_banking_request_id': common.CORE_BANKING_REQUEST_ID},
            2,
        ),
    ],
)
async def test_bank_simpl_stage_set_core_banking_request_id(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
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
    helper.set_values()
    await helper.create_simpl_application()
    helper.prepare_mocks()
    if error_type == 'one_fail':
        applications_mock.set_core_request_id.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.set_core_request_id.first_timeout = True
    await helper.start_single_stage(
        'set-core-banking-request-id-stage-id',
        started_shared,
        expected_shared,
    )
    helper.check_simpl_calls(set_core_banking_request_id=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, set_status_calls',
    [
        (
            {'is_error': False, 'errors': [''], 'status': 'SUCCESS'},
            'none',
            {'is_error': False, 'errors': [''], 'status': 'SUCCESS'},
            1,
        ),
        (
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            'fail_before',
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            1,
        ),
        (
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            'one_fail',
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            2,
        ),
        (
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            'one_timeout',
            {'is_error': True, 'errors': [''], 'status': 'SUCCESS'},
            2,
        ),
    ],
)
async def test_bank_simpl_stage_set_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        set_status_calls,
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
    helper.set_values(set_application_status=[common.STATUS_SUCCESS])
    await helper.create_simpl_application()
    helper.prepare_mocks()
    if error_type == 'one_fail':
        applications_mock.simpl_set_status.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.simpl_set_status.first_timeout = True
    await helper.start_single_stage(
        'set-application-status-stage-id',
        started_shared,
        expected_shared,
        pipeline='simplified-identification-application-status-pipeline',
    )
    assert (
        helper.applications_mock.simpl_set_status.handler.times_called
        == set_status_calls
    )
    helper.check_application_status_calls(
        simpl_set_status=set_status_calls, create_event=0,
    )


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            'none_success',
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_FAILED,
            },
            'none_failed',
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_FAILED,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            'fail_before_1',
            {
                'is_error': True,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_PROCESSING,
            },
            'fail_before_2',
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_PROCESSING,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': [''],
                'status': common.STATUS_PROCESSING,
            },
            'fail_before_3',
            {
                'is_error': True,
                'errors': [''],
                'status': common.STATUS_PROCESSING,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            'one_fail',
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            2,
        ),
        (
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            'one_timeout',
            {
                'is_error': False,
                'errors': [''],
                'status': common.STATUS_SUCCESS,
            },
            2,
        ),
    ],
)
async def test_bank_simpl_stage_set_application_status(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
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
    helper.set_values(set_application_status=[started_shared['status']])
    await helper.create_simpl_application()
    helper.prepare_mocks()
    if error_type == 'one_fail':
        applications_mock.simpl_set_status.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.simpl_set_status.first_timeout = True
    await helper.start_single_stage(
        'set-application-status-stage-id',
        started_shared,
        expected_shared,
        pipeline='simplified-identification-application-status-pipeline',
    )
    assert (
        helper.applications_mock.simpl_set_status.handler.times_called
        == expected_tries
    )
    helper.check_application_status_calls(
        simpl_set_status=expected_tries, create_event=0,
    )


@pytest.mark.parametrize(
    'application_status, expected_tries',
    [
        (common.STATUS_SUCCESS, 0),
        (common.STATUS_PROCESSING, 0),
        (common.STATUS_AGREMENTS_ACCEPTED, 1),
        (common.STATUS_CORE_BANKING, 0),
        (common.STATUS_FAILED, 0),
    ],
)
async def test_bank_simpl_stage_set_agreements_accepted(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        application_status,
        expected_tries,
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

    started_shared = {
        'application_status': application_status,
        'is_error': False,
        'errors': None,
    }

    expected_shared = started_shared
    helper.set_values(
        set_application_status=[common.STATUS_AGREMENTS_ACCEPTED],
    )
    helper.prepare_mocks()
    await helper.start_single_stage(
        'set-agreements-accepted-status-stage-id',
        started_shared,
        expected_shared,
    )
    assert (
        applications_mock.simpl_set_status.handler.times_called
        == expected_tries
    )


@pytest.mark.parametrize(
    'application_status, expected_tries',
    [
        (common.STATUS_SUCCESS, 1),
        (common.STATUS_PROCESSING, 0),
        (common.STATUS_AGREMENTS_ACCEPTED, 0),
        (common.STATUS_CORE_BANKING, 1),
        (common.STATUS_FAILED, 1),
    ],
)
async def test_bank_simpl_stage_set_core_banking(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        application_status,
        expected_tries,
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

    started_shared = {
        'application_status': application_status,
        'is_error': False,
        'errors': None,
    }

    expected_shared = started_shared
    helper.set_values(set_application_status=[application_status])
    helper.prepare_mocks()
    await helper.start_single_stage(
        'set-core-banking-status-stage-id', started_shared, expected_shared,
    )
    assert (
        applications_mock.simpl_set_status.handler.times_called
        == expected_tries
    )
