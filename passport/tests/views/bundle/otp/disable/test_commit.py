# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
    OAuthTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_contains_params
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts

from .test_base import (
    get_headers,
    TEST_GLOBAL_LOGOUT_DATETIME,
    TEST_IP,
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PASSWORD,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_UID,
)


class OtpDisableCommitTestCaseBase(
    BaseBundleTestViews,
    EmailTestMixin,
    OAuthTestMixin,
    AccountModificationNotifyTestMixin,
):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.default_headers = get_headers()
        self.default_params = self.query_params()

        self.setup_db()
        self.setup_blackbox()
        self.setup_shakur()
        self.setup_track()
        self.setup_statbox_templates()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def setup_track(self, uid=TEST_UID, is_it_otp_disable=True, is_otp_checked=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_disable = is_it_otp_disable
            track.is_otp_checked = is_otp_checked

    def get_account_args(self, uid, login):
        self.native_email = self.create_native_email(TEST_LOGIN, 'yandex.ru')
        return dict(
            uid=uid,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.native_email,
            ],
            login=login,
            attributes={
                'account.2fa_on': '1',
                'account.totp.secret_ids': '1:100',
                'account.totp.failed_pin_checks_count': '2',
            },
        )

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN):
        account_args = self.get_account_args(uid, login)

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_args
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                ip=TEST_IP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

    def setup_shakur(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def assert_blackbox_sessionid_called(self):
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'full_info': 'yes',
                'multisession': 'yes',
                'method': 'sessionid',
                'sessionid': '0:old-session',
            },
            callnum=0,
        )

    def assert_blackbox_editsession_called(self, extra_guard_host=None):
        request = self.env.blackbox.get_requests_by_method('editsession')[0]
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host is not None:
            guard_hosts.append(extra_guard_host)
        request.assert_query_equals(
            {
                'uid': str(TEST_UID),
                'format': 'json',
                'userip': TEST_IP,
                'method': 'editsession',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'keyspace': u'yandex.ru',
                'lang': '1',
                'new_default': '1',
                'host': 'passport.yandex.ru',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
                'op': 'add',
                'create_time': TimeNow(),
                'guard_hosts': ','.join(guard_hosts),
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_blackbox_sign_sessguard_called(self):
        request = self.env.blackbox.get_requests_by_method('sign')[0]
        sessguard_cookie = 'sessguard=1.sessguard; Domain=.%s; Secure; HttpOnly; Path=/' % TEST_RETPATH_HOST
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'sign',
                'sign_space': 'sessguard_container',
                'ttl': '60',
                'value': json.dumps({
                    'cookies': [sessguard_cookie],
                    'retpath': TEST_RETPATH,
                }),
            },
        )

    def check_emails_sent(self):
        def build_email(address, is_native):
            return {
                'language': 'ru',
                'addresses': [address],
                'subject': '2fa_disabled.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': u'\\u0414'},
                    '2fa_disabled.auth': {
                        'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                        'ACCESS_CONTROL_URL_END': '</a>',
                    },
                    '2fa_disabled.enable': {
                        'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                        'ACCESS_CONTROL_URL_END': '</a>',
                    },
                    '2fa_disabled.feedback': {
                        'FEEDBACK_2FA_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/passport/problems/\'>',
                        'FEEDBACK_2FA_URL_END': '</a>',
                        'HELP_2FA_URL_BEGIN': '<a href=\'https://yandex.ru/support/passport/authorization/twofa.html\'>',
                        'HELP_2FA_URL_END': '</a>',
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
            build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru'), is_native=True),
            self.create_account_modification_mail(
                'login_method_change',
                '%s@%s' % (TEST_LOGIN, 'gmail.com'),
                dict(
                    login=TEST_LOGIN,
                    USER_IP=TEST_IP,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                'login_method_change',
                '%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                dict(
                    login=TEST_LOGIN,
                    USER_IP=TEST_IP,
                ),
            ),
        ])

    def setup_db(self):
        account_args = self.get_account_args(TEST_UID, TEST_LOGIN)
        self.env.db.serialize(blackbox_userinfo_response(**account_args))

        self.env.db.insert(
            'attributes',
            db='passportdbshard1',
            uid=TEST_UID,
            type=AT['account.totp.check_time'],
            value='123',
        )

    def query_params(self, **kwargs):
        params = {
            'password': TEST_PASSWORD,
            'track_id': self.track_id,
        }
        params.update(kwargs)
        return params

    def make_request(self, params=None, headers=None):
        if not headers:
            headers = self.default_headers
        if not params:
            params = self.default_params
        return self.env.client.post(
            '/1/bundle/otp/disable/commit/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        ok_(track.is_it_otp_disable)
        ok_(track.session)
        eq_(track.old_session_ttl, '0')

    def assert_cookies_ok(self, cookies, with_sessguard=False):
        eq_(len(cookies), 7 + with_sessguard)
        sorted_cookies = sorted(cookies)
        if with_sessguard:
            sessguard_cookie = sorted_cookies.pop(3)
            self.assert_cookie_ok(sessguard_cookie, 'sessguard', domain='.passport-test.yandex.ru', expires=None, http_only=True, secure=True)
        l_cookie, sessionid_cookie, mda2_beacon, sessionid2_cookie, yalogin_cookie, yp_cookie, ys_cookie = sorted_cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yalogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

    def get_account_response(self):
        return {
            'person': {
                'firstname': '\\u0414',
                'language': 'ru',
                'gender': 1,
                'birthday': '1963-05-15',
                'lastname': '\\u0424',
                'country': 'ru',
            },
            'login': TEST_LOGIN,
            'display_name': {'default_avatar': '', 'name': ''},
            'uid': int(TEST_UID),
            'display_login': TEST_LOGIN,
        }

    def assert_ok_response(self, resp, no_cookies=False, with_sessguard=False, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'account': self.get_account_response(),
            'accounts': [
                {
                    'login': TEST_LOGIN,
                    'display_name': {u'default_avatar': u'', u'name': u''},
                    'uid': int(TEST_UID),
                    'display_login': 'user1',
                },
            ],
            'default_uid': TEST_UID,
            'retpath': None,
        }
        body = json.loads(resp.data)
        cookies = body.pop('cookies', [])
        eq_(resp.status_code, 200)
        eq_(
            body,
            merge_dicts(base_response, kwargs),
        )
        if not no_cookies:
            self.assert_cookies_ok(cookies, with_sessguard=with_sessguard)

    def get_password_hash(self):
        dbshardname = 'passportdbshard1'
        return self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db=dbshardname)

    def check_db(self, centraldb_query_count=0, sharddb_query_count=2, global_logout=True,
                 web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False):
        timenow = TimeNow()
        dbshardname = 'passportdbshard1'

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(dbshardname), sharddb_query_count)

        if global_logout:
            self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=TEST_UID, db=dbshardname)
        else:
            self.env.db.check_missing('attributes', 'account.global_logout_datetime', uid=TEST_UID, db=dbshardname)

        if web_sessions_revoked:
            self.env.db.check('attributes', 'revoker.web_sessions', timenow, uid=TEST_UID, db=dbshardname)
        else:
            self.env.db.check_missing('attributes', 'revoker.web_sessions', uid=TEST_UID, db=dbshardname)

        if tokens_revoked:
            self.env.db.check('attributes', 'revoker.tokens', timenow, uid=TEST_UID, db=dbshardname)
        else:
            self.env.db.check_missing('attributes', 'revoker.tokens', uid=TEST_UID, db=dbshardname)

        if app_passwords_revoked:
            self.env.db.check('attributes', 'revoker.app_passwords', timenow, uid=TEST_UID, db=dbshardname)
        else:
            self.env.db.check_missing('attributes', 'revoker.app_passwords', uid=TEST_UID, db=dbshardname)

        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db=dbshardname)
        self.env.db.check_missing('attributes', 'account.totp.failed_pin_checks_count', uid=TEST_UID, db=dbshardname)
        self.env.db.check_missing('attributes', 'account.totp.secret', uid=TEST_UID, db=dbshardname)
        self.env.db.check_missing('attributes', 'account.totp.check_time', uid=TEST_UID, db=dbshardname)

        pass_hash = self.get_password_hash()
        if self.is_password_hash_from_blackbox:
            eq_(pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(pass_hash), 36)
            ok_(pass_hash.startswith('1:'))

    def build_auth_log_entry(self, status, uid, comment=None):
        entry = [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', 'curl'),
            ('ip_from', TEST_IP),
        ]
        if comment:
            entry.append(('comment', comment))
        return entry

    def assert_auth_and_event_log_ok(self, auth_log_entries, global_logout=True,
                                     web_sessions_revoked=False, tokens_revoked=False,
                                     app_passwords_revoked=False):
        event_log_entries = {
            'info.password': self.get_password_hash(),
            'info.password_quality': '100',
            'info.password_update_time': TimeNow(),
            'info.totp': 'disabled',
            'info.totp_secret.1': '-',
            'info.totp_update_time': '-',
            'action': 'disable_otp',
            'user_agent': 'curl',
            'consumer': 'dev',
        }
        if global_logout:
            event_log_entries['info.glogout'] = TimeNow()
        if web_sessions_revoked:
            event_log_entries['info.web_sessions_revoked'] = TimeNow()
        if tokens_revoked:
            event_log_entries['info.tokens_revoked'] = TimeNow()
        if app_passwords_revoked:
            event_log_entries['info.app_passwords_revoked'] = TimeNow()
        self.assert_events_are_logged(
            self.env.handle_mock,
            event_log_entries,
        )
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            auth_log_entries,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            user_agent='curl',
            uid=str(TEST_UID),
            ip=TEST_IP,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _exclude=['consumer'],
            input_login=TEST_LOGIN,
            track_id=self.track_id,
            ttl='0',
            session_method='edit',
            person_country='ru',
            yandexuid='testyandexuid',
            old_session_uids=str(TEST_UID),
            retpath=TEST_RETPATH,
            ip_country='ru',
        )
        for entity in (
            'account.global_logout_datetime',
            'account.revoker.web_sessions',
            'account.revoker.tokens',
            'account.revoker.app_passwords',
        ):
            self.env.statbox.bind_entry(
                entity,
                entity=entity,
                new=DatetimeNow(convert_to_datetime=True),
                old=TEST_GLOBAL_LOGOUT_DATETIME,
                operation='updated',
                event='account_modification',
            )
        self.env.statbox.bind_entry(
            'password_encrypted',
            entity='password.encrypted',
            operation='created',
            event='account_modification',
        )
        self.env.statbox.bind_entry(
            'password_encoding_version',
            entity='password.encoding_version',
            operation='created',
            event='account_modification',
            old='-',
            new=str(self.password_hash_version),
        )
        self.env.statbox.bind_entry(
            'password_quality',
            entity='password.quality',
            operation='created',
            new='100',
            old='-',
            event='account_modification',
        )
        self.env.statbox.bind_entry(
            'disabled',
            action='disabled',
            track_id=self.track_id,
            mode='disable_otp',
            yandexuid='testyandexuid',
        )

    def assert_statbox_ok(self, global_logout=True, tokens_revoked=False,
                          web_sessions_revoked=False, app_passwords_revoked=False, with_check_cookies=False, **kwargs):
        statbox_entries = []
        if with_check_cookies:
            statbox_entries.append(self.env.statbox.entry('check_cookies', host='passport.yandex.ru'))
        if global_logout:
            statbox_entries.append(
                self.env.statbox.entry('account.global_logout_datetime'),
            )
        if tokens_revoked:
            statbox_entries.append(
                self.env.statbox.entry('account.revoker.tokens'),
            )
        if web_sessions_revoked:
            statbox_entries.append(
                self.env.statbox.entry('account.revoker.web_sessions'),
            )
        if app_passwords_revoked:
            statbox_entries.append(
                self.env.statbox.entry('account.revoker.app_passwords'),
            )
        statbox_entries.extend([
            self.env.statbox.entry('password_encrypted'),
            self.env.statbox.entry('password_encoding_version'),
            self.env.statbox.entry('password_quality'),
            self.env.statbox.entry(
                'cookie_set',
                **kwargs.get('cookie_set', {})
            ),
            self.env.statbox.entry('disabled'),
        ])
        self.env.statbox.assert_has_written(statbox_entries)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    PASSPORT_SUBDOMAIN='passport-test',
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'login_method_change'},
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'login_method_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
        },
    )
)
class OtpDisableCommitTestCase(OtpDisableCommitTestCaseBase):

    def test_empty_track_error(self):
        resp = self.make_request(params=self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

    def test_empty_password_error(self):
        resp = self.make_request(params=self.query_params(password=''))
        self.assert_error_response(resp, ['password.empty'])

    def test_weak_password_error(self):
        resp = self.make_request(params=self.query_params(password='123456'))
        self.assert_error_response_with_track_id(resp, ['password.weak'])

    def test_password_like_email_error(self):
        """
        Проверим, что пароль не может совпадать с емейлом пользователя,
        т.е. мы корректно вызываем валидатор
        """
        resp = self.make_request(params=self.query_params(password='%s@yandex.ru' % TEST_LOGIN))
        self.assert_error_response_with_track_id(resp, ['password.likelogin'])

    def test_empty_cookies_error(self):
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_bad_cookies_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled_on_deletion'])

    def test_action_not_required_error(self):
        """
        Пришли в ручку, а секрет уже удален
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['action.not_required'])
        self.check_account_modification_push_not_sent()

    def test_action_not_required_by_track_error(self):
        """
        Пришли в ручку, а секрет уже удален именно на этом треке
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '0:sessionid'
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['action.not_required'])

    def test_account_uid_not_match_track(self):
        """
        Пришли с кукой, в которой другой аккаунт
        """
        self.setup_blackbox(uid=TEST_OTHER_UID, login='lala1')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_track_not_for_otp_disable_error(self):
        self.setup_track(is_it_otp_disable=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_no_uid_in_track_error(self):
        self.setup_track(uid='')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_otp_was_not_check_error(self):
        """
        Пришли на финальный шаг, а отп не был проверен
        """
        self.setup_track(is_otp_checked=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(with_check_cookies=True)
        self.check_emails_sent()
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='login_method_change',
            uid=TEST_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_ok_otp_magic_logged(self):
        """Если пользователь проверял otp с помощью магии, это будет записано"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.otp = 'somepass'

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID, comment='aid=123:1422501443:126;mgc=1;ttl=0'),
            ],
        )
        self.assert_statbox_ok(with_check_cookies=True)

    def test_ok_revoke_tokens(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        resp = self.make_request(
            params=self.query_params(
                revoke_web_sessions='0',
                revoke_tokens='1',
                revoke_app_passwords='1',
            ),
        )

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_db(
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
        )
        self.assert_track_ok()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            auth_log_entries=[
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
            global_logout=False,
            web_sessions_revoked=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
        )
        self.assert_statbox_ok(
            global_logout=False,
            tokens_revoked=True,
            app_passwords_revoked=True,
            with_check_cookies=True,
        )
        self.check_emails_sent()

    def test_ok_revoke_web_sessions(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        resp = self.make_request(
            params=self.query_params(
                revoke_web_sessions='1',
                revoke_tokens='0',
                revoke_app_passwords='0',
            ),
        )

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_db(
            global_logout=False,
            web_sessions_revoked=True,
            tokens_revoked=False,
            app_passwords_revoked=False,
        )
        self.assert_track_ok()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            auth_log_entries=[
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
            global_logout=False,
            web_sessions_revoked=True,
            tokens_revoked=False,
            app_passwords_revoked=False,
        )
        self.assert_statbox_ok(
            global_logout=False,
            web_sessions_revoked=True,
            with_check_cookies=True,
        )
        self.check_emails_sent()

    def test_67_sid_track_flag_ok(self):
        account_args = self.get_account_args(TEST_UID, TEST_LOGIN)

        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                subscribed_to=[67],
                **account_args
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = False

        resp = self.make_request()

        self.assert_ok_response(resp)
        self.assert_track_ok()
        track = self.track_manager.read(self.track_id)
        eq_(track.is_strong_password_policy_required, True)

    def test_other_account_in_session_error(self):
        """
        Пришли в ручку с мультикукой, в которой нет аккаунта, начавшего процесс.
        """
        self.setup_blackbox(uid=TEST_OTHER_UID)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_account_in_session_not_default_and_invalid_error(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт, начавший процесс недефолтный и невалидный.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                ),
                item_id=TEST_UID,
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_account_in_session_not_default_and_valid_ok(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт,
        начавший процесс недефолтный, но валидный. Все ок, продолжаем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                ),
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.2fa_on': '1',
                    'account.totp.secret_ids': '1:100',
                },
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called()
        self.assert_track_ok()
        self.check_db()
        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'login': TEST_LOGIN,
                    'display_name': {'default_avatar': '', 'name': ''},
                    'uid': int(TEST_UID),
                    'display_login': TEST_LOGIN,
                },
                {
                    'login': 'other_login',
                    'display_name': {'default_avatar': '', 'name': ''},
                    'uid': int(TEST_OTHER_UID),
                    'display_login': TEST_OTHER_LOGIN,
                },
            ],
        )
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
                self.build_auth_log_entry('ses_update', TEST_OTHER_UID),
            ],
        )
        self.assert_statbox_ok(
            cookie_set=dict(
                _exclude=['retpath'],
                uids_count='2',
                old_session_uids='%s,%s' % (TEST_UID, TEST_OTHER_UID),
            ),
            with_check_cookies=True,
        )

    def test_ok_2fa_disabled_passed_to_build_yp_cookie(self):
        """
        Удостоверимся, что в функцию создания куки yp передали знание о том,
        что 2фа выключено.
        """

        build_cookie_yp = mock.Mock(return_value='yp')
        with mock.patch(
                'passport.backend.api.common.authorization.build_cookie_yp',
                build_cookie_yp,
        ):
            self.make_request()
        eq_(build_cookie_yp.call_args_list[0][0][5], False)

    def test_extra_sessguard_container(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                ip=TEST_IP,
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sign',
            blackbox_sign_response(),
        )

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(
            resp,
            with_sessguard=True,
            retpath=TEST_RETPATH,
            service_guard_container='123.abc',
        )
        self.assert_blackbox_sign_sessguard_called()
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(with_check_cookies=True)
        self.check_emails_sent()


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    PASSPORT_SUBDOMAIN='passport-test',
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
        },
    )
)
class OtpDisableCommitTestCaseNoBlackboxHash(OtpDisableCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
