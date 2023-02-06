import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


ESIA_STATE = '123'
AUTH_CODE = '456'
REDIRECT_URL = 'some_url'


def common_checks(
        pgsql,
        application_id,
        status=common.STATUS_SUBMITTED,
        auth_code=None,
        hist_not_empty=False,
):
    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].application_id == application_id
    assert applications[0].esia_state == ESIA_STATE
    assert applications[0].auth_code == auth_code
    assert applications[0].status == status

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, application_id,
    )
    if hist_not_empty:
        assert len(application_history) == 1
    else:
        assert not application_history


@pytest.mark.parametrize(
    'header',
    [
        'X-Yandex-BUID',
        'X-Yandex-UID',
        'X-YaBank-SessionUUID',
        'X-YaBank-PhoneID',
    ],
)
async def test_simplified_identification_submit_esia_response_unauthorized(
        taxi_bank_applications, core_esia_integration_mock, pgsql, header,
):
    headers = common.headers_with_idempotency()
    headers.pop(header)
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=headers,
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 401


async def test_simplified_identification_submit_esia_response_esia_core_500(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.internal_error = True

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


async def test_simplified_identification_submit_esia_response_esia_core_400(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.parse_error_reason = 'TOKEN_IS_NOT_VALID'

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.INVALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 400
    assert response.json()['parse_error_reason'] == 'TOKEN_IS_NOT_VALID'
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


async def test_simplified_identification_submit_esia_response_no_app_found(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 404
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.parametrize(
    'simpl_status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_SUCCESS,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_esia_app_no_idemp_token(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        simpl_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    status = common.STATUS_PROCESSING
    if simpl_status in [common.STATUS_SUCCESS, common.STATUS_FAILED]:
        status = simpl_status
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=status,
        simpl_esia_status=simpl_status,
        esia_state=ESIA_STATE,
        submit_idempotency_token=None,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(pgsql, application_id, status=simpl_status)


@pytest.mark.parametrize(
    'simpl_status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_SUCCESS,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_esia_app_with_other_idemp_token(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        simpl_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    status = common.STATUS_PROCESSING
    if simpl_status in [common.STATUS_SUCCESS, common.STATUS_FAILED]:
        status = simpl_status
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=status,
        simpl_esia_status=simpl_status,
        esia_state=ESIA_STATE,
        submit_idempotency_token='11111111-1111-1111-1111-111111111111',
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 409
    assert (
        response.json()['message']
        == 'Application is already submitted with another idempotency token'
    )
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(pgsql, application_id, status=simpl_status)


async def test_simplified_identification_esia_old_app_success(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_SUCCESS,
        simpl_esia_status=common.STATUS_SUCCESS,
        esia_state=ESIA_STATE,
        auth_code=AUTH_CODE,
        redirect_url=REDIRECT_URL,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(
        pgsql,
        application_id,
        status=common.STATUS_SUCCESS,
        auth_code=AUTH_CODE,
    )


@pytest.mark.parametrize(
    'simpl_status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_esia_app_with_none_auth_code(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        simpl_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    status = common.STATUS_PROCESSING
    if simpl_status == common.STATUS_FAILED:
        status = simpl_status
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=status,
        simpl_esia_status=simpl_status,
        esia_state=ESIA_STATE,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(pgsql, application_id, status=simpl_status)


@pytest.mark.parametrize(
    'simpl_status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_esia_app_with_other_auth_code(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        simpl_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE + '1234'

    status = common.STATUS_PROCESSING
    if simpl_status == common.STATUS_FAILED:
        status = simpl_status
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=status,
        simpl_esia_status=simpl_status,
        esia_state=ESIA_STATE,
        auth_code=AUTH_CODE,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 409
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(
        pgsql, application_id, status=simpl_status, auth_code=AUTH_CODE,
    )


@pytest.mark.parametrize(
    'simpl_status',
    [
        common.STATUS_PROCESSING,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_esia_app_with_same_auth_code(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        simpl_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    status = common.STATUS_PROCESSING
    if simpl_status == common.STATUS_FAILED:
        status = simpl_status
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=status,
        simpl_esia_status=simpl_status,
        esia_state=ESIA_STATE,
        auth_code=AUTH_CODE,
        redirect_url=REDIRECT_URL,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql, application_id, status=simpl_status, auth_code=AUTH_CODE,
    )


async def test_simplified_identification_esia_submitted_app_same_auth_code(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_PROCESSING,
        simpl_esia_status=common.STATUS_SUBMITTED,
        esia_state=ESIA_STATE,
        auth_code=AUTH_CODE,
        redirect_url=REDIRECT_URL,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert taxi_processing_mock.create_event_handler.times_called == 1

    common_checks(pgsql, application_id, auth_code=AUTH_CODE)


async def test_simplified_identification_submit_esia_response_processing_500(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    taxi_processing_mock.http_status_code = 500
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status='CREATED',
        simpl_esia_status=common.STATUS_CREATED,
        esia_state=ESIA_STATE,
        submit_idempotency_token=None,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql, application_id, auth_code=AUTH_CODE, hist_not_empty=True,
    )


async def test_simplified_identification_submit_esia_response_ok(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
        esia_state=ESIA_STATE,
        submit_idempotency_token=None,
        redirect_url=REDIRECT_URL,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.parse_esia_auth_response.has_calls
    assert taxi_processing_mock.create_event_handler.times_called == 1
    resp = response.json()
    assert 'application_id' in resp
    assert resp['application_id'] == application_id

    common_checks(
        pgsql, application_id, auth_code=AUTH_CODE, hist_not_empty=True,
    )


@pytest.mark.parametrize('auth_code', [AUTH_CODE, AUTH_CODE + '1'])
async def test_simplified_identification_esia_app_already_submitted_new_creat(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
        auth_code,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
        esia_state=ESIA_STATE,
        auth_code=AUTH_CODE,
        submit_idempotency_token=None,
    )

    @testpoint('esia_auth_code_update')
    async def _data_race(data):
        sql = """
            UPDATE bank_applications.simplified_identification_esia
            SET status = \'SUBMITTED\', auth_code = %s,
                submit_idempotency_token = %s
            WHERE application_id = %s
            RETURNING
            application_id
            """
        cursor = pgsql['bank_applications'].cursor()
        cursor.execute(
            sql, (auth_code, common.DEFAULT_IDEMPOTENCY_TOKEN, application_id),
        )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert core_esia_integration_mock.parse_esia_auth_response.has_calls

    assert response.status_code == 500
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, auth_code=auth_code)


@pytest.mark.parametrize(
    'simpl_esia_status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_SUCCESS,
        common.STATUS_FAILED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_simplified_identification_submit_esia_app_changed_status(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
        simpl_esia_status,
):
    core_esia_integration_mock.esia_state = ESIA_STATE
    core_esia_integration_mock.auth_code = AUTH_CODE

    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
        esia_state=ESIA_STATE,
        submit_idempotency_token=None,
    )

    @testpoint('esia_auth_code_update')
    async def _data_race(data):
        sql = """
            UPDATE bank_applications.simplified_identification_esia
            SET status = %s, auth_code = %s, submit_idempotency_token = %s
            WHERE application_id = %s
            RETURNING
            application_id
            """
        cursor = pgsql['bank_applications'].cursor()
        cursor.execute(
            sql,
            (
                simpl_esia_status,
                AUTH_CODE,
                common.DEFAULT_IDEMPOTENCY_TOKEN,
                application_id,
            ),
        )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/submit',
        headers=common.headers_with_idempotency(),
        json={'esia_raw_response': common.VALID_ESIA_RAW_RESPONSE},
    )

    assert core_esia_integration_mock.parse_esia_auth_response.has_calls

    assert response.status_code == 500
    assert not taxi_processing_mock.create_event_handler.has_calls
    common_checks(
        pgsql, application_id, auth_code=AUTH_CODE, status=simpl_esia_status,
    )
