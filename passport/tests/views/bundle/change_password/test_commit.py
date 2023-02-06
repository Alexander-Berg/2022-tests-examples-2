# -*- coding: utf-8 -*-
import base64
from datetime import timedelta
import json
import time

import ldap
import mock
from nose.tools import (
    assert_is_none,
    eq_,
    istest,
    nottest,
    ok_,
)
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    OAuthTestMixin,
    ProfileTestMixin,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SECOND_STEP_RFC_TOTP
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_ip_response,
    blackbox_create_pwd_hash_response,
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
    blackbox_test_pwd_hashes_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)

from .base import BaseChangePasswordTestCase
from .base_test_data import (
    FRODO_RESPONSE_FORBIDDEN_CHANGE_PASSWORD,
    FRODO_RESPONSE_OK,
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_COOKIE_AGE,
    TEST_COOKIE_TIMESTAMP,
    TEST_DIFFERENT_PHONE_NUMBER,
    TEST_DOMAIN,
    TEST_GLOBAL_LOGOUT_DATETIME,
    TEST_HOST,
    TEST_LOGIN,
    TEST_NEW_PASSWORD,
    TEST_NEW_PASSWORD_QUALITY,
    TEST_NOT_STRONG_PASSWORD,
    TEST_OLD_AUTH_ID,
    TEST_OLD_SERIALIZED_PASSWORD,
    TEST_ORIGIN,
    TEST_PASSWORD,
    TEST_PASSWORD_QUALITY,
    TEST_PASSWORD_QUALITY_VERSION,
    TEST_PDD_LOGIN,
    TEST_PDD_LOGIN_PART,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_SESSIONID,
    TEST_SSL_SESSIONID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COUNTRY,
    TEST_USER_IP,
    TEST_USER_LANGUAGE,
    TEST_USER_TIMEZONE,
    TEST_WEAK_PASSWORD,
)


TEST_OPERATION_TTL = timedelta(seconds=360)


