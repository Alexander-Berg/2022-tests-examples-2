# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from passport.backend.api.common.processes import PROCESS_VOLUNTARY_PASSWORD_CHANGE
from passport.backend.api.test.mixins import OAuthTestMixin
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base import BaseChangePasswordTestCase
from .base_test_data import *


@nottest
@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    PASSPORT_SUBDOMAIN='passport-test',
)
class BaseChangePasswordOptionalLogoutTestCase(BaseChangePasswordTestCase):

    def setUp(self):
        super(BaseChangePasswordOptionalLogoutTestCase, self).setUp()

        self.default_url = '/1/bundle/change_password/optional_logout/?consumer=dev'
        self.http_query_args = dict(track_id=self.track_id)

    def setup_track(self, uid=TEST_UID, login=TEST_LOGIN, origin=None, retpath=None):
        super(BaseChangePasswordOptionalLogoutTestCase, self).setup_track(uid, login, origin, retpath)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_VOLUNTARY_PASSWORD_CHANGE
            track.is_password_change = False  # TODO
            track.session = 'session'

    def check_db(self, centraldb_query_count=0, sharddb_query_count=1, global_logout=False,
                 web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False,
                 uid=TEST_UID, dbshard='passportdbshard1'):
        timenow = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(dbshard), sharddb_query_count)

        if global_logout:
            self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=uid,
                              db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'account.global_logout_datetime', uid=uid,
                                      db=dbshard)

        if web_sessions_revoked:
            self.env.db.check('attributes', 'revoker.web_sessions', timenow, uid=uid, db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'revoker.web_sessions', uid=uid, db=dbshard)

        if tokens_revoked:
            self.env.db.check('attributes', 'revoker.tokens', timenow, uid=uid, db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'revoker.tokens', uid=uid, db=dbshard)

        if app_passwords_revoked:
            self.env.db.check('attributes', 'revoker.app_passwords', timenow, uid=uid, db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'revoker.app_passwords', uid=uid, db=dbshard)

        self.env.db.check_missing('attributes', 'password.update_datetime', uid=uid, db=dbshard)
        self.env.db.check('attributes', 'password.quality', '3:%s' % TEST_PASSWORD_QUALITY, uid=uid, db=dbshard)
        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=uid, db=dbshard)
        ok_(eav_pass_hash == TEST_OLD_SERIALIZED_PASSWORD)

    def check_log_entries(self, uid=TEST_UID, login=TEST_LOGIN, old_session_uids=None, global_logout=False,
                          web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False,
                          uids_count=None, origin=None, expected_auth_log_records=None, with_check_cookies=False):
        expected_log_entries = []

        if global_logout:
            expected_log_entries.append(
                self.historydb_entry(uid, 'info.glogout', TimeNow()),
            )
        if tokens_revoked:
            expected_log_entries.append(
                self.historydb_entry(uid, 'info.tokens_revoked', TimeNow()),
            )
        if web_sessions_revoked:
            expected_log_entries.append(
                self.historydb_entry(uid, 'info.web_sessions_revoked', TimeNow()),
            )
        if app_passwords_revoked:
            expected_log_entries.append(
                self.historydb_entry(uid, 'info.app_passwords_revoked', TimeNow()),
            )

        if expected_log_entries:
            expected_log_entries.extend([
                self.historydb_entry(uid, 'action', 'change_password_optional_logout'),
                self.historydb_entry(uid, 'consumer', 'dev'),
                self.historydb_entry(uid, 'user_agent', 'curl'),
            ])

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            expected_log_entries,
        )

        # Одна запись в auth-log об обновлении сессии
        expected_log_records = expected_auth_log_records or [
            [
                ('uid', str(uid)),
                ('status', 'ses_update'),
                ('type', authtypes.AUTH_TYPE_WEB),
                ('client_name', 'passport'),
                ('useragent', TEST_USER_AGENT),
                ('ip_from', TEST_USER_IP),
            ],
        ] if web_sessions_revoked or global_logout else []
        eq_(self.env.auth_handle_mock.call_count, len(expected_log_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_log_records,
        )

        extra_kwargs = {}
        if origin:
            extra_kwargs['origin'] = origin
        expected_log_entries = [
            self.env.statbox.entry('optional_logout_submitted', uid=str(uid), **extra_kwargs),
        ]
        if with_check_cookies:
            expected_log_entries.append(self.env.statbox.entry('check_cookies'))

        if global_logout:
            expected_log_entries += [
                self.env.statbox.entry('account_global_logout_datetime', uid=str(uid)),
            ]

        if web_sessions_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_web_sessions', uid=str(uid)),
            ]

        if tokens_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_app_tokens', uid=str(uid)),
            ]

        if app_passwords_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_app_passwords', uid=str(uid)),
            ]

        if web_sessions_revoked or global_logout:
            auth_entry = self.env.statbox.entry('cookie_set', uid=str(uid), input_login=login, **extra_kwargs)
            if old_session_uids:
                auth_entry.update(old_session_uids=old_session_uids)

            if uids_count:
                auth_entry.update(uids_count=uids_count)

            expected_log_entries.append(auth_entry)

        optional_logout_entry = self.env.statbox.entry(
            'optional_logout_committed',
            uid=str(uid),
            web_sessions_revoked=tskv_bool(web_sessions_revoked or global_logout),
            tokens_revoked=tskv_bool(tokens_revoked or global_logout),
            app_passwords_revoked=tskv_bool(app_passwords_revoked or global_logout),
            **extra_kwargs
        )
        expected_log_entries.append(optional_logout_entry)

        self.env.statbox.assert_equals(expected_log_entries)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='change_password_voluntarily',
            track_id=self.track_id,
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'optional_logout_submitted',
            _inherit_from='local_base',
            action='optional_logout_submitted',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _inherit_from='local_base',
            _exclude=['consumer'],
            mode='any_auth',
            action='cookie_set',
            cookie_version=str(settings.BLACKBOX_SESSION_VERSION),
            input_login=TEST_LOGIN,
            ttl='0',
            captcha_passed='1',
            ip_country='us',
            session_method='edit',
            uids_count='1',
            person_country='ru',
            authid=TEST_AUTH_ID,
        )
        self.env.statbox.bind_entry(
            'optional_logout_committed',
            _inherit_from='local_base',
            action='optional_logout_committed',
        )

        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from='local_base',
            _exclude=['mode', 'track_id'],
            operation='updated',
            event='account_modification',
        )
        self.env.statbox.bind_entry(
            'logout',
            _inherit_from='account_modification',
            new=DatetimeNow(convert_to_datetime=True),
            old=TEST_GLOBAL_LOGOUT_DATETIME,
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'account_revoker_app_passwords',
            _inherit_from='logout',
            entity='account.revoker.app_passwords',
        )
        self.env.statbox.bind_entry(
            'account_revoker_app_tokens',
            _inherit_from='logout',
            entity='account.revoker.tokens',
        )
        self.env.statbox.bind_entry(
            'account_revoker_web_sessions',
            _inherit_from='logout',
            entity='account.revoker.web_sessions',
        )
        self.env.statbox.bind_entry(
            'account_global_logout_datetime',
            _inherit_from='logout',
            entity='account.global_logout_datetime',
        )


