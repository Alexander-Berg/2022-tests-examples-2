# pylint: disable=too-many-lines

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'
SUPPORT_URL = {'support_url': 'http://support.ya/'}
DEFAULT_ADDITIONAL_PARAMS = (
    '{"agreement_version":0,"phone":"%s","phone_id":"2"}'
    % common.DEFAULT_PHONE
)
APPLICATION_TYPE = 'REGISTRATION'


@pytest.mark.parametrize(
    'platform, gps_package_name_send', [('android', True), ('ios', False)],
)
@pytest.mark.now(MOCK_NOW)
async def test_send_code_happy_with_history(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        pgsql,
        mocked_time,
        platform,
        gps_package_name_send,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    headers['X-Request-Application'] = (
        'app_brand=yataxi,'
        'app_name=Yandex.Bank,'
        'app_ver1=0,'
        'app_ver2=15,'
        'app_ver3=0,'
        'bank_sdk=true,'
        f'platform={platform},'
        'sdk_ver1=0,'
        'sdk_ver2=15,'
        'sdk_ver3=0'
    )
    passport_internal_mock.gps_package_name_send = gps_package_name_send

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
    }
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 3
    assert record[:2] == records_history[2][:2]

    mocked_time.sleep(1)
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    passport_internal_mock.update_ts_in_submit_response()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': '+79990001122'},
    )
    assert response.status_code == 200
    record_new = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record_new[0] == {
        'agreement_version': 0,
        'phone': '+79990001122',
        'track_id': common.TRACK_ID,
        'deny_resend_until': deny_resend_until,
    }
    assert passport_internal_mock.submit_handler.times_called == 2
    assert passport_internal_mock.limits_handler.times_called == 2
    records_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(records_history) == 6
    record[0]['phone'] = record_new[0]['phone']
    del record[0]['phone_id']
    assert record[:2] == records_history[4][:2]
    assert record_new[:2] == records_history[5][:2]


@pytest.mark.now(MOCK_NOW)
async def test_send_code_happy(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        pgsql,
        mocked_time,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    headers['X-Request-Application'] = (
        'app_brand=yataxi,'
        'app_name=Unknown.Bank.Missing.Match,'
        'app_ver1=0,'
        'app_ver2=15,'
        'app_ver3=0,'
        'bank_sdk=true,'
        'platform=android,'
        'sdk_ver1=0,'
        'sdk_ver2=15,'
        'sdk_ver3=0'
    )
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
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'track_id': common.TRACK_ID,
    }
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_this_phone_more_try(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        mocked_time,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    for i in range(0, passport_internal_mock.time_to_resend):
        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/send_code',
            headers=headers,
            json={'application_id': application_id, 'phone_id': '2'},
        )
        assert response.status_code == 200
        assert response.json() == {
            'status': 'OK',
            'seconds': passport_internal_mock.time_to_resend - i,
            'action': 'RETRY',
        }
        record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
        assert record[0] == {
            'agreement_version': 0,
            'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
            'phone_id': '2',
            'track_id': common.TRACK_ID,
            'deny_resend_until': deny_resend_until,
        }
        assert passport_internal_mock.submit_handler.times_called == 1
        assert passport_internal_mock.limits_handler.times_called == i + 1
        mocked_time.sleep(1)
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    passport_internal_mock.update_ts_in_submit_response()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={
            'application_id': application_id,
            'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'track_id': common.TRACK_ID,
        'deny_resend_until': deny_resend_until,
    }
    assert passport_internal_mock.submit_handler.times_called == 2
    assert (
        passport_internal_mock.limits_handler.times_called
        == passport_internal_mock.time_to_resend + 1
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_this_phone_after_recreate(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        mocked_time,
):
    prev_application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'FAILED',
    )
    del bank_forms_mock.forms[APPLICATION_TYPE]['passport_phone_id']
    del bank_forms_mock.forms[APPLICATION_TYPE]['masked_phone']
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']
    assert prev_application_id != application_id
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={
            'application_id': application_id,
            'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'track_id': common.TRACK_ID,
        'deny_resend_until': deny_resend_until,
        'accepted_plus_offer': False,
        'has_ya_plus': False,
    }
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_other_phone_more_try(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        mocked_time,
):
    passport_internal_mock.sms_remained = 10
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
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
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'track_id': common.TRACK_ID,
        'deny_resend_until': deny_resend_until,
    }
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1

    i = 0
    for (phone, seconds, times) in [
            ('+79990001122', 5, 2),
            ('+79990001122', 4, 2),
            ('+79990001133', 5, 3),
    ]:
        i += 1
        mocked_time.sleep(1)
        if seconds == 5:
            deny_resend_until = common.get_current_ts_with_shift(
                mocked_time, passport_internal_mock.time_to_resend,
            )
            passport_internal_mock.update_ts_in_submit_response()

        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/send_code',
            headers=headers,
            json={'application_id': application_id, 'phone': phone},
        )
        assert response.status_code == 200
        assert response.json() == {
            'status': 'OK',
            'seconds': seconds,
            'action': 'RETRY',
        }
        record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
        assert record[0] == {
            'agreement_version': 0,
            'phone': phone,
            'track_id': common.TRACK_ID,
            'deny_resend_until': deny_resend_until,
        }
        assert passport_internal_mock.submit_handler.times_called == times
        assert passport_internal_mock.limits_handler.times_called == i + 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_other_phone_then_phone_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        mocked_time,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': '+79990001122'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'RETRY',
    }
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'phone': '+79990001122',
        'track_id': common.TRACK_ID,
        'deny_resend_until': deny_resend_until,
    }
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert response.status_code == 400
    assert passport_internal_mock.submit_handler.times_called == 1
    assert passport_internal_mock.limits_handler.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_other_phone_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '3'},
    )
    assert response.status_code == 400
    assert passport_internal_mock.submit_handler.times_called == 0
    assert passport_internal_mock.limits_handler.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_happy_use_all_tries(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        pgsql,
        bank_userinfo_mock,
        mocked_time,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'

    for i in range(0, 2, 1):
        deny_resend_until = common.get_current_ts_with_shift(
            mocked_time, passport_internal_mock.time_to_resend,
        )
        passport_internal_mock.update_ts_in_submit_response()
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

        record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
        assert record[0] == {
            'agreement_version': 0,
            'deny_resend_until': deny_resend_until,
            'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
            'phone_id': '2',
            'track_id': common.TRACK_ID,
        }

        assert passport_internal_mock.submit_handler.times_called == i + 1
        assert passport_internal_mock.limits_handler.times_called == i + 1
        mocked_time.sleep(passport_internal_mock.time_to_resend)

    deny_resend_until = common.get_current_ts_with_shift(
        mocked_time, passport_internal_mock.time_to_resend,
    )
    passport_internal_mock.update_ts_in_submit_response()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'seconds': passport_internal_mock.time_to_resend,
        'action': 'SUPPORT',
        'support_url': SUPPORT_URL['support_url'],
    }
    record = db_helpers.get_app_with_add_params_reg(pgsql, application_id)
    assert record[0] == {
        'agreement_version': 0,
        'deny_resend_until': deny_resend_until,
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
        'phone_id': '2',
        'track_id': common.TRACK_ID,
    }


