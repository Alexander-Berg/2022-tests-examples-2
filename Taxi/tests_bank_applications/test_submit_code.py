import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'
SOME_PHONE = '+79081234323'
SUPPORT_URL = {'support_url': 'http://support.ya/'}
APPLICATION_TYPE = 'REGISTRATION'


async def test_submit_code_not_found_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
):
    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={
            'application_id': '97754336-d4d1-43c1-aadb-cabd06674ea6',
            'code': '123456',
        },
    )

    assert response.status_code == 404


async def test_submit_code_permission_violation(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    headers['X-Yandex-UID'] = 'qwer'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 404


@pytest.mark.now(MOCK_NOW)
async def test_submit_code_idempotency_check(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application_id = response.json()['application_id']

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': SOME_PHONE},
    )
    assert taxi_processing_mock.create_event_handler.times_called == 1

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2

    # simulate procaas start
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    # repeat submit_code with PROCESSING status
    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2

    headers = common.headers_wo_buid_w_idempotency(
        idempotency_token='57154736-d6d1-45c1-bbdb-cabd06674ea6',
    )
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 409
    assert taxi_processing_mock.create_event_handler.times_called == 2
    assert passport_internal_mock.commit_handler.times_called == 1
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1


@pytest.mark.now(MOCK_NOW)
async def test_submit_code_happy(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        testpoint,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    assert taxi_processing_mock.create_event_handler.times_called == 1

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': SOME_PHONE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    @testpoint('get_application_data_race')
    async def _get_application_data_race(data):
        response = await taxi_bank_applications.post(
            '/applications-internal/v1/get_application_data',
            headers=common.headers_without_buid(),
            json={'application_id': application_id},
        )
        assert response.status_code == 200
        assert response.json()['form'] == {'phone': SOME_PHONE}

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT status_text, submitted_form, yandex_uid '
        'FROM bank_applications.registration_applications '
        f'WHERE application_id=\'{application_id}\';',
    )
    records = list(cursor)

    assert len(records) == 1
    assert records[0][0] == 'PROCESSING'
    assert records[0][1] == {'phone': SOME_PHONE}
    assert records[0][2] == common.DEFAULT_YANDEX_UID

    assert taxi_processing_mock.create_event_handler.times_called == 2


CODE_INVALID = 'code.invalid'
ERRORS_TO_TANKER_KEY = {
    '__default__': {'tanker_key': 'passport.default_error'},
    CODE_INVALID: {'tanker_key': 'passport.code.invalid'},
}


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.config(
    BANK_APPLICATIONS_SUBMIT_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'locale, hint',
    [
        (None, 'Неверный код из смс'),
        ('ru', 'Неверный код из смс'),
        ('en', 'Invalid SMS code'),
    ],
)
async def test_submit_code_wrong_code(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        locale,
        hint,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    assert taxi_processing_mock.create_event_handler.times_called == 1

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': SOME_PHONE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    passport_internal_mock.set_commit_response(
        {'status': 'error', 'errors': [CODE_INVALID]},
    )

    headers = common.headers_wo_buid_w_idempotency()
    headers['X-Request-Language'] = locale
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAILED',
        'hint': hint,
        'support_url': SUPPORT_URL['support_url'],
    }


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.config(
    BANK_APPLICATIONS_SUBMIT_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'locale, hint',
    [
        (None, 'Неизвестная ошибка'),
        ('ru', 'Неизвестная ошибка'),
        ('en', 'Unknown error'),
    ],
)
async def test_submit_code_unknown_passport_error(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        locale,
        hint,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    assert taxi_processing_mock.create_event_handler.times_called == 1

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': SOME_PHONE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    passport_internal_mock.set_commit_response(
        {'status': 'error', 'errors': ['some_error']},
    )

    headers = common.headers_wo_buid_w_idempotency()
    headers['X-Request-Language'] = locale
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAILED',
        'hint': hint,
        'support_url': SUPPORT_URL['support_url'],
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('userinfo_fail_status', [404, 429, 500])
async def test_buid_not_found(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        userinfo_fail_status,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params '
        'FROM bank_applications.registration_applications '
        'WHERE application_id=%s;',
        [application_id],
    )
    records = list(cursor)

    assert len(records) == 1
    assert records[0][0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert bank_userinfo_mock.get_buid_info_handler.times_called == 0

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    headers = common.headers_wo_buid_w_idempotency()
    bank_userinfo_mock.set_http_status_code(userinfo_fail_status)
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )
    assert bank_userinfo_mock.get_buid_info_handler.times_called == 1
    assert response.status_code == userinfo_fail_status


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BANK_APPLICATIONS_SUBMIT_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
async def test_processing_has_fall_double_request_error(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params '
        'FROM bank_applications.registration_applications '
        'WHERE application_id=%s;',
        [application_id],
    )
    records = list(cursor)

    assert len(records) == 1
    assert records[0][0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert passport_internal_mock.submit_handler.times_called == 1

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    headers = common.headers_wo_buid_w_idempotency()
    taxi_processing_mock.set_http_status_code(500)
    taxi_processing_mock.set_response({})
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )
    assert response.status_code == 500
    assert passport_internal_mock.commit_handler.times_called == 1
    # default retry count
    assert taxi_processing_mock.create_event_handler.times_called == 4

    # passport has not idempotency and it will fail at this situation in real
    # will fixed in PASSP-35136
    passport_internal_mock.set_commit_response(
        {'status': 'error', 'errors': ['track.invalid_state']},
    )
    taxi_processing_mock.set_http_status_code(200)
    taxi_processing_mock.set_response({'event_id': 'abc123'})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 4
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.commit_handler.times_called == 2
    assert response.json() == {
        'status': 'FAILED',
        'support_url': '',
        'hint': 'Неизвестная ошибка',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_processing_has_fall_double_request_ok(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        product,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
        params={'product': product},
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params '
        'FROM bank_applications.registration_applications '
        'WHERE application_id=%s;',
        [application_id],
    )
    records = list(cursor)

    assert len(records) == 1
    assert records[0][0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert passport_internal_mock.submit_handler.times_called == 1

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    headers = common.headers_wo_buid_w_idempotency()
    taxi_processing_mock.set_http_status_code(500)
    taxi_processing_mock.set_response({})
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )
    assert response.status_code == 500
    assert passport_internal_mock.commit_handler.times_called == 1
    # default retry count
    assert taxi_processing_mock.create_event_handler.times_called == 4

    # passport has not idempotency and it will fail at this situation in real
    # but we check this like after deploy PASSP-35136
    taxi_processing_mock.set_http_status_code(200)
    taxi_processing_mock.set_response({'event_id': 'abc123'})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 5
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.commit_handler.times_called == 2
    assert response.json() == {'status': 'OK'}
    assert taxi_processing_mock.payloads[2][1] == {
        'buid': common.DEFAULT_YANDEX_BUID,
        'kind': 'update',
        'client_ip': common.SOME_IP,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'type': 'REGISTRATION',
        'yuid': common.DEFAULT_YANDEX_UID,
        'product': product,
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('application_id,code', [('', '123'), ('123', '')])
async def test_empty_param(taxi_bank_applications, application_id, code):
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': code},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_invalid_application_id(taxi_bank_applications):
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': '1-2-3-4-5', 'code': '123'},
    )
    assert response.status_code == 400


async def test_submit_code_history_table(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
        bank_userinfo_mock,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'SMS_CODE_SENT',
        '{"agreement_version":0,"phone":"'
        + common.DEFAULT_PHONE
        + f'","phone_id":"2","track_id":"{common.TRACK_ID}"'
        + '}',
        update_idempotency_token=None,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=common.headers_wo_buid_w_idempotency(),
        json={'application_id': application_id, 'code': '123'},
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params, yandex_uid, '
        'submitted_form, update_idempotency_token, status_text '
        'FROM bank_applications.registration_applications '
        'WHERE application_id=%s;',
        [application_id],
    )
    records = list(cursor)
    assert len(records) == 1
    assert records[0][0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'track_id': common.TRACK_ID,
    }
    assert records[0][1] == common.DEFAULT_YANDEX_UID
    assert records[0][2] == {'phone': common.DEFAULT_PHONE}
    assert records[0][3] != ''
    assert records[0][4] == 'PROCESSING'
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 3
    assert records_history[1][0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'track_id': common.TRACK_ID,
    }
    assert records_history[1][2] == {'phone': common.DEFAULT_PHONE}
    assert records_history[1][3] is not None
    assert records_history[1][4] == 'SMS_CODE_SENT'
    assert records[0] == records_history[2][:5]


@pytest.mark.parametrize(
    'delete_or_not, rewrite_or_not, header, value, status_code',
    [
        (False, False, '', '', 200),
        (True, False, 'X-Yandex-UID', '', 401),
        (False, True, 'X-Yandex-UID', '', 401),
        (True, False, 'X-YaBank-SessionStatus', '', 401),
        (False, True, 'X-YaBank-SessionStatus', 'not_confirmed', 401),
        (True, False, 'X-YaBank-SessionUUID', '', 401),
        (False, True, 'X-YaBank-SessionUUID', '', 401),
    ],
)
async def test_submit_code_not_authorized(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
        bank_userinfo_mock,
        delete_or_not,
        rewrite_or_not,
        header,
        value,
        status_code,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'SMS_CODE_SENT',
        '{"agreement_version":0,"phone":"'
        + common.DEFAULT_PHONE
        + f'","phone_id":"2","track_id":"{common.TRACK_ID}"'
        + '}',
        update_idempotency_token=None,
    )

    headers = common.headers_wo_buid_w_idempotency()
    if delete_or_not:
        headers.pop(header)
    if rewrite_or_not:
        headers[header] = value
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123'},
    )

    assert response.status_code == status_code


