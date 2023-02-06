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
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    ALLOWED_PIN_CHECK_FAILS_COUNT=3,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreCheckPinTestCase(RestoreBaseTestCase, CommonTestsMixin,
                              AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = RESTORE_STEP_CHECK_PIN

    default_url = '/1/bundle/restore/pin/check/'

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                         secure_phone_number=TEST_PHONE, user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
                         phone_confirmation_is_confirmed=True,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            secure_phone_number=secure_phone_number,
            user_entered_phone_number=user_entered_phone_number,
            phone_confirmation_is_confirmed=phone_confirmation_is_confirmed,
        )
        super(RestoreCheckPinTestCase, self).set_track_values(**params)

    def query_params(self, pin=TEST_PIN, **kwargs):
        return dict(
            pin=pin,
        )

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_PHONE_AND_2FA_FACTOR)

    def test_phone_not_confirmed_fails(self):
        """Телефон не был подтвержден"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=False)

    def test_pin_check_counter_in_track_overflow_fails(self):
        """Переполнен счетчик проверок пина в треке"""
        self.set_track_values(pin_check_errors_count=3)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['pin.check_limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='pin.check_limit_exceeded',
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                pin_checks_count='3',
            ),
        ])

    def test_restore_method_no_more_available_fails(self):
        """Способ восстановления более недоступен"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                # Обычный, не 2ФА, аккаунт
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
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
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                is_hint_masked='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_phone_suitable_for_restore_changed_fails(self):
        """Изменился телефон на аккаунте - нельзя проверить пин-код"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
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
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_pin_check_counter_in_account_overflow_fails(self):
        """Переполнен счетчик проверок пина в аккаунте"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                    'account.totp.failed_pin_checks_count': 3,
                },
                pin_status=True,
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['pin.check_limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            last_restore_method_step=RESTORE_STEP_CHECK_PIN,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='pin.check_limit_exceeded',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_incorrect_pin_fails(self):
        """Введён некорректный пин"""
        userinfo_response = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
            },
            pin_status=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['pin.not_matched'],
            pin_checks_left=2,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            failed_pins=[TEST_PIN],
            pin_check_errors_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_PIN,
        )
        self.check_pin_check_counter(expected_value=1)
        self.env.event_logger.assert_event_is_logged('action', 'pin_check_update')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='pin.not_matched',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                pin_checks_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_incorrect_pin_same_value_fails(self):
        """Введён тот же некорректный пин второй раз, счетчики не обновляются"""
        userinfo_response = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
                'account.totp.failed_pin_checks_count': 1,
            },
            pin_status=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)
        self.set_track_values(
            failed_pins=[TEST_PIN],
            pin_check_errors_count=1,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['pin.not_matched'],
            pin_checks_left=2,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            last_restore_method_step=RESTORE_STEP_CHECK_PIN,
        )
        self.check_pin_check_counter(expected_value=1)
        self.env.event_logger.assert_event_is_logged('action', 'pin_check_update')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='pin.not_matched',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                pin_checks_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_incorrect_pin_other_value_fails(self):
        """Введён другой некорректный пин, счетчики обновляются"""
        userinfo_response = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
                'account.totp.failed_pin_checks_count': 1,
            },
            pin_status=False,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)
        self.set_track_values(
            failed_pins=[TEST_PIN],
            pin_check_errors_count=1,
        )

        resp = self.make_request(self.query_params(pin=TEST_PIN_2), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['pin.not_matched'],
            pin_checks_left=1,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            failed_pins=[TEST_PIN, TEST_PIN_2],
            pin_check_errors_count=2,
            last_restore_method_step=RESTORE_STEP_CHECK_PIN,
        )
        self.check_pin_check_counter(expected_value=2)
        self.env.event_logger.assert_event_is_logged('action', 'pin_check_update')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='pin.not_matched',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                pin_checks_count='2',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_correct_pin_ok(self):
        """Введён правильный пин, счетчик в аккаунте сбрасывается"""
        userinfo_response = self.default_userinfo_response(
            with_password=False,
            attributes={
                'account.2fa_on': '1',
                'account.totp.failed_pin_checks_count': 1,
            },
            pin_status=True,
            phone=TEST_PHONE,
            is_phone_secure=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)
        self.set_track_values(
            failed_pins=[TEST_PIN],
            pin_check_errors_count=1,
            last_restore_method_step=RESTORE_STEP_CHECK_2FA_FORM,
        )

        resp = self.make_request(self.query_params(pin=TEST_PIN_2), headers=self.get_headers())

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            restore_state=RESTORE_STATE_METHOD_PASSED,
            is_strong_password_policy_required=False,
            last_restore_method_step=RESTORE_STEP_CHECK_PIN,
        )
        self.check_pin_check_counter(expected_value=0)
        self.env.event_logger.assert_event_is_logged('action', 'pin_check_update')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                suitable_restore_methods=','.join(USUAL_2FA_RESTORE_METHODS),
                current_restore_method=RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
                pin_checks_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