@pytest.mark.parametrize(
    'send_code_body',
    [{'phone_id': '2', 'phone': '89013212121'}, {'phone_id': '23'}, {}],
)
async def test_send_code_bad_request_phone_phone_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        send_code_body,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    application_id_body = {'application_id': application_id}

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json=application_id_body.update(send_code_body),
    )

    assert response.status_code == 400


PHONE_BLOCKED = 'phone.blocked'
ERRORS_TO_TANKER_KEY = {
    '__default__': {'tanker_key': 'passport.default_error'},
    PHONE_BLOCKED: {'tanker_key': 'passport.phone.blocked'},
}


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.config(
    BANK_APPLICATIONS_SEND_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.parametrize(
    'locale, hint',
    [('ru', 'Телефон заблокирован'), ('en', 'Phone is blocked')],
)
async def test_send_code_submit_fail(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
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

    passport_internal_mock.set_submit_response(
        {'status': 'nok', 'errors': [PHONE_BLOCKED]},
    )

    headers = common.headers_without_buid()
    headers['X-Request-Language'] = locale
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAILED',
        'hint': hint,
        'support_url': SUPPORT_URL['support_url'],
    }


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.config(
    BANK_APPLICATIONS_SEND_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.parametrize(
    'locale, hint', [('ru', 'Неизвестная ошибка'), ('en', 'Unknown error')],
)
async def test_send_code_submit_unknown_passport_error(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
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

    passport_internal_mock.set_submit_response(
        {'status': 'nok', 'errors': ['some_error']},
    )

    headers = common.headers_without_buid()
    headers['X-Request-Language'] = locale
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAILED',
        'hint': hint,
        'support_url': SUPPORT_URL['support_url'],
    }


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_submit_fail_wo_errors(
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

    passport_internal_mock.set_submit_response({'status': 'nok'})

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )

    assert response.status_code == 500


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_send_code_submit_internal_error(
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

    passport_internal_mock.set_submit_status_code(500)
    passport_internal_mock.set_submit_response({})

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )

    assert response.status_code == 500


@pytest.mark.now(MOCK_NOW)
async def test_send_code_set_registration_form(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    some_phone = '+79001231212'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    assert bank_forms_mock.get_registration_form_handler.times_called == 1
    application_id = response.json()['application_id']

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == 200
    assert bank_forms_mock.set_registration_form_handler.times_called == 1

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    assert response.json()['form'] == {'phone': some_phone}
    assert bank_forms_mock.get_registration_form_handler.times_called == 2


REGISTRATION_CONFIG = {'response_with_masked_phone': True}


@pytest.mark.config(BANK_APPLICATIONS_REGISTRATION_CONFIG=REGISTRATION_CONFIG)
@pytest.mark.now(MOCK_NOW)
async def test_send_code_set_registration_form_failed(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    some_phone = '+79001231212'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    bank_forms_mock.set_http_status_code(500)

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == 200

    bank_forms_mock.set_http_status_code(200)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    assert response.json()['form'] == {
        'phone_id': bank_forms_mock.forms[APPLICATION_TYPE][
            'passport_phone_id'
        ],
        'masked_phone': bank_forms_mock.forms[APPLICATION_TYPE][
            'masked_phone'
        ],
    }


@pytest.mark.config(
    BANK_APPLICATIONS_REGISTRATION_CONFIG={
        'response_with_masked_phone': False,
    },
)
@pytest.mark.now(MOCK_NOW)
async def test_send_code_set_registration_form_failed_without_masked_phone(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    some_phone = '+79001231212'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    bank_forms_mock.set_http_status_code(500)

    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == 200

    bank_forms_mock.set_http_status_code(200)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )
    assert response.status_code == 200
    assert response.json()['form'] == {
        'phone': bank_forms_mock.forms[APPLICATION_TYPE]['phone'],
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'application_id,phone', [('', '+79999999999'), ('123', '')],
)
async def test_empty_param(taxi_bank_applications, application_id, phone):
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': phone},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_invalid_application_id(taxi_bank_applications):
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': '1-2-3-4-5', 'phone': '+79123456789'},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_empty_locale(taxi_bank_applications):
    headers = common.headers_without_buid()
    headers.pop('X-Request-Language')
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': 'some_id', 'phone': '+79999999999'},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_invalid_phone_format(taxi_bank_applications):
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': 'some_id', 'phone': '79999999999'},
    )
    assert response.status_code == 400


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
@pytest.mark.now(MOCK_NOW)
async def test_send_code_not_authorized(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        delete_or_not,
        rewrite_or_not,
        header,
        value,
        status_code,
):
    some_phone = '+79001231212'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    headers = common.headers_without_buid()
    if delete_or_not:
        headers.pop(header)
    if rewrite_or_not:
        headers[header] = value
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == status_code


async def test_registration_send_code_wrong_user_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
):
    some_phone = '+79001231212'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    headers = common.headers_without_buid()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == 200

    headers = common.headers_without_buid()
    headers['X-Yandex-UID'] = 'trap'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone': some_phone},
    )

    assert response.status_code == 404


@pytest.mark.config(
    BANK_APPLICATIONS_SEND_CODE_PASSPORT_ERRORS_TANKER_KEYS=(
        ERRORS_TO_TANKER_KEY
    ),
)
@pytest.mark.now(MOCK_NOW)
async def test_send_code_nok_from_passport(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        passport_internal_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        pgsql,
        mocked_time,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'CREATED',
        DEFAULT_ADDITIONAL_PARAMS,
        update_idempotency_token=None,
    )
    headers = common.headers_without_buid()
    headers['User-Agent'] = 'Mozilla/5.0 (compatible; BankRobot/0.01)'
    headers['X-Request-Application'] = (
        'app_brand=yataxi,'
        'app_name=Unknown.Bank.Missing.Match,'
        'app_ver1=0,'
        'app_ver2=15,'
        'app_ver3=0,'
        'bank_sdk=true,'
        'platform=android,'
        'sdk_ver1=0,'
        'sdk_ver2=15,'
        'sdk_ver3=0'
    )
    passport_internal_mock.set_submit_response(
        {'status': 'nok', 'errors': ('error', 'error2')},
    )
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
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
    assert application.status == 'PASSPORT_ERROR_SEND_SMS'
    assert application.error == 'Passport submit errors(error,error2)'
    passport_internal_mock.set_submit_response(
        {'status': 'ok', 'track_id': common.TRACK_ID},
    )
    passport_internal_mock.update_ts_in_submit_response()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/send_code',
        headers=headers,
        json={'application_id': application_id, 'phone_id': '2'},
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'OK', 'action': 'RETRY', 'seconds': 5}
    application = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application.status == 'SMS_CODE_SENT'
    assert application.error is None
