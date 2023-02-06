# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonTestsMixin,
    RestoreBaseTestCase,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_GPS_PACKAGE_NAME
from passport.backend.api.views.bundle.restore.base import (
    RESTORE_STATE_METHOD_SELECTED,
    RESTORE_STATE_SUBMIT_PASSED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_hosted_domains_response,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    **mock_counters()
)
class RestoreSubmitTestCase(RestoreBaseTestCase, CommonTestsMixin, AccountValidityTestsMixin):

    restore_step = 'submit'

    default_url = '/1/bundle/restore/submit/'

    is_uid_preset_in_track = False

    account_validity_tests_extra_statbox_params = {
        'captcha_check_count': '0',
    }

    def set_track_values(self, **params):
        params['uid'] = None
        super(RestoreSubmitTestCase, self).set_track_values(**params)

    def query_params(self, login=TEST_USER_ENTERED_LOGIN, retpath=None, gps_package_name=None):
        params = dict(
            login=login,
        )
        if retpath is not None:
            params['retpath'] = retpath
        if gps_package_name is not None:
            params['gps_package_name'] = gps_package_name
        return params

    def assert_track_updated(self, uid=TEST_DEFAULT_UID, login=TEST_DEFAULT_LOGIN,
                             user_entered_login=TEST_USER_ENTERED_LOGIN,
                             restore_state=RESTORE_STATE_SUBMIT_PASSED,
                             gps_package_name=None,
                             **data):
        super(RestoreSubmitTestCase, self).assert_track_updated(
            uid=str(uid),
            login=login,
            user_entered_login=user_entered_login,
            restore_state=restore_state,
            gps_package_name=gps_package_name,
            **data
        )

    def test_unexpected_valid_restore_state_fails(self):
        """Трек с установленным (даже корректным) состоянием восстановления не принимаем"""
        self.set_track_values(restore_state=RESTORE_STATE_METHOD_SELECTED)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_captcha_not_passed_fails(self):
        """Капча не пройдена"""
        self.set_track_values(is_captcha_recognized=False)
        self.env.blackbox.set_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['user.not_verified'],
            **self.base_expected_response()
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                captcha_check_count='0',
                # нет данных о логине, поэтому берем логин из формы; UID неизвестен
                login=TEST_USER_ENTERED_LOGIN,
                _exclude=['uid'],
            ),
        ])

    def test_with_phonenumber_alias_login_restore_not_available(self):
        """При использовании цифрового алиаса в качестве логина восстановление пока недоступно"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                self.default_userinfo_response(
                    aliases={
                        'portal': TEST_DEFAULT_LOGIN,
                        'phonenumber': TEST_PHONE_OBJECT.digital,
                    },
                    emails=TEST_EMAILS,
                    emails_native=False,
                    phone=TEST_PHONE,
                    is_phone_secure=True,
                ),
                # Второй запрос должен быть сделан с sid=restore
                self.default_userinfo_response(uid=None),
            ],
        )
        self.set_track_values(user_entered_login=None)

        resp = self.make_request(
            self.query_params(login=TEST_PHONE_LOCAL_FORMAT),
            self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            state='phone_alias_prohibited',
            **self.base_expected_response(user_entered_login=TEST_PHONE_LOCAL_FORMAT)
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(
            state='phone_alias_prohibited',
            is_phonenumber_alias_used_as_login='1',
        )
        self.env.statbox.assert_has_written([entry])
        self.env.blackbox.get_requests_by_method('userinfo')[1].assert_post_data_contains(
            {
                'method': 'userinfo',
                'login': TEST_PHONE_LOCAL_FORMAT,
                'sid': 'restore',
            },
        )

    def test_account_not_found_by_native_email(self):
        """Не нашли аккаунт по емейлу, сообщаем это (емейла может не быть, но может быть аккаунт с таким логином)"""
        self.env.blackbox.set_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_track_values(user_entered_login=None)

        native_email = TEST_USER_ENTERED_LOGIN + '@yandex.ru'
        resp = self.make_request(
            self.query_params(login=native_email),
            self.get_headers(),
        )

        self.assert_error_response(
            resp,
            errors=['account.not_found'],
            looks_like_yandex_email=True,
            **self.base_expected_response(user_entered_login=native_email)
        )
        self.assert_track_unchanged()

    def test_submit_passed(self):
        """Submit пройден"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)
        self.assert_track_updated()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed', captcha_check_count='0'),
        ])

    def test_submit_passed_with_retpath(self):
        """Submit пройден, retpath сохранен в трек"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(retpath=TEST_RETPATH), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)
        self.assert_track_updated(retpath=TEST_RETPATH)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed', captcha_check_count='0', retpath=TEST_RETPATH),
        ])

    def test_submit_passed_with_pdd_retpath_fixed(self):
        """Submit пройден, retpath для ПДД исправлен и сохранен в трек"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1', domain=TEST_PDD_DOMAIN),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(retpath=TEST_PDD_RETPATH, login=TEST_PDD_LOGIN),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_PDD_LOGIN)
        self.assert_track_updated(
            retpath=TEST_CLEANED_PDD_RETPATH,
            uid=str(TEST_PDD_UID),
            login=TEST_PDD_LOGIN,
            user_entered_login=TEST_PDD_LOGIN,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed',
                captcha_check_count='0',
                retpath=TEST_CLEANED_PDD_RETPATH,
                uid=str(TEST_PDD_UID),
                login=TEST_PDD_LOGIN,
            ),
        ])

    def test_submit_passed_with_gps_package_name(self):
        """Submit пройден, gps_package_name сохранен в трек"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(gps_package_name=TEST_GPS_PACKAGE_NAME), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)
        self.assert_track_updated(gps_package_name=TEST_GPS_PACKAGE_NAME)

    def test_submit_passed_with_login_from_suggest(self):
        """Submit пройден, использован логин из саджеста"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(suggested_logins=[TEST_USER_ENTERED_LOGIN])

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)
        self.assert_track_updated()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('passed', captcha_check_count='0', is_suggested_login='1'),
        ])

    def test_child_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(resp, track_id=self.track_id, user_entered_login=TEST_USER_ENTERED_LOGIN)

    def test_child_family_full_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID, uids=[1, 2, 3, 4]),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            errors=['family.max_capacity'],
            **self.base_expected_response(user_entered_login=TEST_USER_ENTERED_LOGIN)
        )

    def test_child_family_not_found_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.is_child': '1',
                    'account.last_child_family': TEST_FAMILY_ID,
                    'account.deletion_operation_started_at': time.time() - 60,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            blackbox_family_info_response(family_id=TEST_FAMILY_ID, exists=False),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            errors=['family.does_not_exist'],
            **self.base_expected_response(user_entered_login=TEST_USER_ENTERED_LOGIN)
        )
