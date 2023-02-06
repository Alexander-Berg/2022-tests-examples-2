# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_HINT,
    RESTORE_METHOD_PHONE,
    RESTORE_STATE_METHOD_PASSED,
    RESTORE_STATE_METHOD_SELECTED,
)
from passport.backend.core.models.phones.faker import assert_secure_phone_bound
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import format_code_by_3


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    SMS_VALIDATION_MAX_CHECKS_COUNT=2,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreConfirmPhoneTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                  AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'confirm_phone'

    default_url = '/1/bundle/restore/phone/confirm/'

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_PHONE,
                         phone_confirmation_code=TEST_VALIDATION_CODE,
                         secure_phone_number=TEST_PHONE, user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            secure_phone_number=secure_phone_number,
            user_entered_phone_number=user_entered_phone_number,
        )
        if phone_confirmation_code:
            params['phone_confirmation_code'] = str(phone_confirmation_code)
        super(RestoreConfirmPhoneTestCase, self).set_track_values(**params)

    def query_params(self, code=TEST_VALIDATION_CODE, **kwargs):
        return dict(
            code=code,
        )

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_PHONE)

    def test_phone_no_validation_code_sent_fails(self):
        """На телефон не высылался код подтверждения"""
        self.track_invalid_state_case(phone_confirmation_code=None)

    def test_phone_already_confirmed_fails(self):
        """Телефон уже подтвержден"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=True)

    def test_phone_restore_no_more_available_fails(self):
        """Восстановление по телефону более недоступно для аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def test_phone_suitable_for_restore_changed_fails(self):
        """Изменился телефон на аккаунте - нельзя подтвердить"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['phone.changed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.changed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def base_code_check_error_case(self, error_code, set_track_kwargs=None, code=TEST_VALIDATION_CODE,
                                   expected_track_kwargs=None):
        """Общий код тестов ошибки проверки кода"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(**(set_track_kwargs or {}))

        resp = self.make_request(self.query_params(code=code), headers=self.get_headers())

        self.assert_error_response(
            resp,
            [error_code],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            **(expected_track_kwargs or {})
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error=error_code,
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_confirmations_limit_exceeded_fails(self):
        """Превышено число проверок кода в треке"""
        self.base_code_check_error_case(
            'confirmations_limit.exceeded',
            code=TEST_VALIDATION_CODE_2,
            set_track_kwargs=dict(
                phone_confirmation_sms_count=1,
                phone_confirmation_confirms_count=2,
            ),
        )

    def test_code_invalid_fails(self):
        """Введен невалидный код"""
        self.base_code_check_error_case(
            'code.invalid',
            code=TEST_VALIDATION_CODE_2,
            set_track_kwargs=dict(phone_confirmation_sms_count=1),
            expected_track_kwargs=dict(
                phone_confirmation_confirms_count=1,
            ),
        )

    def test_code_valid_restore_method_phone_passed_ok(self):
        """Введен валидный код, восстановление по телефону пройдено"""
        userinfo = self.default_userinfo_response(
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo,
        )
        self.env.db.serialize(userinfo)
        self.set_track_values(phone_confirmation_sms_count=1)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            is_strong_password_policy_required=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                code_checks_count='1',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                _exclude=['operation_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=TEST_DEFAULT_UID,
            phone_attributes={
                'id': TEST_PHONE_ID,
                'number': TEST_PHONE,
                'created': TEST_PHONE_ACTION_DEFAULT_DATE,
                'bound': TEST_PHONE_ACTION_DEFAULT_DATE,
                'confirmed': DatetimeNow(),  # Подновили время подтверждения
                'secured': TEST_PHONE_ACTION_DEFAULT_DATE,
            },
        )

    def test_code_valid_on_second_attempt_ok(self):
        """Правильный код введен со второй попытки"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_confirmation_sms_count=1,
            phone_confirmation_confirms_count=1,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=2,
            is_strong_password_policy_required=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                code_checks_count='2',
                is_hint_masked='1',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                _exclude=['operation_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_code_valid_restore_method_phone_and_pin_not_passed_ok(self):
        """Введен валидный код, 2ФА-восстановление не пройдено до конца"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            phone_confirmation_sms_count=1,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                code_checks_count='1',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                _exclude=['operation_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_called_code_valid_restore_method_phone_passed_ok(self):
        """
        Код продиктован в телефон.
        Введен валидный код.
        Восстановление по телефону пройдено.
        """
        userinfo = self.default_userinfo_response(
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo,
        )
        self.env.db.serialize(userinfo)
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
            phone_call_session_id='123',
            phone_confirmation_calls_count=1,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code='123 456',
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            country='ru',
        )

        resp = self.make_request(
            self.query_params(code='123456'),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            is_strong_password_policy_required=False,
            phone_confirmation_confirms_count_limit_reached=False,
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_first_checked=TimeNow(),
            phone_confirmation_last_checked=TimeNow(),
        )
        suitable_restore_methods = ','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed_by_call',
                suitable_restore_methods=suitable_restore_methods,
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=suitable_restore_methods,
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                code_checks_count='1',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                _exclude=['operation_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=suitable_restore_methods,
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
            ),
        ])
        self.env.antifraud_logger.assert_has_written(
            [
                self.env.antifraud_logger.entry(
                    'base',
                    channel='pharma',
                    sub_channel='dev',
                    status='OK',
                    external_id='track-{}'.format(self.track_id),
                    scenario='restore',
                    uid=str(TEST_DEFAULT_UID),
                    phone_confirmation_method='by_call',
                    request_path='/1/bundle/restore/phone/confirm/',
                    request='auth',
                    user_phone=TEST_PHONE,  # e164
                ),
            ],
        )

        self.assert_blackbox_userinfo_called()
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=TEST_DEFAULT_UID,
            phone_attributes={
                'id': TEST_PHONE_ID,
                'number': TEST_PHONE,
                'created': TEST_PHONE_ACTION_DEFAULT_DATE,
                'bound': TEST_PHONE_ACTION_DEFAULT_DATE,
                'confirmed': DatetimeNow(),  # Подновили время подтверждения
                'secured': TEST_PHONE_ACTION_DEFAULT_DATE,
            },
        )

    def test_code_with_delimiters_ok(self):
        """Введен валидный код с дефисами"""
        userinfo = self.default_userinfo_response(
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo,
        )
        self.env.db.serialize(userinfo)
        self.set_track_values(phone_confirmation_sms_count=1)

        resp = self.make_request(
            self.query_params(
                code=format_code_by_3(str(TEST_VALIDATION_CODE)),
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