@nottest
@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    YASMS_URL='http://localhost/',
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    PASSPORT_SUBDOMAIN='passport-test',
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class BaseChangePasswordCommitTestCase(
    AccountModificationNotifyTestMixin,
    BaseChangePasswordTestCase,
    ProfileTestMixin,
):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        super(BaseChangePasswordCommitTestCase, self).setUp()

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs()),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: False}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'checkip',
            blackbox_check_ip_response(True),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_OK)
        self.env.frodo.set_response_value(u'', u'')

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        self.default_url = '/1/bundle/change_password/commit/?consumer=dev'

        self.setup_profile_patches()

        self.http_query_args = dict(
            track_id=self.track_id,
            current_password=TEST_PASSWORD,
            password=TEST_NEW_PASSWORD,
            consumer='dev',
        )

        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.teardown_profile_patches()
        super(BaseChangePasswordCommitTestCase, self).tearDown()

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
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'phone_notification_sent',
            _inherit_from='local_base',
            action='change_password_notification.notification_sent',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            sms_id='1',
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
            ip_country='ru',
            session_method='edit',
            uids_count='1',
            person_country='ru',
            authid=TEST_AUTH_ID,
        )
        self.env.statbox.bind_entry(
            'analyzed_frodo',
            _inherit_from='local_base',
            action='analyzed_frodo',
            karma_prefix='7',
            is_karma_prefix_returned='1',
        )
        self.env.statbox.bind_entry(
            'changed_password',
            _inherit_from='local_base',
            action='changed_password',
            password_quality=str(TEST_NEW_PASSWORD_QUALITY),
            optional_logout_possible='1',
            old_authid=TEST_OLD_AUTH_ID,
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
            'clear_is_creating_required',
            _inherit_from='account_modification',
            sid='100',
            operation='removed',
            entity='subscriptions',
        )
        self.env.statbox.bind_entry(
            'clear_pwn_forced_changing_suspended_at',
            _inherit_from='account_modification',
            operation='deleted',
            entity='password.pwn_forced_changing_suspended_at',
            new='-',
            old=DatetimeNow(convert_to_datetime=True),
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

        self.env.statbox.bind_entry(
            'password_encrypted',
            _inherit_from='account_modification',
            entity='password.encrypted',
        )
        self.env.statbox.bind_entry(
            'password_encoding',
            _inherit_from='account_modification',
            entity='password.encoding_version',
            old=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT),
            new=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON),
        )
        self.env.statbox.bind_entry(
            'password_quality',
            _inherit_from='account_modification',
            entity='password.quality',
            old=str(TEST_PASSWORD_QUALITY),
            new=str(TEST_NEW_PASSWORD_QUALITY),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def get_expected_response(self, revoke_all=True, allow_select_revokers=True,
                              validation_method=u'captcha', *args, **kwargs):
        response = super(BaseChangePasswordCommitTestCase, self).get_expected_response(*args, **kwargs)
        if validation_method:
            response['validation_method'] = validation_method
            response['revokers'] = {
                'default': {
                    'tokens': revoke_all,
                    'web_sessions': revoke_all,
                    'app_passwords': revoke_all,
                },
                'allow_select': allow_select_revokers,
            }
        return response

    def expected_frodo_params(self, uid=TEST_UID, login=TEST_LOGIN, karma=0, **kwargs):
        params = {
            'uid': str(uid),
            'login': login,
            'from': '',
            'consumer': 'dev',
            'passwd': '15.0.14.0',
            'passwdex': '4.10.1.0',
            'v2_password_quality': '100',
            'v2_old_password_quality': str(TEST_PASSWORD_QUALITY),
            'hintqid': '',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': '',
            'fuid': '',
            'useragent': TEST_USER_AGENT,
            'host': TEST_HOST,
            'ip_from': TEST_USER_IP,
            'v2_ip': TEST_USER_IP,
            'valkey': '0000000000',
            'action': 'change_password_voluntarily',
            'xcountry': 'ru',
            'lang': 'ru',
            'v2_track_created': TimeNow(),
            'v2_account_country': TEST_USER_COUNTRY,
            'v2_account_language': TEST_USER_LANGUAGE,
            'v2_account_timezone': TEST_USER_TIMEZONE,
            'v2_accept_language': TEST_ACCEPT_LANGUAGE,
            'v2_account_karma': str(karma),
            'v2_is_ssl': '1',
            'v2_is_ssl_session_cookie_valid': '1',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_l': '0',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_has_cookie_my': '0',
            'v2_cookie_my_block_count': '',
            'v2_cookie_my_language': '',
            'v2_cookie_l_login': '',
            'v2_cookie_l_uid': '',
            'v2_cookie_l_timestamp': '',
            'v2_session_age': str(TEST_COOKIE_AGE),
            'v2_session_ip': TEST_USER_IP,
            'v2_session_create_timestamp': str(TEST_COOKIE_TIMESTAMP),
        }
        params.update(**kwargs)
        return EmptyFrodoParams(**params)

    def check_db(self, centraldb_query_count=0, sharddb_query_count=2, uid=TEST_UID,
                 check_password=True, global_logout=True,
                 web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False,
                 dbshard='passportdbshard1'):
        timenow = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(dbshard), sharddb_query_count)

        if global_logout:
            self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=uid, db=dbshard)
        else:
            self.env.db.check_missing('attributes', 'account.global_logout_datetime', uid=uid, db=dbshard)

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

        if check_password:
            self.env.db.check('attributes', 'password.update_datetime', timenow, uid=uid, db=dbshard)
            self.env.db.check('attributes', 'password.quality', '3:100', uid=uid, db=dbshard)
            self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=uid, db=dbshard)
            self.env.db.check_missing('attributes', 'password.is_creating_required', uid=uid, db=dbshard)

            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=uid, db=dbshard)
            if self.is_password_hash_from_blackbox:
                eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
            else:
                eq_(len(eav_pass_hash), 36)
                ok_(eav_pass_hash.startswith('1:'))
                ok_(eav_pass_hash != TEST_OLD_SERIALIZED_PASSWORD)

    def assert_frodo_not_called(self):
        eq_(len(self.env.frodo.requests), 0)

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_query_equals(self.expected_frodo_params(**kwargs))

    def check_captcha_statuses_on_error(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, False)
        eq_(track.is_captcha_checked, False)

    def assert_yasms_not_called(self):
        eq_(len(self.env.yasms.requests), 0)

    def check_sms_sent(self, uid=TEST_UID):
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry('phone_notification_sent'),
            entry_index=-2,
        )

        requests = self.env.yasms.requests
        requests[-1].assert_query_contains({
            'from_uid': str(uid),
            'text': u'Пароль от Вашего аккаунта на Яндексе изменён. Подробности в Почте.',
            'identity': 'change_password_notification.notify',
        })

    def check_emails_sent(self):
        def build_email(address, is_native):
            return {
                'language': 'ru',
                'addresses': [address],
                'subject': 'password_changed.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': u'\\u0414'},
                    'password_changed.notice': {
                        'MASKED_LOGIN': TEST_LOGIN if is_native else TEST_LOGIN[:3] + '***',
                    },
                    'password_changed.feedback': {
                        'FEEDBACK_PASSWORD_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/passport/security/\'>',
                        'FEEDBACK_PASSWORD_URL_END': '</a>',
                    },
                    'signature.secure': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                        'FEEDBACK_URL_END': '</a>',
                    },
                },
            }

        self.assert_emails_sent([
            build_email(address='%s@%s' % (TEST_LOGIN, 'gmail.com'), is_native=False),
        ])

    def check_log_entries(self, password_hash=None, uid=TEST_UID, login=TEST_LOGIN,
                          old_session_uids=None, global_logout=True, retpath=None,
                          web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False,
                          uids_count=None, clear_is_creating_required=False, optional_logout_possible=True,
                          expected_auth_log_records=None, origin=None,
                          clear_pwn_forced_changing_suspended_at=False,
                          dbshard='passportdbshard1', with_check_cookies=False):

        if password_hash is None:
            password_hash = self.env.db.get(
                'attributes',
                'password.encrypted',
                uid=uid,
                db=dbshard,
            )

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

        # Одна запись в historydb о смене пароля
        expected_log_entries.extend([
            self.historydb_entry(uid, 'info.password', password_hash),
            self.historydb_entry(uid, 'info.password_quality', '100'),
            self.historydb_entry(uid, 'info.password_update_time', TimeNow()),
        ])

        if clear_is_creating_required:
            expected_log_entries.append(self.historydb_entry(uid, 'sid.rm', '100|%s' % TEST_LOGIN))
        if clear_pwn_forced_changing_suspended_at:
            expected_log_entries.append(self.historydb_entry(uid, 'info.password_pwn_forced_changing_suspension_time', '-'))

        expected_log_entries.extend([
            self.historydb_entry(uid, 'action', 'change_password'),
            self.historydb_entry(uid, 'consumer', 'dev'),
            self.historydb_entry(uid, 'user_agent', 'curl'),
        ])

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            expected_log_entries,
        )

        expected_log_records = expected_auth_log_records or [
            [
                ('uid', str(uid)),
                ('status', 'ses_update'),
                ('type', authtypes.AUTH_TYPE_WEB),
                ('client_name', 'passport'),
                ('useragent', TEST_USER_AGENT),
                ('ip_from', TEST_USER_IP),
            ],
        ]
        eq_(self.env.auth_handle_mock.call_count, len(expected_log_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_log_records,
        )

        extra_kwargs = {}
        if origin:
            extra_kwargs['origin'] = origin
        expected_log_entries = [self.env.statbox.entry('submitted', uid=str(uid), **extra_kwargs)]
        if with_check_cookies:
            expected_log_entries.append(self.env.statbox.entry('check_cookies'))
        expected_log_entries.append(
            self.env.statbox.entry(
                'analyzed_frodo',
                karma_prefix='0',
                is_karma_prefix_returned='0',
                uid=str(uid),
                **extra_kwargs
            ),
        )

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

        expected_log_entries += [
            self.env.statbox.entry('password_encrypted', uid=str(uid)),
        ]
        if self.is_password_hash_from_blackbox:
            expected_log_entries += [
                self.env.statbox.entry('password_encoding', uid=str(uid)),
            ]
        expected_log_entries += [
            self.env.statbox.entry('password_quality', uid=str(uid)),
        ]

        if clear_is_creating_required:
            expected_log_entries.append(self.env.statbox.entry('clear_is_creating_required', uid=str(uid)))
        if clear_pwn_forced_changing_suspended_at:
            expected_log_entries.append(self.env.statbox.entry('clear_pwn_forced_changing_suspended_at', uid=str(uid)))

        auth_entry = self.env.statbox.entry(
            'cookie_set',
            uid=str(uid),
            input_login=login,
            **extra_kwargs
        )
        if old_session_uids:
            auth_entry.update(old_session_uids=old_session_uids)
        if retpath:
            auth_entry.update(retpath=retpath)
        if uids_count:
            auth_entry.update(uids_count=uids_count)
        changed_password_entry = self.env.statbox.entry(
            'changed_password',
            optional_logout_possible=tskv_bool(optional_logout_possible),
            uid=str(uid),
            **extra_kwargs
        )

        expected_log_entries += [
            auth_entry,
            changed_password_entry,
        ]

        self.env.statbox.assert_equals(expected_log_entries)

    def assert_sessionid_called(self, call_index=0):
        self.env.blackbox.requests[call_index].assert_query_contains({
            'method': 'sessionid',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[call_index].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def assert_editsession_called(self, guard_hosts=None, yateam_auth=False):
        if guard_hosts is None:
            guard_hosts = [TEST_HOST]
        expected_kwargs = {
            'uid': str(TEST_UID),
            'format': 'json',
            'sessionid': TEST_SESSIONID,
            'host': 'passport-test.yandex.ru',
            'userip': TEST_USER_IP,
            'method': 'editsession',
            'op': 'add',
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'new_default': str(TEST_UID),
            'keyspace': u'yandex.ru',
            'sslsessionid': TEST_SSL_SESSIONID,
            'create_time': TimeNow(),
            'guard_hosts': ','.join(guard_hosts),
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if yateam_auth:
            expected_kwargs.update(yateam_auth='1')

        editsession_request = self.env.blackbox.get_requests_by_method('editsession')[0]
        editsession_request.assert_query_equals(expected_kwargs)


@istest
class ChangePasswordCommitTestCase(BaseChangePasswordCommitTestCase, OAuthTestMixin):

    def test_wrong_track_state__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = False

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_empty_form__validation_error(self):
        rv = self.make_request(
            query_args=dict(
                current_password='',
                password='',
            ),
        )

        self.assert_error_response(rv, ['current_password.empty', 'password.empty'])

    def test_login_not_found__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                login_status=blackbox.BLACKBOX_LOGIN_NOT_FOUND_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.not_found'],
            **self.get_expected_response()
        )

        self.check_captcha_statuses_on_error()

    def test_disabled_account__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.disabled'],
            **self.get_expected_response()
        )

        self.check_captcha_statuses_on_error()

    def test_disabled_on_deletion_account__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                login_status=blackbox.BLACKBOX_LOGIN_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.disabled_on_deletion'],
            **self.get_expected_response()
        )
        self.check_captcha_statuses_on_error()

    def test_blackbox_unknown_login__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                login_status=blackbox.BLACKBOX_LOGIN_UNKNOWN_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['backend.blackbox_failed'],
            **self.get_expected_response()
        )
        self.check_captcha_statuses_on_error()

    def test_rfc_2fa__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                password_status=blackbox.BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['second_step.not_implemented'],
            **self.get_expected_response()
        )

    def test_good_way__ok(self):
        """Проход по самому короткому пути, проверка изменений в БД"""
        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
        self.check_db()

        self.check_log_entries(old_session_uids=str(TEST_UID), with_check_cookies=True)
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_origin_written_to_statbox__with_retpath__ok(self):
        """Запись origin в статбокс, отдача retpath"""
        self.setup_track(origin=TEST_ORIGIN, retpath=TEST_RETPATH)

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response(retpath=TEST_RETPATH))

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            origin=TEST_ORIGIN,
            retpath=TEST_RETPATH,
            with_check_cookies=True,
        )

    def test_good_way__no_secure_phone__ok(self):
        """
        Проход по самому короткому пути, проверка изменений в БД,
        у пользователя нет телефона
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(phone=None)
            ),
        )

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
        self.check_db()

        self.check_log_entries(old_session_uids=str(TEST_UID), with_check_cookies=True)
        self.check_frodo_call()
        self.check_track_ok()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_revoke_tokens__ok(self):
        """Проход по самому короткому пути, с явным отказом отзывать веб-сессии, но с отзывом токенов и ПП"""
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='1',
                revoke_app_passwords='1',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
        self.check_db(
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
        )

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')

        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))
            ok_(eav_pass_hash != TEST_OLD_SERIALIZED_PASSWORD)

        self.check_log_entries(
            password_hash=eav_pass_hash,
            old_session_uids=str(TEST_UID),
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
            with_check_cookies=True,
        )
        self.check_frodo_call()
        self.check_track_ok()
        self.check_emails_sent()

    def test_revoke_web_sessions__ok(self):
        """Проход по самому короткому пути, с явным отказом отзывать токены и ПП, но с отзывом веб-сессий"""
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='1',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
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
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_strong_password_policy__ok(self):
        """Проход по самому короткому пути, с принудительным выставлением ревокеров
        из-за усиленной парольной политики"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(subscribed_to=[67])
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )

        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_ok_response_with_cookies(
            rv,
            self.get_expected_response(allow_select_revokers=False),
        )
        self.assert_editsession_called()
        self.check_db(sharddb_query_count=3, global_logout=True)

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=True,
            optional_logout_possible=False,
            with_check_cookies=True,
        )
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_clear_creating_required__ok(self):
        """Убеждаемся что признак is_creating_required сбрасывается"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(subscribed_to=[100])
            ),
        )

        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
        self.check_db(global_logout=False)

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=False,
            clear_is_creating_required=True,
            with_check_cookies=True,
        )
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_clear_pwn_forced_changing_suspension__ok(self):
        """Убеждаемся что признак pwn_forced_changing_suspended_at сбрасывается"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(
                    attributes={
                        'password.pwn_forced_changing_suspended_at': str(int(time.time())),
                    },
                )
            ),
        )

        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_editsession_called()
        self.check_db(global_logout=False)

        self.check_log_entries(
            old_session_uids=str(TEST_UID),
            global_logout=False,
            clear_pwn_forced_changing_suspended_at=True,
            with_check_cookies=True,
        )
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        self.assert_sessionid_called()

    def test_with_env_profile_modification__ok(self):
        """Проход по самому короткому пути, проверка обновления профиля"""

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_profile_written_to_auth_challenge_log()

    def test_with_env_profile_modification_for_shared_account__ok(self):
        """Проход по самому короткому пути, не обновляем профиль для аккаунта с атрибутом account.is_shared"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs(
                    attributes={
                        'account.is_shared': True,
                    },
                )
            ),
        )

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_profile_written_to_auth_challenge_log()

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
        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db()

        self.check_log_entries(old_session_uids=str(TEST_UID), with_check_cookies=True)
        self.check_frodo_call()
        self.check_track_ok()

        editsession_request = self.env.blackbox.get_requests_by_method('editsession')[0]
        editsession_request.assert_query_contains(
            {
                'is_yastaff': '1',
                'is_betatester': '1',
            },
        )

    def test_change_password_for_single_user_session(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                authid=TEST_OLD_AUTH_ID,
                **self.account_kwargs()
            ),
        )

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db()

        self.check_frodo_call()
        self.check_track_ok()
        self.assert_sessionid_called()
        self.check_log_entries(old_session_uids=str(TEST_UID), global_logout=True, with_check_cookies=True)

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

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db()
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_sessionid_called()
        self.check_log_entries(
            old_session_uids='%d,12345' % TEST_UID,
            global_logout=True,
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

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db()
        self.check_frodo_call()
        self.check_track_ok()
        self.assert_sessionid_called()
        self.check_log_entries(
            old_session_uids='%d,12345' % TEST_UID,
            uids_count='2',
            global_logout=True,
            with_check_cookies=True,
        )

    def test_repeated_call__error(self):
        """После успешной обработки, повторный вызов ручки возвращает ошибку состояния"""
        rv = self.make_request()

        # Первый вызов успешен
        self.assert_ok_response_with_cookies(rv, self.get_expected_response())

        # Повторный вызов должен вернуть ошибку
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_too_weak_new_password__validation_error(self):
        rv = self.make_request(
            query_args=dict(
                password=TEST_WEAK_PASSWORD,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.weak'],
            **self.get_expected_response()
        )

    def test_change_password_equals_phone_for_user_with_secure_number_in_track_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(phone=None)
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.secure_phone_number = TEST_PHONE_NUMBER.e164
            track.can_use_secure_number_for_password_validation = True

        rv = self.make_request(
            query_args=dict(
                password=TEST_PHONE_NUMBER.e164,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.likephonenumber'],
            **self.get_expected_response()
        )

    def test_change_password_equals_phone_for_user_with_confirmed_secure_number_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(phone=None)
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        rv = self.make_request(
            query_args=dict(
                password=TEST_PHONE_NUMBER.e164,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.likephonenumber'],
            **self.get_expected_response()
        )

    def test_change_password_equals_phone_for_user_with_confirmed_and_another_secure_number_in_track_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(phone=None)
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.secure_phone_number = TEST_DIFFERENT_PHONE_NUMBER.e164
            track.can_use_secure_number_for_password_validation = False

        rv = self.make_request(
            query_args=dict(
                password=TEST_PHONE_NUMBER.e164,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.likephonenumber'],
            **self.get_expected_response()
        )

    def test_change_password_equals_phone_in_db_error(self):
        rv = self.make_request(
            query_args=dict(
                password=TEST_PHONE_NUMBER.e164,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.likephonenumber'],
            **self.get_expected_response()
        )

    def test_strong_policy_and_not_strong_new_password__validation_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(subscribed_to=[67])
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )

        rv = self.make_request(
            query_args=dict(
                password=TEST_NOT_STRONG_PASSWORD,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.weak'],
            **self.get_expected_response(allow_select_revokers=False)
        )
        track = self.track_manager.read(self.track_id)
        assert_is_none(track.is_strong_password_policy_required)

    def test_new_password_like_current__validation_error(self):
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: True}),
        )

        rv = self.make_request(
            query_args=dict(
                password=TEST_PASSWORD,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.equals_previous'],
            **self.get_expected_response()
        )
        track = self.track_manager.read(self.track_id)
        assert_is_none(track.password_hash)

    def test_new_password_like_current_with_bad_current_password__error(self):
        """
        Проверяет что при неправильно введёном старом пароле мы не выдаём информацию
        о том, что новый пароль совпадает с текущим паролем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            )),
        )

        rv = self.make_request(
            query_args=dict(
                current_password='blblbla',
                password=TEST_PASSWORD,
            ),
        )

        self.assert_error_response(
            rv,
            ['captcha.required', 'password.not_matched'],
            **self.get_expected_response()
        )

        self.check_captcha_statuses_on_error()

        track = self.track_manager.read(self.track_id)
        assert_is_none(track.password_hash)

    def test_new_password_found_in_history_for_strong_password__validation_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(subscribed_to=[67])
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['password.found_in_history'],
            **self.get_expected_response(allow_select_revokers=False)
        )

    def test_new_password_found_in_history_for_strong_password_with_bad_current_password__validation_error(self):
        """
        Проверяет что при неправильно введёном старом пароле мы не выдаём информацию
        об истории паролей.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            )),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.account_kwargs(subscribed_to=[67])),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['captcha.required', 'password.not_matched'],
            **self.get_expected_response(allow_select_revokers=False)
        )

        self.check_captcha_statuses_on_error()

    def test_bad_current_password__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['captcha.required', 'password.not_matched'],
            **self.get_expected_response()
        )

        self.check_captcha_statuses_on_error()

    def test_blackbox_unknown_password__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs(
                password_status=blackbox.BLACKBOX_PASSWORD_UNKNOWN_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['backend.blackbox_failed'],
            **self.get_expected_response()
        )

        self.check_captcha_statuses_on_error()

    def test_frodo_forbidden_change_password(self):
        self.env.frodo.set_response_value(
            u'check',
            FRODO_RESPONSE_FORBIDDEN_CHANGE_PASSWORD,
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.check_db(sharddb_query_count=3)
        self.assert_sessionid_called()

        self.env.db.check('attributes', 'karma.value', '7000', uid=TEST_UID, db='passportdbshard1')

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.expected_frodo_params())

        self.check_track_ok()

        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry('analyzed_frodo'),
            entry_index=3,
        )
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry('check_cookies'),
            entry_index=1,
        )
        self.check_emails_sent()
        self.check_sms_sent()

    def test_account_karma_passed_to_frodo(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                karma=85,
                **self.account_kwargs(phone=None)
            ),
        )
        resp = self.make_request()
        self.assert_ok_response_with_cookies(resp, self.get_expected_response())
        self.check_frodo_call(karma=85)

    def test_commit__blackbox_unexpected_response__error(self):
        """
        ЧЯ вернул что-то странное при запросе в метод login,
        то, чего возвращать он никак не должен. Проверим, что корректно
        отработаем данную ситуацию.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            json.dumps(
                {
                    'error': 'ok',
                    'login_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                    'password_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                },
            ),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['backend.blackbox_permanent_error'],
            **self.get_expected_response()
        )

    def test_pdd_change_password__good_way__ok(self):
        """ПДД-пользователь приходит и меняет свой пароль"""
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

        rv = self.make_request()

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
        self.check_db(
            uid=TEST_PDD_UID,
            dbshard='passportdbshard2',
        )
        self.check_log_entries(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            old_session_uids=str(TEST_PDD_UID),
            dbshard='passportdbshard2',
            with_check_cookies=True,
        )
        self.check_frodo_call(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
        )
        self.check_track_ok()
        self.assert_sessionid_called()

    def test_pdd_change_password__password_like_yandex_login__ok(self):
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

        rv = self.make_request(
            query_args=dict(password='%s@yandex.ru' % TEST_PDD_LOGIN_PART),
        )

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

    def test_pdd_password_like_login__validation_error(self):
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

        rv = self.make_request(
            query_args=dict(
                password=TEST_PDD_LOGIN,
            ),
        )

        self.assert_error_response(
            rv,
            ['password.likelogin'],
            **self.get_expected_response(
                display_login=TEST_PDD_LOGIN,
                is_pdd=True,
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
            )
        )

    def test_service_guard_container__ok(self):
        """ Отдача service_guard_container """
        self.setup_track(retpath=TEST_RETPATH)
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_USER_IP,
                time=TEST_COOKIE_TIMESTAMP,
                sessguard_hosts=[TEST_HOST, TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sign',
            blackbox_sign_response(),
        )

        rv = self.make_request()

        resp = self.get_expected_response(retpath=TEST_RETPATH)
        resp.update(dict(service_guard_container='123.abc'))
        self.assert_ok_response_with_cookies(rv, resp, with_sessguard=True)
        self.assert_editsession_called(guard_hosts=[TEST_HOST, TEST_RETPATH_HOST])


