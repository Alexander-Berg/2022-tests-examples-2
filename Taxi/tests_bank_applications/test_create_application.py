import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

AGREEMENT_TEXT = {'agreement_text': 'Privet {}'}
REGISTRATION_CONFIG = {'response_with_masked_phone': True}
MOCK_NOW = '2021-09-28T19:31:00+00:00'


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
@pytest.mark.parametrize('forms_response_code', [200, 400, 500])
async def test_create_registration_application_with_header(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        forms_response_code,
        pgsql,
):
    bank_forms_mock.set_http_status_code(forms_response_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': 'REGISTRATION'},
    )

    assert response.status_code == 200
    db_helpers.check_asserts_registration(
        pgsql,
        response,
        'REGISTRATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms if forms_response_code == 200 else None,
    )

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert bank_forms_mock.get_registration_form_handler.times_called == 1


@pytest.mark.parametrize('userinfo_error_code', [400, 500])
async def test_create_registration_application_userinfo_error(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_userinfo_mock,
        userinfo_error_code,
):
    bank_userinfo_mock.set_http_status_code(userinfo_error_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': 'REGISTRATION'},
    )
    assert response.status_code == userinfo_error_code
    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert bank_userinfo_mock.create_buid_handler.times_called == 1


@pytest.mark.config(
    BANK_APPLICATIONS_REGISTRATION_CONFIG={
        'response_with_masked_phone': False,
    },
)
async def test_create_registration_application_without_masked_phone(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': 'REGISTRATION'},
    )

    assert response.status_code == 200
    assert response.json()['form'] == {
        'phone': bank_forms_mock.forms['REGISTRATION']['phone'],
    }

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert bank_forms_mock.get_registration_form_handler.times_called == 1


@pytest.mark.parametrize('locale', ['unknown', 'en'])
async def test_create_simplified_application(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        locale,
):
    headers = common.default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        json={'type': 'SIMPLIFIED_IDENTIFICATION'},
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.parametrize('locale', ['unknown', 'en'])
async def test_create_simplified_application_esia(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        locale,
):
    headers = common.default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        json={'type': 'SIMPLIFIED_IDENTIFICATION_ESIA'},
        headers=headers,
    )
    assert response.status_code == 400


async def test_create_simplified_application_without_header(
        taxi_bank_applications,
):
    headers = common.headers_without_buid()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': 'SIMPLIFIED_IDENTIFICATION'},
    )

    assert response.status_code == 401


async def test_create_simplified_application_empty_header(
        taxi_bank_applications,
):
    headers = common.default_headers()
    headers['X-Yandex-BUID'] = ''
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': 'SIMPLIFIED_IDENTIFICATION'},
    )

    assert response.status_code == 401


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
@pytest.mark.parametrize(
    'application_type', ['REGISTRATION', 'DIGITAL_CARD_ISSUE'],
)
async def test_create_application_with_no_agreement_in_config(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        application_type,
):
    bank_agreements_mock.set_agreements({})
    headers = (
        common.headers_without_buid()
        if application_type == 'REGISTRATION'
        else (
            headers_good_card_exp()
            if application_type == 'DIGITAL_CARD_ISSUE'
            else common.default_headers()
        )
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': application_type},
    )

    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 0


async def test_create_application_idempotency_one(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    application_type = 'REGISTRATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    assert application_id == response.json()['application_id']
    assert response.json()['status'] == 'CREATED'

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )

    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    assert application_id == response.json()['application_id']
    assert response.json()['status'] == 'PROCESSING'

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'FAILED'},
    )

    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    assert application_id != response.json()['application_id']
    assert response.json()['status'] == 'CREATED'

    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'SUCCESS'},
    )

    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 409


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
async def test_create_application_registration_with_previous_failed(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    application_type = 'REGISTRATION'
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'FAILED',
    )
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] != application_id
    db_helpers.check_asserts_registration(
        pgsql,
        response,
        application_type,
        bank_agreements_mock.agreements,
        forms=bank_forms_mock.forms,
    )


def headers_good_card_exp():
    headers = common.headers_with_idempotency()
    headers['X-YaBank-SessionUUID'] = common.OK
    return headers


def headers_bad_card_exp():
    headers = common.headers_with_idempotency()
    headers['X-YaBank-SessionUUID'] = common.NOK
    return headers


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
async def test_create_application_digital_card(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers_good_card_exp(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'CREATED'

    db_helpers.check_asserts(
        pgsql,
        response,
        application_type,
        bank_agreements_mock.agreements,
        forms=None,
    )


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
async def test_fail_create_application_digital_card_due_exp(
        taxi_bank_applications, mockserver,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers_bad_card_exp(),
        json={'type': application_type},
    )
    assert response.status_code == 404


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
async def test_create_application_digital_card_new_idempotency_token(
        taxi_bank_applications,
        pgsql,
        application_status,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    headers = headers_good_card_exp()
    headers['X-Idempotency-Token'] = '67754336-d4d1-43c1-aadb-cabd06674ea7'
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        application_status,
        True,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'CREATED'
    assert application_id != response.json()['application_id']


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
@pytest.mark.parametrize('application_status', ['CREATED', 'PROCESSING'])
async def test_create_application_digital_card_old_idempotency_token(
        taxi_bank_applications,
        pgsql,
        application_status,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        application_status,
        True,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers_good_card_exp(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == application_status
    assert application_id == response.json()['application_id']


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
async def test_create_application_digital_card_old_idemp_token_failed_status(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'FAILED',
        True,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers_good_card_exp(),
        json={'type': application_type},
    )
    assert response.status_code == 409


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
async def test_create_application_digital_card_old_idemp_token_success_status(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'SUCCESS',
        True,
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers_good_card_exp(),
        json={'type': application_type},
    )
    assert response.status_code == 200


async def test_create_application_history_table(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
):
    application_type = 'REGISTRATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    assert record[1] == common.DEFAULT_YANDEX_UID

    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 1
    assert record[:2] == records_history[0][:2]


@pytest.mark.now(MOCK_NOW)
async def test_create_application_after_send_code_history_table(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
        mocked_time,
):
    application_type = 'REGISTRATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    assert record[1] == common.DEFAULT_YANDEX_UID
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 1
    assert record[:2] == records_history[0][:2]

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )

    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'deny_resend_until': deny_resend_until,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'track_id': common.TRACK_ID,
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 4
    assert record[:2] == records_history[3][:2]

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200

    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 5
    assert record[:2] == records_history[4][:2]


async def test_create_application_processing_has_fall_double(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    taxi_processing_mock.set_http_status_code(500)
    taxi_processing_mock.set_response({})
    application_type = 'REGISTRATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 500
    # default retry count
    assert taxi_processing_mock.create_event_handler.times_called == 3

    taxi_processing_mock.set_http_status_code(200)
    taxi_processing_mock.set_response({'event_id': 'abc123'})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 4
    res = response.json()
    res.pop('application_id')
    res.pop('agreement')
    assert res == {'status': 'CREATED', 'form': {'phone': '+70001002020'}}


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
async def test_insert_conflict(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        pgsql,
        testpoint,
):
    headers = common.headers_without_buid()

    @testpoint('insert conflict')
    def _insert_same_applicaton(data):
        db_helpers.add_application_registration(
            pgsql, headers['X-Yandex-UID'], 'SUCCESS',
        )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': 'REGISTRATION'},
    )

    assert response.status_code == 409
    assert bank_forms_mock.get_registration_form_handler.times_called == 1
