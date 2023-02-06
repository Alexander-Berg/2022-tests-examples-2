import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'
REGISTRATION_CONFIG = {'response_with_masked_phone': True}


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
@pytest.mark.parametrize('forms_response_code', [200, 400, 500])
@pytest.mark.parametrize(
    'product, accepted_plus_offer, has_ya_plus',
    [(common.PRODUCT_WALLET, True, False), (common.PRODUCT_PRO, False, True)],
)
async def test_registration_create_application_with_header(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        forms_response_code,
        pgsql,
        product,
        accepted_plus_offer,
        has_ya_plus,
):
    headers = common.headers_without_buid()
    if has_ya_plus:
        headers['X-YaTaxi-Pass-Flags'] = 'ya-plus'
    bank_forms_mock.set_http_status_code(forms_response_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=headers,
        params={
            'product': product,
            'accepted_plus_offer': accepted_plus_offer,
        },
    )

    assert response.status_code == 200

    other_additional_params = {
        'accepted_plus_offer': accepted_plus_offer,
        'has_ya_plus': has_ya_plus,
    }
    db_helpers.check_asserts_registration(
        pgsql,
        response,
        'REGISTRATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms if forms_response_code == 200 else None,
        other_additional_params=other_additional_params,
        product=product,
    )

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert bank_forms_mock.get_registration_form_handler.times_called == 1


@pytest.mark.parametrize('userinfo_error_code', [400, 500])
async def test_registration_create_application_userinfo_error(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_userinfo_mock,
        userinfo_error_code,
):
    bank_userinfo_mock.set_http_status_code(userinfo_error_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == userinfo_error_code
    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert bank_userinfo_mock.create_buid_handler.times_called == 1


@pytest.mark.config(
    BANK_APPLICATIONS_REGISTRATION_CONFIG={
        'response_with_masked_phone': False,
    },
)
async def test_registration_create_application_without_masked_phone(
        taxi_bank_applications,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    assert response.json()['form'] == {
        'phone': bank_forms_mock.forms['REGISTRATION']['phone'],
    }

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert bank_forms_mock.get_registration_form_handler.times_called == 1


@pytest.mark.experiments3(
    filename='bank_digital_card_feature_experiments.json',
)
async def test_registration_create_application_with_no_agreement_in_config(
        taxi_bank_applications, bank_agreements_mock, taxi_processing_mock,
):
    bank_agreements_mock.set_agreements({})
    headers = common.headers_without_buid()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )

    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 0


async def test_registration_create_application_idempotency_one(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 409


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
async def test_registration_create_application_reg_with_previous_failed(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    application_type = 'REGISTRATION'
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        application_type,
        'FAILED',
        False,
    )
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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


async def test_registration_create_application_history_table(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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
async def test_registration_create_application_after_send_code_history_table(
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
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
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


async def test_registration_create_application_processing_has_fall_double(
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
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 500
    # default retry count
    assert taxi_processing_mock.create_event_handler.times_called == 3

    taxi_processing_mock.set_http_status_code(200)
    taxi_processing_mock.set_response({'event_id': 'abc123'})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 4
    res = response.json()
    res.pop('application_id')
    res.pop('agreement')
    assert res == {'status': 'CREATED', 'form': {'phone': '+70001002020'}}


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
async def test_registration_insert_conflict(
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
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 409
    assert bank_forms_mock.get_registration_form_handler.times_called == 1


async def test_registration_create_application_with_other_product(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    first_application_id = response.json()['application_id']

    record = db_helpers.get_app_with_add_params_reg(
        pgsql, first_application_id,
    )
    assert record[0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    assert record[1] == common.DEFAULT_YANDEX_UID
    assert record[2] == common.STATUS_CREATED
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, first_application_id,
    )
    assert len(records_history) == 1
    assert record[:2] == records_history[0][:2]

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
        params={'product': 'PRO'},
    )
    assert response.status_code == 200
    second_application_id = response.json()['application_id']
    assert first_application_id != second_application_id

    record = db_helpers.get_app_with_add_params_reg(
        pgsql, first_application_id,
    )
    assert record[2] == common.STATUS_CANCELLED
    record = db_helpers.get_app_with_add_params_reg(
        pgsql, second_application_id,
    )
    assert record[0] == {
        'agreement_version': 0,
        'phone': common.DEFAULT_PHONE,
        'phone_id': '2',
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, second_application_id,
    )
    assert len(records_history) == 1
    assert record[:2] == records_history[0][:2]


async def test_registration_create_application_with_other_product_processing(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        bank_agreements_mock,
        bank_forms_mock,
        passport_internal_mock,
):
    db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING',
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
        params={'product': 'PRO'},
    )
    assert response.status_code == 409


@pytest.mark.config(
    BANK_USERINFO_USER_AGENT_TO_PRODUCT={
        '__default__': 'WALLET',
        'taximeter': 'PRO',
    },
    BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG,
)
@pytest.mark.parametrize(
    'request_application, expected_product',
    [
        ('platform=android,app_name=taximeter', 'PRO'),
        ('platform=android,app_name=yandex_go', 'WALLET'),
    ],
)
async def test_registration_create_application_without_product(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        request_application,
        expected_product,
):
    headers = common.headers_without_buid()
    headers['X-Request-Application'] = request_application

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )

    assert response.status_code == 200

    db_helpers.check_asserts_registration(
        pgsql,
        response,
        'REGISTRATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms,
        other_additional_params={},
        product=expected_product,
    )


@pytest.mark.config(
    BANK_USERINFO_USER_AGENT_TO_PRODUCT={'__default__': ''},
    BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG,
)
async def test_registration_create_application_broken_default_config(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    headers = common.headers_without_buid()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )

    assert response.status_code == 200

    db_helpers.check_asserts_registration(
        pgsql,
        response,
        'REGISTRATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms,
        other_additional_params={},
        product='WALLET',
    )