@with_settings_hosts(
    IS_INTRANET=True,
)
@istest
class ChangePasswordCommitIntranetTestCase(BaseChangePasswordCommitTestCase):
    def setUp(self):
        super(ChangePasswordCommitIntranetTestCase, self).setUp()

        self.ldap_bind_mock = mock.Mock(return_value=None)
        self.ldap_search_mock = mock.Mock(return_value=[
            (
                'CN=Firstname Lastname,CN=Users,DC=tst,DC=virtual',
                {'cn': ['Firstname Lastname']},
            ),
        ])
        self.ldap_modify_mock = mock.Mock(return_value=None)
        self.ldap_mock = mock.Mock()
        self.ldap_mock.simple_bind_s = self.ldap_bind_mock
        self.ldap_mock.search_s = self.ldap_search_mock
        self.ldap_mock.modify_s = self.ldap_modify_mock
        self.ldap_patch = mock.patch('ldap.initialize', mock.Mock(return_value=self.ldap_mock))
        self.ldap_patch.start()

    def tearDown(self):
        self.ldap_patch.stop()
        super(ChangePasswordCommitIntranetTestCase, self).tearDown()

    def get_expected_response(self, *args, **kwargs):
        return super(ChangePasswordCommitIntranetTestCase, self).get_expected_response(
            *args,
            revoke_all=False,
            allow_select_revokers=True,
            **kwargs
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_sessionid_called()
        self.assert_editsession_called(yateam_auth=True)

        self.check_db(
            sharddb_query_count=0,
            check_password=False,
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=False,
            app_passwords_revoked=False,
        )
        self.check_track_ok()
        self.assert_frodo_not_called()
        self.assert_yasms_not_called()
        self.check_emails_sent()

        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='changed_password',
            uid=TEST_UID,
            title='Пароль в аккаунте {} успешно изменён'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )
        assert self.ldap_mock.simple_bind_s.call_args.args == (
            '%s@%s' % (TEST_LOGIN, settings.LDAP_USER_DOMAIN), TEST_PASSWORD,
        )

    def test_ok_with_revokers(self):
        rv = self.make_request(
            query_args=dict(
                revoke_web_sessions='0',
                revoke_tokens='1',
                revoke_app_passwords='1',
            ),
        )

        self.assert_ok_response_with_cookies(rv, self.get_expected_response())
        self.assert_sessionid_called()
        self.assert_editsession_called(yateam_auth=True)

        self.check_db(
            sharddb_query_count=1,
            check_password=False,
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
        )
        self.check_track_ok()
        self.assert_frodo_not_called()
        self.assert_yasms_not_called()
        self.check_emails_sent()
        ok_(self.ldap_modify_mock.called)

    def test_current_password_not_matched_error(self):
        self.ldap_bind_mock.side_effect = ldap.INVALID_CREDENTIALS
        rv = self.make_request()

        self.assert_error_response(rv, ['password.not_matched'], **self.get_expected_response())
        ok_(not self.ldap_modify_mock.called)

    def test_new_password_invalid_error(self):
        self.ldap_modify_mock.side_effect = ldap.CONSTRAINT_VIOLATION
        rv = self.make_request()

        self.assert_error_response(rv, ['password.change_forbidden'], **self.get_expected_response())
        ok_(self.ldap_modify_mock.called)

    def test_ldap_unavailable_error(self):
        self.ldap_bind_mock.side_effect = ldap.LDAPError
        rv = self.make_request()

        self.assert_error_response(rv, ['backend.ldap_failed'], **self.get_expected_response())
        ok_(not self.ldap_modify_mock.called)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class ChangePasswordCommitTestCaseNoBlackboxHash(ChangePasswordCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
