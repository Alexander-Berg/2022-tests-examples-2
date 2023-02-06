# pylint: disable=too-many-lines
import pytest
from tests_processing.processing.bank import common

BUID = 'buid-1'
YUID = '8421'
PHONE_NUMBER = '89037842423'

CORE_BANKING_REQUEST_ID = 'some_javist_id'
APPLICATION_ID = '123456789abcdefgh'

STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING'

IP = '127.0.0.1'


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            '400',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'DENY',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': True,
                'errors': [
                    '10.00.99:Phone analyzer: '
                    'Failed Russian phone number verification',
                ],
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_fail',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            2,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_timeout',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            2,
        ),
    ],
)
async def test_bank_anon_stage_risk_phone_check(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == '400':
        risk_mock.phone_check.response_code = 400
    elif error_type == 'DENY':
        risk_mock.phone_check.access_deny = True
    elif error_type == 'one_fail':
        risk_mock.phone_check.first_fail = True
    elif error_type == 'one_timeout':
        risk_mock.phone_check.first_timeout = True
    await helper.start_single_stage(
        'bank-risk-phone-check-stage-id', started_shared, expected_shared,
    )
    helper.check_anon_calls(risk_phone_check=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'errors': None, 'is_error': False},
            'none',
            {'errors': None, 'is_error': False},
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {'errors': None, 'is_error': False},
            'one_timeout',
            {'errors': None, 'is_error': False},
            2,
        ),
    ],
)
async def test_bank_anon_stage_subscribe_sid(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == 'one_timeout':
        passport_mock.subscribe_sid.first_timeout = True
    await helper.start_single_stage(
        'subscribe-sid-stage-id', started_shared, expected_shared,
    )
    helper.check_anon_calls(subscribe_sid=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            '409',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': True,
                'errors': ['409:phone already use'],
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_fail',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            2,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_timeout',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': None,
            },
            2,
        ),
    ],
)
async def test_bank_anon_stage_set_bank_phone(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == '409':
        userinfo_mock.set_bank_phone.response_code = 409
    elif error_type == 'one_fail':
        userinfo_mock.set_bank_phone.first_fail = True
    elif error_type == 'one_timeout':
        userinfo_mock.set_bank_phone.first_timeout = True
    await helper.start_single_stage(
        'set-bank-phone-stage-id', started_shared, expected_shared,
    )
    helper.check_anon_calls(set_bank_phone=expected_tries)


@pytest.mark.parametrize(
    'product', [None, common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none_success',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none_failed',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_FAILED,
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none_pending',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_PENDING,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_fail',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'one_timeout',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none_success_errors_list',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors', '1:but in lines'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {'application_data': {'phone': PHONE_NUMBER}},
            'none_success_empty_errors_list',
            {
                'application_data': {'phone': PHONE_NUMBER},
                'is_error': False,
                'errors': ['0:no errors'],
                'creation_error': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
    ],
)
async def test_bank_anon_stage_anonymous_create(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        product,
        started_shared,
        error_type,
        expected_shared,
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
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        product=product,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    if error_type == 'none_failed':
        core_client_mock.application_status = STATUS_FAILED
    elif error_type == 'none_success':
        core_client_mock.application_status = STATUS_SUCCESS
    elif error_type == '500':
        core_client_mock.request_create.response_code = 500
    elif error_type == 'one_fail':
        core_client_mock.request_create.first_fail = True
        core_client_mock.application_status = STATUS_SUCCESS
    elif error_type == 'one_timeout':
        core_client_mock.request_create.first_timeout = True
        core_client_mock.application_status = STATUS_SUCCESS
    elif error_type == 'none_success_errors_list':
        core_client_mock.request_create.errors_list = True
        core_client_mock.application_status = STATUS_SUCCESS
    elif error_type == 'none_success_empty_errors_list':
        core_client_mock.request_create.empty_errors_list = True
        core_client_mock.application_status = STATUS_SUCCESS
    await helper.start_single_stage(
        'create-anon-stage-id', started_shared, expected_shared,
    )
    helper.check_anon_calls(anonymous_create=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            'none',
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            1,
        ),
        (
            {'core_banking_request_id': None},
            'null',
            {'core_banking_request_id': None},
            0,
        ),
        (
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            'one_fail',
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            2,
        ),
        (
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            'one_timeout',
            {'core_banking_request_id': CORE_BANKING_REQUEST_ID},
            2,
        ),
    ],
)
async def test_bank_anon_stage_set_core_banking_request_id(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == '400':
        applications_mock.set_core_request_id.response_code = 400
    elif error_type == '500':
        applications_mock.set_core_request_id.response_code = 500
    elif error_type == 'one_fail':
        applications_mock.set_core_request_id.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.set_core_request_id.first_timeout = True
    await helper.start_single_stage(
        'set-core-banking-request-id-registration-stage-id',
        started_shared,
        expected_shared,
    )
    helper.check_anon_calls(set_core_banking_request_id=expected_tries)


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {
                'is_error': False,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            'none',
            {
                'is_error': False,
                'errors': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {
                'is_error': False,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            'one_fail',
            {
                'is_error': False,
                'errors': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {
                'is_error': False,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            'one_timeout',
            {
                'is_error': False,
                'errors': None,
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
    ],
)
async def test_bank_anon_stage_update_buid_status(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == 'one_fail':
        userinfo_mock.update_buid_status.first_fail = True
    elif error_type == 'one_timeout':
        userinfo_mock.update_buid_status.first_timeout = True
    await helper.start_single_stage(
        'update-buid-status-stage-id',
        started_shared,
        expected_shared,
        pipeline='update-buid-pipeline',
    )
    helper.check_update_buid_calls(
        update_buid_status=expected_tries, update_app_status=0,
    )


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, set_status_calls',
    [
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            'none',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            'one_fail',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            2,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            'one_timeout',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': 'SUCCESS',
            },
            2,
        ),
    ],
)
async def test_bank_anon_stage_set_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
        set_status_calls,
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
    if error_type == 'one_fail':
        applications_mock.set_status.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.set_status.first_timeout = True
    await helper.start_single_stage(
        'set-application-status-stage-id',
        started_shared,
        expected_shared,
        pipeline='application-status-pipeline',
    )
    assert (
        helper.applications_mock.set_status.handler.times_called
        == set_status_calls
    )
    helper.check_application_status_calls(
        set_status=set_status_calls, create_event=0,
    )


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            'none_success',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_FAILED,
            },
            'none_failed',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_FAILED,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            'fail_before_1',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_PENDING,
            },
            'fail_before_2',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_PENDING,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_PENDING,
            },
            'fail_before_3',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_PENDING,
            },
            1,
        ),
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            'one_fail',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            'one_timeout',
            {
                'is_error': False,
                'errors': ['unknown error at get-application-data-stage'],
                'status': STATUS_SUCCESS,
            },
            2,
        ),
    ],
)
async def test_bank_anon_stage_set_application_status(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        started_shared,
        error_type,
        expected_shared,
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
    if error_type == 'one_fail':
        applications_mock.set_status.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.set_status.first_timeout = True
    await helper.start_single_stage(
        'set-application-status-stage-id',
        started_shared,
        expected_shared,
        pipeline='application-status-pipeline',
    )
    assert (
        helper.applications_mock.set_status.handler.times_called
        == expected_tries
    )
    helper.check_application_status_calls(
        set_status=expected_tries, create_event=0,
    )
