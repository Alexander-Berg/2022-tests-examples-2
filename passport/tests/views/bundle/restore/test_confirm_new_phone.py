# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.counters.change_password_counter import get_per_phone_number_buckets
from passport.backend.core.support_link_types import SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    SMS_VALIDATION_MAX_CHECKS_COUNT=2,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_PER_IP_COUNTER_LIMIT_FOR_SUPPORT_LINK=10,
    **mock_counters()
)
class RestoreConfirmNewPhoneTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                     AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'confirm_new_phone'

    default_url = '/1/bundle/restore/new_phone/confirm/'

    account_validity_tests_extra_statbox_params = {
        'support_link_type': SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    }
    common_tests_mixin_extra_statbox_context = account_validity_tests_extra_statbox_params
    test_invalid_support_link_types = False
    require_enabled_account = False
    allow_missing_password_with_portal_alias = True

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_PASSED,
                         current_restore_method=RESTORE_METHOD_LINK,
                         phone_confirmation_code=TEST_VALIDATION_CODE,
                         phone_confirmation_phone_number=TEST_PHONE, user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                         support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            phone_confirmation_phone_number=phone_confirmation_phone_number,
            user_entered_phone_number=user_entered_phone_number,
            country='ru',
            # Сейчас привязка телефона возможна только при восстановлении по ссылке на ввод нового пароля
            support_link_type=support_link_type,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        if phone_confirmation_code:
            params['phone_confirmation_code'] = str(phone_confirmation_code)
        super(RestoreConfirmNewPhoneTestCase, self).set_track_values(**params)

    def query_params(self, code=TEST_VALIDATION_CODE, **kwargs):
        return dict(
            code=code,
        )

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_LINK)

    def test_new_phone_not_allowed_fails(self):
        """Процессом не предусмотрена привязка нового телефона"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.track_invalid_state_case(
            support_link_type=None,
            extra_response_params=self.base_expected_response(),
        )

    def test_phone_no_user_entered_phone_number_fails(self):
        """Телефон не сохранен в треке"""
        self.track_invalid_state_case(user_entered_phone_number=None)

    def test_phone_no_phone_confirmation_phone_number_fails(self):
        """Телефон не сохранен в треке"""
        self.track_invalid_state_case(phone_confirmation_phone_number=None)

    def test_phone_no_validation_code_sent_fails(self):
        """На телефон не высылался код подтверждения"""
        self.track_invalid_state_case(phone_confirmation_code=None)

    def test_phone_already_confirmed_fails(self):
        """Телефон уже подтвержден"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=True)

    def test_phone_is_compromised_fails(self):
        """Использованный номер телефона нельзя привязать как защищенный"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            support_link_type=None,
        )
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE)
        eq_(counter.get(TEST_PHONE), counter.limit)

        resp = self.make_request(
            self.query_params(),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['phone.compromised'],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        eq_(counter.get(TEST_PHONE), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.compromised',
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])

    def base_code_check_error_case(self, error_code, set_track_kwargs=None, code=TEST_VALIDATION_CODE,
                                   expected_track_kwargs=None):
        """Общий код тестов ошибки проверки кода"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(**(set_track_kwargs or {}))

        resp = self.make_request(self.query_params(code=code), headers=self.get_headers())

        self.assert_error_response(
            resp,
            [error_code],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            **(expected_track_kwargs or {})
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error=error_code,
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            ),
        ])
        self.assert_blackbox_userinfo_called()

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

    def test_code_valid_ok(self):
        """Введен валидный код"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(phone_confirmation_sms_count=1)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                code_checks_count='1',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                _exclude=['operation_id', 'phone_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            ),
        ])
        self.env.antifraud_logger.assert_has_written([])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_code_valid_on_second_attempt_ok(self):
        """Правильный код введен со второй попытки"""
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
            current_restore_method=RESTORE_METHOD_LINK,
            support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            phone_confirmation_sms_count=1,
            phone_confirmation_confirms_count=1,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=2,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'phone_confirmed',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                code_checks_count='2',
                confirmation_time=DatetimeNow(convert_to_datetime=True),
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                _exclude=['operation_id'],
            ),
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