@istest
class ChangePasswordOptionalLogoutTestCase(BaseChangePasswordOptionalLogoutTestCase, OAuthTestMixin):

    def test_missing_process__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = None

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_strong_password_policy__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(subscribed_to=[67])
            ),
        )

        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_error_response(rv, ['action.not_required'])

    def test_nothing_logouted__ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.get_expected_response())
        # Куку не меняли
        eq_(self.env.blackbox.get_requests_by_method('editsession'), [])

        self.check_db(sharddb_query_count=0)
        self.check_log_entries(old_session_uids=str(TEST_UID), with_check_cookies=True)
        self.check_track_ok()
        self.assert_sessionid_called()

    def test_origin_written_to_statbox__with_retpath__ok(self):
        """Запись origin в статбокс, отдача retpath"""
        self.setup_track(origin=TEST_ORIGIN, retpath=TEST_RETPATH)

        rv = self.make_request()

        self.assert_ok_response(rv, **self.get_expected_response(retpath=TEST_RETPATH))

        self.check_log_entries(old_session_uids=str(TEST_UID), origin=TEST_ORIGIN, with_check_cookies=True)

    def test_revoke_all_tokens__ok(self):
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='1',
                revoke_app_passwords='1',
            ),
        )

        self.assert_ok_response(rv, **self.get_expected_response())
        # Куку не меняли
        eq_(self.env.blackbox.get_requests_by_method('editsession'), [])
        self.check_db(
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
        )

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
            with_check_cookies=True,
        )
        self.check_track_ok()

    def test_revoke_web_sessions__ok(self):
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='1',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called(call_index=1)
        self.check_db(
            global_logout=False,
            web_sessions_revoked=True,
            tokens_revoked=False,
            app_passwords_revoked=False,
        )

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=False,
            web_sessions_revoked=True,
            tokens_revoked=False,
            app_passwords_revoked=False,
            with_check_cookies=True,
        )
        self.check_track_ok()
        self.assert_sessionid_called()

    def test_revoke_everything__ok(self):
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='1',
                revoke_tokens='1',
                revoke_app_passwords='1',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called(call_index=1)
        self.check_db(
            global_logout=True,
        )

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=True,
            with_check_cookies=True,
        )
        self.check_track_ok()

    def test_ok__specific_create_session_params(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(
                    aliases={
                        'portal': TEST_LOGIN,
                        'yandexoid': 'yastaff_login',  # Яндексоид
                    },
                    attributes={
                        'person.country': TEST_USER_COUNTRY,
                        'person.timezone': TEST_USER_TIMEZONE,
                        'person.language': TEST_USER_LANGUAGE,
                        'password.encrypted': TEST_OLD_SERIALIZED_PASSWORD,
                    },
                    dbfields={
                        'password_quality.quality.uid': TEST_PASSWORD_QUALITY,
                        'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
                        'subscription.suid.668': '1',  # Бетатестер
                        'subscription.login.668': 'yastaff_login',
                    },
                )
            ),
        )
        rv = self.make_request(query_args=dict(revoke_web_sessions=True))

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db(web_sessions_revoked=True)
        self.check_log_entries(old_session_uids=str(TEST_UID), web_sessions_revoked=True, with_check_cookies=True)
        self.check_track_ok()
        request = self.env.blackbox.get_requests_by_method('editsession')[0]
        request.assert_query_contains(
            {
                'is_yastaff': '1',
                'is_betatester': '1',
            },
        )

    def test_pdd_change_password__good_way__ok(self):
        self.setup_blackbox_responses(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            emails=[
                self.create_native_email(TEST_PDD_LOGIN_PART, TEST_DOMAIN),
            ],
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            domain=TEST_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1', domain=TEST_DOMAIN),
        )
        self.setup_track(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN)

        rv = self.make_request(query_args=dict(revoke_web_sessions=True))

        self.assert_ok_response_with_cookies(
            rv,
            self.get_expected_response(
                display_login=TEST_PDD_LOGIN,
                is_pdd=True,
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
            ),
            default_uid=TEST_PDD_UID,
        )
        self.assert_editsession_called(uid=TEST_PDD_UID, call_index=2)
        self.check_db(
            uid=TEST_PDD_UID,
            dbshard='passportdbshard2',
            web_sessions_revoked=True,
        )
        self.check_log_entries(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            old_session_uids=str(TEST_PDD_UID),
            web_sessions_revoked=True,
            with_check_cookies=True,
        )
        self.check_track_ok()
        self.assert_sessionid_called()

    def test_change_password_for_multiple_users_session(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ip=TEST_USER_IP,
                    age=TEST_COOKIE_AGE,
                    time=TEST_COOKIE_TIMESTAMP,
                    authid=TEST_OLD_AUTH_ID,
                    **self.account_kwargs()
                ),
                uid=12345,
                login='other_login',
            ),
        )

        rv = self.make_request(query_args=dict(revoke_web_sessions=True))

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db(web_sessions_revoked=True)
        self.check_track_ok()
        self.assert_sessionid_called()
        self.check_log_entries(
            old_session_uids='%d,12345' % TEST_UID,
            web_sessions_revoked=True,
            uids_count='2',
            expected_auth_log_records=[
                self.build_auth_log_entry('ses_update', TEST_UID),
                self.build_auth_log_entry('ses_update', 12345),
            ],
            with_check_cookies=True,
        )

    def test_change_password_for_multiple_users_session_one_invalid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ip=TEST_USER_IP,
                    age=TEST_COOKIE_AGE,
                    time=TEST_COOKIE_TIMESTAMP,
                    authid=TEST_OLD_AUTH_ID,
                    **self.account_kwargs()
                ),
                uid=12345,
                login='other_login',
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request(query_args=dict(revoke_web_sessions=True))

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db(web_sessions_revoked=True)
        self.check_track_ok()
        self.assert_sessionid_called()
        self.check_log_entries(
            old_session_uids='%d,12345' % TEST_UID,
            uids_count='2',
            web_sessions_revoked=True,
            with_check_cookies=True,
        )
