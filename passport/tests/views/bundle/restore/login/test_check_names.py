# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_LOGIN_RESTORE
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.test_base_data import TEST_AVATAR_URL_TEMPLATE
from passport.backend.api.views.bundle.restore.login.controllers import (
    RESTORE_STATE_ACCOUNTS_FOUND,
    RESTORE_STATE_PHONE_CONFIRMED,
    RESTORE_STATE_SUBMITTED,
)
from passport.backend.core.counters import login_restore_counter
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .test_base import (
    CommonTestsMixin,
    LoginRestoreBaseTestCase,
)


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    BLACKBOX_URL='localhost',
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckNamesTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'check_names'

    default_url = '/1/bundle/restore/login/check_names/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreCheckNamesTestCase, self).setUp()
        self.http_query_args = dict(
            track_id=self.track_id,
            firstname=TEST_DEFAULT_FIRSTNAME,
            lastname=TEST_DEFAULT_LASTNAME,
        )

    def set_track_values(self, restore_state=RESTORE_STATE_PHONE_CONFIRMED,
                         process_name=PROCESS_LOGIN_RESTORE, **params):
        super(LoginRestoreCheckNamesTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_last_send_at=str(int(time.time())),
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_confirms_count=1,
            **params
        )

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_SUBMITTED}
    test_action_not_required_options = {'restore_state': RESTORE_STATE_ACCOUNTS_FOUND}

    def test_names_check_failed(self):
        """По ФИО не найдены подходящие аккаунты"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request(query_args=dict(firstname='wrong name'))

        self.assert_error_response(resp, ['compare.not_matched'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='compare.not_matched',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

        # Оба счетчика увеличиваются
        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 1)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 1)

    def test_names_check_passed(self):
        """По ФИО найдены подходящие аккаунты"""
        self.set_track_values()
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 50
        accounts = [
            self.build_account(
                uid=1,
                login=TEST_DEFAULT_LOGIN,
                display_login=TEST_USER_ENTERED_LOGIN,
                has_plus=True,
            ),
            self.build_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                firstname=TEST_DEFAULT_FIRSTNAME_INEXACT,
                lastname=TEST_DEFAULT_LASTNAME_INEXACT,
                alias_type='pdd',
            ),
            self.build_account(uid=3, firstname='123', lastname='345'),
            self.build_account(
                uid=4,
                disabled_status=ACCOUNT_DISABLED_ON_DELETION,
                deletion_started_at=deletion_started_at,
            ),
            self.build_account(
                uid=5,
                disabled_status=ACCOUNT_DISABLED,
            ),
            self.build_account(
                uid=7,
                login=TEST_LITE_LOGIN,
                firstname=TEST_DEFAULT_FIRSTNAME_INEXACT,
                lastname=TEST_DEFAULT_LASTNAME_INEXACT,
                alias_type='lite',
                has_plus=True,
            ),
            self.build_account(
                uid=12,
                login='child',
                display_login='the child',
                has_family=True,
                is_child=True,
            )
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            accounts=[
                dict(
                    login=TEST_USER_ENTERED_LOGIN,
                    uid=TEST_DEFAULT_UID,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=1,
                    has_plus=True,
                ),
                dict(
                    login=TEST_LITE_LOGIN,
                    uid=7,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=5,
                    has_plus=True,
                ),
                dict(
                    login=TEST_PDD_LOGIN,
                    uid=TEST_PDD_UID,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=7,
                ),
                dict(
                    login=TEST_DEFAULT_LOGIN,
                    uid=4,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=1,
                ),
                dict(
                    login=TEST_DEFAULT_LOGIN,
                    uid=5,
                    default_avatar=TEST_AVATAR_KEY,
                    avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'normal'),
                    primary_alias_type=1,
                ),
            ],
        )
        self.assert_track_updated(
            restore_state=RESTORE_STATE_ACCOUNTS_FOUND,
            user_entered_firstname=TEST_DEFAULT_FIRSTNAME,
            user_entered_lastname=TEST_DEFAULT_LASTNAME,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                uids=','.join(['1', '7', str(TEST_PDD_UID), '4', '5'])
            ),
        ])
        self.assert_blackbox_called(uids=[1, 3, 4, 5, 7, 12, TEST_PDD_UID])

        # Оба счетчика не увеличиваются
        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
