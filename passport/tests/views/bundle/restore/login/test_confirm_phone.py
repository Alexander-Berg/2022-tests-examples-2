# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import PROCESS_LOGIN_RESTORE
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.restore.login.controllers import (
    RESTORE_STATE_ACCOUNTS_FOUND,
    RESTORE_STATE_PHONE_CONFIRMED,
    RESTORE_STATE_SUBMITTED,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_base import (
    CommonTestsMixin,
    LoginRestoreBaseTestCase,
)


TEST_SMS_VALIDATION_MAX_CHECKS_COUNT = 4


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_SMS_VALIDATION_MAX_CHECKS_COUNT,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreConfirmPhoneByCallTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'confirm_phone'

    default_url = '/1/bundle/restore/login/confirm_phone/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreConfirmPhoneByCallTestCase, self).setUp()
        self.http_query_args = dict(
            track_id=self.track_id,
            code=TEST_VALIDATION_CODE,
        )

    def setup_statbox_templates(self):
        super(LoginRestoreConfirmPhoneByCallTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'phone_confirmed',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            _exclude=['uid', 'phone_id', 'operation_id'],
            _inherit_from=['phone_confirmed', 'local_base'],
        )

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED,
                         process_name=PROCESS_LOGIN_RESTORE, **params):
        super(LoginRestoreConfirmPhoneByCallTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=str(int(time.time())),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            phone_confirmation_calls_count=1,
            phone_call_session_id='123',
            **params
        )

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_ACCOUNTS_FOUND}
    test_action_not_required_options = {'restore_state': RESTORE_STATE_PHONE_CONFIRMED}

    def test_code_checks_limit_exceeded(self):
        """Слишком много неуспешных проверок кода, переполнен счетчик в треке"""
        self.set_track_values(phone_confirmation_confirms_count=TEST_SMS_VALIDATION_MAX_CHECKS_COUNT)
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['confirmations_limit.exceeded'])
        self.assert_track_updated(
            phone_confirmation_confirms_count_limit_reached='1',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'enter_code',
                _exclude=['action'],  # action не пишется в лог, если не дошли до проверки кода
                error='confirmations_limit.exceeded',
                operation='confirm',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='confirmations_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_invalid_code(self):
        """Некорректный код"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request(query_args=dict(code=TEST_VALIDATION_CODE_2))

        self.assert_error_response(resp, ['code.invalid'])
        self.assert_track_updated(
            phone_confirmation_is_confirmed=False,
            phone_confirmation_confirms_count=1,
            phone_confirmation_confirms_count_limit_reached=False,
            phone_confirmation_first_checked=TimeNow(),
            phone_confirmation_last_checked=TimeNow(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'enter_code',
                error='code.invalid',
                good='0',
                operation='confirm',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'finished_with_error',
                error='code.invalid',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_confirm_phone_passed(self):
        """Телефон успешно подтвержден"""
        self.set_track_values(scenario='scenario1')
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.assert_track_updated(
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
            phone_confirmation_confirms_count_limit_reached=False,
            phone_confirmation_first_checked=TimeNow(),
            phone_confirmation_last_checked=TimeNow(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'enter_code',
                good='1',
                operation='confirm',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                code_checks_count='1',
            ),
        ])
        self.env.antifraud_logger.assert_has_written(
            [
                self.env.antifraud_logger.entry(
                    'base',
                    channel='pharma',
                    sub_channel='dev',
                    status='OK',
                    scenario='scenario1',
                    external_id='track-{}'.format(self.track_id),
                    phone_confirmation_method='by_call',
                    request_path='/1/bundle/restore/login/confirm_phone/',
                    request='auth',
                    user_phone=TEST_PHONE,  # e164
                ),
            ],
        )
        self.assert_blackbox_called()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_SMS_VALIDATION_MAX_CHECKS_COUNT,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreConfirmPhoneBySmsTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'confirm_phone'

    default_url = '/1/bundle/restore/login/confirm_phone/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreConfirmPhoneBySmsTestCase, self).setUp()
        self.http_query_args = dict(
            track_id=self.track_id,
            code=TEST_VALIDATION_CODE,
        )

    def setup_statbox_templates(self):
        super(LoginRestoreConfirmPhoneBySmsTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'phone_confirmed',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            _exclude=['uid', 'phone_id', 'operation_id'],
            _inherit_from=['phone_confirmed', 'local_base'],
        )

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED,
                         process_name=PROCESS_LOGIN_RESTORE, **params):
        super(LoginRestoreConfirmPhoneBySmsTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=str(int(time.time())),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,
            **params
        )

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_ACCOUNTS_FOUND}
    test_action_not_required_options = {'restore_state': RESTORE_STATE_PHONE_CONFIRMED}

    def test_code_checks_limit_exceeded(self):
        """Слишком много неуспешных проверок кода, переполнен счетчик в треке"""
        self.set_track_values(phone_confirmation_confirms_count=TEST_SMS_VALIDATION_MAX_CHECKS_COUNT)
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['confirmations_limit.exceeded'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='confirmations_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_invalid_code(self):
        """Некорректный код"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request(query_args=dict(code=TEST_VALIDATION_CODE_2))

        self.assert_error_response(resp, ['code.invalid'])
        self.assert_track_updated(
            phone_confirmation_is_confirmed=False,
            phone_confirmation_confirms_count=1,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='code.invalid',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_confirm_phone_passed(self):
        """Телефон успешно подтвержден"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.assert_track_updated(
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                code_checks_count='1',
            ),
        ])
        self.assert_blackbox_called()