async def test_registration_submit_code_wrong_user_id(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
        bank_userinfo_mock,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'SMS_CODE_SENT',
        '{"agreement_version":0,"phone":"'
        + common.DEFAULT_PHONE
        + f'","phone_id":"2","track_id":"{common.TRACK_ID}"'
        + '}',
        update_idempotency_token=None,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=common.headers_wo_buid_w_idempotency(),
        json={'application_id': application_id, 'code': '123'},
    )
    assert response.status_code == 200

    headers = common.headers_wo_buid_w_idempotency()
    headers['X-Yandex-UID'] = 'trap'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123'},
    )
    assert response.status_code == 404


@pytest.mark.config(
    BANK_APPLICATIONS_SUBMIT_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.now(MOCK_NOW)
async def test_submit_code_nok_from_passport(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        testpoint,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    assert taxi_processing_mock.create_event_handler.times_called == 1

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': SOME_PHONE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }

    headers = common.headers_wo_buid_w_idempotency()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'

    passport_internal_mock.set_commit_response(
        {'status': 'nok', 'errors': ('error', 'error2')},
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAILED',
        'hint': 'Неизвестная ошибка',
        'support_url': '',
    }
    application = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application.status == 'PASSPORT_ERROR_SUBMIT_SMS'
    assert application.error == 'Passport commit errors(error,error2)'

    passport_internal_mock.set_commit_response(
        {'status': 'ok', 'track_id': common.TRACK_ID},
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/submit_code',
        headers=headers,
        json={'application_id': application_id, 'code': '123456'},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}

    application = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application.status == 'PROCESSING'
    assert application.error is None
