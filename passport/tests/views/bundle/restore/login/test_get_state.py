# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import PROCESS_LOGIN_RESTORE
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.test_base_data import TEST_AVATAR_URL_TEMPLATE
from passport.backend.api.views.bundle.restore.login.controllers import (
    RESTORE_STATE_ACCOUNTS_FOUND,
    RESTORE_STATE_PHONE_CONFIRMED,
    RESTORE_STATE_SUBMITTED,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_base import LoginRestoreBaseTestCase


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    BLACKBOX_URL='localhost',
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreGetStateTestCase(LoginRestoreBaseTestCase):

    restore_step = 'get_state'

    default_url = '/1/bundle/restore/login/get_state/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreGetStateTestCase, self).setUp()
        self.http_query_args = dict(
            track_id=self.track_id,
        )

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED, retpath=TEST_RETPATH,
                         process_name=PROCESS_LOGIN_RESTORE, is_captcha_checked=True,
                         is_captcha_recognized=True, **params):
        super(LoginRestoreGetStateTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            retpath=TEST_RETPATH,
            is_captcha_required=True,
            is_captcha_checked=is_captcha_checked,
            is_captcha_recognized=is_captcha_recognized,
            **params
        )

    def test_phone_not_submitted(self):
        """Телефон еще не вводился, либо вводился неподходящий"""
        self.set_track_values()

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            restore_state=RESTORE_STATE_SUBMITTED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed'),
        ])

    def test_phone_submitted(self):
        """Подходящий телефон был введен, код отправлен"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            is_code_sent=True,
            is_phone_confirmed=False,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_SUBMITTED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed', number=TEST_PHONE_OBJECT.masked_format_for_statbox),
        ])

    def test_phone_confirmed(self):
        """Телефон был подтвержден"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            is_code_sent=True,
            is_phone_confirmed=True,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed', number=TEST_PHONE_OBJECT.masked_format_for_statbox),
        ])
        self.assert_blackbox_called()

    def test_phone_confirmed_and_no_longer_suitable(self):
        """Телефон более не подходит для восстановления логина"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
        )
        accounts = [
            self.build_account(secured_at=None),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['phone_secure.not_found'],
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            is_code_sent=True,
            is_phone_confirmed=True,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone_secure.not_found',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_matching_names_entered(self):
        """Введены подходящие ФИО"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_ACCOUNTS_FOUND,
            user_entered_firstname=TEST_DEFAULT_FIRSTNAME,
            user_entered_lastname=TEST_DEFAULT_LASTNAME,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            is_code_sent=True,
            is_phone_confirmed=True,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            accounts=[
                dict(
                    login=TEST_DEFAULT_LOGIN,
                    uid=TEST_DEFAULT_UID,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=1,
                ),
            ],
            restore_state=RESTORE_STATE_ACCOUNTS_FOUND,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                uids=str(TEST_DEFAULT_UID),
            ),
        ])
        self.assert_blackbox_called()

    def test_names_no_longer_valid(self):
        """Введенные имена более не подходят для найденных аккаунтов"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            restore_state=RESTORE_STATE_ACCOUNTS_FOUND,
            user_entered_firstname=TEST_DEFAULT_FIRSTNAME,
            user_entered_lastname=TEST_DEFAULT_LASTNAME,
        )
        accounts = [
            self.build_account(firstname='Leopold', lastname='Leopoldovich'),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['compare.not_matched'],
            track_id=self.track_id,
            retpath=TEST_RETPATH,
            is_code_sent=True,
            is_phone_confirmed=True,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            restore_state=RESTORE_STATE_ACCOUNTS_FOUND,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='compare.not_matched',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()
