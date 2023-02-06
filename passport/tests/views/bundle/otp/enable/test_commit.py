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
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_params_equal
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import get_unixtime

from .test_base import (
    get_headers,
    TEST_GLOBAL_LOGOUT_DATETIME,
    TEST_IP,
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PHONE_NUMBER,
    TEST_PIN,
    TEST_PIN_LENGTH,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_TOTP_CHECK_TIME,
    TEST_UID,
    TOTP_SECRET_ENCRYPTED,
)


DB_SHARD_NAME = 'passportdbshard1'


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_CONSUMER='passport',
    OAUTH_RETRIES=1,
    PASSWORD_VERIFICATION_MAX_AGE=600,
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
class OtpEnableCommitTestCase(
    BaseBundleTestViews,
    OAuthTestMixin,
    EmailTestMixin,
    AccountModificationNotifyTestMixin,
):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.default_headers = get_headers()
        self.default_params = self.query_params()

        self.setup_blackbox()
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

    def setup_account(self, account_kwargs=None):
        if account_kwargs is None:
            account_kwargs = self.get_account_kwargs(TEST_UID, TEST_LOGIN)
        self.env.db.serialize(blackbox_userinfo_response(**account_kwargs))

    def assert_blackbox_editsession_called(self, callnum=1, extra_guard_host=None):
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host is not None:
            guard_hosts.append(extra_guard_host)
        assert_builder_url_params_equal(
            self.env.blackbox,
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
            callnum=callnum,
        )

    def setup_track(self, uid=TEST_UID, is_it_otp_enable=True,
                    totp_secret_encrypted=TOTP_SECRET_ENCRYPTED,
                    password_verification_passed_at=None, is_otp_checked=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
            track.totp_pin = TEST_PIN
            track.totp_secret_encrypted = totp_secret_encrypted
            track.totp_secret_ids = {1: 100}
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            if password_verification_passed_at:
                track.password_verification_passed_at = password_verification_passed_at
            track.is_otp_checked = is_otp_checked
            track.blackbox_totp_check_time = TEST_TOTP_CHECK_TIME

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN, **kwargs):
        account_kwargs = self.get_account_kwargs(uid, login, **kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )
        sessionid_params = dict(
            crypt_password='1:crypt',
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        sessionid_params = deep_merge(sessionid_params, account_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **sessionid_params
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                ip=TEST_IP,
            ),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def query_params(self, **kwargs):
        params = {
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
            '/1/bundle/otp/enable/commit/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        ok_(track.session)
        eq_(track.old_session_ttl, '0')
        ok_(track.is_otp_checked)

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

    def check_emails_sent(self):
        def build_email(address, is_native):
            return {
                'language': 'ru',
                'addresses': [address],
                'subject': '2fa_enabled.subject',
                'tanker_keys': {
                    'greeting': {'FIRST_NAME': u'\\u0414'},
                    '2fa_enabled.app_password.section': {
                        'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                        'ACCESS_CONTROL_URL_END': '</a>',
                    },
                    '2fa_enabled.help': {
                        'HELP_2FA_URL_BEGIN':
                            '<a href=\'https://yandex.ru/support/passport/authorization/twofa.html\'>',
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
            'retpath': None,
            'accounts': [
                {
                    'login': TEST_LOGIN,
                    'display_name': {'default_avatar': '', 'name': ''},
                    'uid': int(TEST_UID),
                    'display_login': TEST_LOGIN,
                },
            ],
            'default_uid': TEST_UID,
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

    def check_db(self, centraldb_query_count=0, sharddb_query_count=2):
        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(DB_SHARD_NAME), sharddb_query_count)

        self.env.db.check(
            'attributes',
            'account.totp.secret',
            TOTP_SECRET_ENCRYPTED,
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check(
            'attributes',
            'account.global_logout_datetime',
            TimeNow(),
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check(
            'attributes',
            'account.totp.check_time',
            str(TEST_TOTP_CHECK_TIME),
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check(
            'attributes',
            'account.enable_app_password',
            '1',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )

        self.env.db.check_missing(
            'attributes',
            'password.encrypted',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check_missing(
            'attributes',
            'password.update_datetime',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check_missing(
            'attributes',
            'password.quality',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check_missing(
            'attributes',
            'account.sms_2fa_on',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        self.env.db.check_missing(
            'attributes',
            'account.forbid_disabling_sms_2fa',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', 'curl'),
            ('ip_from', TEST_IP),
        ]

    def assert_auth_and_event_log_ok(self, auth_log_entries, **kwargs):
        params = {
            'info.password': '-',
            'info.password_quality': '-',
            'info.password_update_time': '-',
            'info.sms_2fa_on': '0',
            'info.forbid_disabling_sms_2fa': '0',
            'info.totp': 'enabled',
            'info.totp_secret.1': '*',
            'info.totp_update_time': TimeNow(),
            'info.glogout': TimeNow(),
            'info.enable_app_password': '1',
            'action': 'enable_otp',
            'user_agent': 'curl',
            'consumer': 'dev',
        }

        params.update(kwargs)

        self.assert_events_are_logged(
            self.env.handle_mock,
            params,
        )
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            auth_log_entries,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            user_agent='curl',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_IP,
        )
        self.env.statbox.bind_entry(
            'save_app_password',
            entity='account.enable_app_password',
            event='account_modification',
            operation='created',
            old='-',
            new='1',
        )
        self.env.statbox.bind_entry(
            'global_logout',
            entity='account.global_logout_datetime',
            event='account_modification',
            operation='updated',
            new=DatetimeNow(convert_to_datetime=True),
            old=TEST_GLOBAL_LOGOUT_DATETIME,
        )
        self.env.statbox.bind_entry(
            'sms_2fa',
            entity='account.sms_2fa_on',
            event='account_modification',
            operation='created',
            new='0',
            old='-',
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
            is_2fa_enabled='1',
            retpath=TEST_RETPATH,
            old_session_uids=str(TEST_UID),
            ip=TEST_IP,
            ip_country='ru',
        )
        self.env.statbox.bind_entry(
            'enabled',
            track_id=self.track_id,
            mode='enable_otp',
            action='enabled',
            consumer='dev',
            yandexuid='testyandexuid',
            pin_length=str(TEST_PIN_LENGTH),
        )

    def assert_statbox_ok(self, with_check_cookies=False, **kwargs):
        statbox_entries = []
        if with_check_cookies:
            statbox_entries.append(self.env.statbox.entry('check_cookies', host='passport.yandex.ru'))
        statbox_entries.extend([
            self.env.statbox.entry('save_app_password'),
            self.env.statbox.entry('global_logout'),
            self.env.statbox.entry(
                'sms_2fa',
                **kwargs.get('sms_2fa', {})
            ),
            self.env.statbox.entry(
                'cookie_set',
                **kwargs.get('cookie_set', {})
            ),
            self.env.statbox.entry(
                'enabled',
                **kwargs.get('enabled', {})
            ),
        ])
        self.env.statbox.assert_has_written(statbox_entries)

    def get_account_kwargs(self, uid, login, with_secure_phone=True, **kwargs):
        account_kwargs = dict(
            uid=uid,
            login=login,
            crypt_password='1:crypt',
            **kwargs
        )
        phone_builder = build_phone_secured if with_secure_phone else build_phone_bound
        phone = phone_builder(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        return deep_merge(account_kwargs, phone)

    def assert_blackbox_sessionid_called(self):
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

        self.env.blackbox.requests[0].assert_query_contains({
            'full_info': 'yes',
            'multisession': 'yes',
            'method': 'sessionid',
            'sessionid': '0:old-session',
            'sslsessionid': '0:old-sslsession',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

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

    def test_empty_track_error(self):
        self.setup_account()
        resp = self.make_request(params=self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

    def test_empty_cookies_error(self):
        self.setup_account()
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)

    def test_bad_cookies_error(self):
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)

    def test_opt_already_enabled_on_track_error(self):
        """
        Проверим ситуацию, когда на переданном треке уже завершили процесс
        """
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '1:session'
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], track_id=self.track_id)

    def test_account_disabled_error(self):
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'], track_id=self.track_id)

    def test_account_disabled_on_deletion_error(self):
        self.setup_account()
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
        self.assert_error_response(resp, ['account.disabled_on_deletion'], track_id=self.track_id)

    def test_action_not_required_error(self):
        """
        Пришли в ручку, а секрет уже установлен на аккаунте
        """
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], track_id=self.track_id)
        self.check_account_modification_push_not_sent()

    def test_sms_2fa_enabled_ok(self):
        """
        На аккаунте включена sms-2fa
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        account_kwargs = self.get_account_kwargs(
            TEST_UID,
            TEST_LOGIN,
            with_secure_phone=True,
            attributes={
                'account.sms_2fa_on': '1',
                'account.forbid_disabling_sms_2fa': '1',
            },
        )
        self.setup_account(account_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(
            sms_2fa={
                'old': '1',
                'new': '0',
                'operation': 'updated',
            },
            with_check_cookies=True,
        )
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='login_method_change',
            uid=TEST_UID,
            title='Изменён способ входа в аккаунт {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_account_uid_not_match_track(self):
        """
        Пришли с кукой, в которой другой аккаунт дефолтный
        """
        self.setup_account()
        self.setup_blackbox(uid=TEST_OTHER_UID, login='lala1')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_track_not_for_otp_enable_error(self):
        self.setup_account()
        self.setup_track(is_it_otp_enable=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_without_otp_check_error(self):
        """
        Не проверили отп ранее
        """
        self.setup_account()
        self.setup_track(is_otp_checked=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_no_uid_in_track_error(self):
        self.setup_account()
        self.setup_track(uid='')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_no_app_secret_in_track_error(self):
        self.setup_account()
        self.setup_track(totp_secret_encrypted='')
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_no_secure_phone_error(self):
        account_kwargs = self.get_account_kwargs(
            TEST_UID,
            TEST_LOGIN,
            with_secure_phone=False,
        )
        self.setup_account(account_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **account_kwargs
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response(resp, ['phone_secure.not_found'], track_id=self.track_id)

    def test_ok(self):
        self.setup_account()
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

    def test_ok_with_yakey_device_ids(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.totp_push_device_ids.append('test_device_id1')
            track.totp_push_device_ids.append('test_device_id2')

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
            **{'info.totp_yakey_device_ids': 'test_device_id1,test_device_id2'}
        )
        self.assert_statbox_ok(with_check_cookies=True)
        self.check_emails_sent()

    def test_67_sid_ok(self):
        """
        Проверяем, что вдобавок к успешному завершению включения
        2FA для пользователя с усиленной парольной политикой мы
        также записываем удаляемый пароль в историю.
        """
        account_kwargs = self.get_account_kwargs(TEST_UID, TEST_LOGIN)
        account_kwargs = deep_merge(
            account_kwargs,
            dict(
                subscribed_to=[67],
                dbfields={
                    'subscription.login_rule.67': 1,
                },
                attributes={
                    'password.update_datetime': 1,
                },
            ),
        )
        self.setup_account(account_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**account_kwargs),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(extra_guard_host=TEST_RETPATH_HOST)
        # Так как здесь мы пишем в историю паролей, то число запросов +1
        self.check_db(sharddb_query_count=3)
        self.assert_track_ok()
        self.assert_ok_response(resp, retpath=TEST_RETPATH)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(with_check_cookies=True)

        # Проверяем, что признак усиленной парольной политике не сбрасывается
        self.env.db.check(
            'attributes',
            'password.is_strong_policy_enabled',
            '1',
            uid=TEST_UID,
            db=DB_SHARD_NAME,
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_strong_password_policy_required, True)
        self.assert_oauth_not_called()

    def test_ok_password_not_required_by_track(self):
        """
        Пришли к этому шагу с чрезмерно старой кукой,
        но в треке записано, что пароль недавно проверялся - не требуем проверки
        """
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **self.get_account_kwargs(TEST_UID, TEST_LOGIN)
            ),
        )
        self.setup_track(password_verification_passed_at=get_unixtime() - 10)

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called()
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(cookie_set=dict(_exclude=['retpath']), with_check_cookies=True)

    def test_ok_with_user_current_password(self):
        """
        Все хорошо с подтверждением нынешним паролем пользователя
        """
        self.setup_account()
        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(callnum=1)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(cookie_set=dict(_exclude=['retpath']), with_check_cookies=True)

    def test_other_account_in_session_error(self):
        """
        Пришли в ручку с мультикукой, в которой нет аккаунта, начавшего процесс.
        """
        account_kwargs = self.get_account_kwargs(TEST_OTHER_UID, TEST_OTHER_LOGIN)
        self.setup_account(account_kwargs)
        self.setup_blackbox(TEST_OTHER_UID, TEST_OTHER_LOGIN)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_account_in_session_not_default_and_invalid_error(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт, начавший процесс, недефолтный и невалидный.
        """
        self.setup_account()
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
        начавший процесс, недефолтный, но валидный. Все ок, продолжаем.
        """
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                ),
                **self.get_account_kwargs(TEST_UID, TEST_LOGIN)
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
                uids_count='2',
                old_session_uids='%s,%s' % (TEST_UID, TEST_OTHER_UID),
                _exclude=['retpath'],
            ),
            with_check_cookies=True,
        )

    def test_ok_with_old_cookie_but_fresh_password(self):
        """
        Удостоверимся, что проверяем именно время ввода пароля на аккаунте,
        а не время жизни куки
        """
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                    age=100500,  # кука ОЧЕНЬ старая
                ),
                age=0,  # А пароль на аккаунте свежий
                **self.get_account_kwargs(TEST_UID, TEST_LOGIN)
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
                uids_count='2',
                old_session_uids='%s,%s' % (TEST_UID, TEST_OTHER_UID),
                _exclude=['retpath'],
            ),
            with_check_cookies=True,
        )

    def test_required_and_not_recognized_captcha(self):
        """
        Пришёл пользователь с треком, в котором нужна капча и она не пройдена.
        Вернули ошибку captcha.required.
        """
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True

        resp = self.make_request()

        self.assert_error_response_with_track_id(resp, ['captcha.required'])

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)

    def test_required_and_recognized_captcha_and_good_password(self):
        """
        Пришёл пользователь с верным паролем, ЧЯ не требует капчи,
        капча уже была пройдена в данном треке.
        Успешно сохранили в БД данные.
        """
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(),
        )

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(callnum=1)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
        )
        self.assert_statbox_ok(
            cookie_set=dict(
                captcha_passed='1',
                _exclude=['retpath'],
            ),
            with_check_cookies=True,
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, True)
        eq_(track.is_captcha_checked, True)

    def test_ok_2fa_enabled_passed_to_build_yp_cookie(self):
        """
        Удостоверимся, что в функцию создания куки yp передали знание о том,
        что 2фа включено.
        """
        build_cookie_yp = mock.Mock(return_value='yp')
        self.setup_account()

        with mock.patch(
                'passport.backend.api.common.authorization.build_cookie_yp',
                build_cookie_yp,
        ):
            self.make_request()
        eq_(build_cookie_yp.call_args_list[0][0][6], True)

    def test_app_params_in_track__logged_to_statbox_and_historydb(self):
        self.setup_account()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(),
        )
        # Наполним трек данными от приложения Яндекс.Ключ
        # Кроме поля device_name, которое не будет записано в логи. см PASSP-11958
        app_track_fields = (
            'device_application',
            'device_application_version',
            'device_app_uuid',
            'device_os_id',
            'device_manufacturer',
            'device_hardware_model',
            'device_hardware_id',
            'device_ifv',
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

            for field_name in sorted(app_track_fields):
                value_to_save = 'test-%s' % field_name
                setattr(track, field_name, value_to_save)

        resp = self.make_request()

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_editsession_called(callnum=1)
        self.check_db()
        self.assert_track_ok()
        self.assert_ok_response(resp)
        expected = dict(
            map(
                lambda name: (name, 'test-%s' % name),
                app_track_fields,
            ),
        )
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', TEST_UID),
            ],
            app_key_info=json.dumps(expected, sort_keys=True),
        )
        self.assert_statbox_ok(
            cookie_set=dict(
                captcha_passed='1',
                _exclude=['retpath'],
            ),
            enabled=expected,
            with_check_cookies=True,
        )

    def test_extra_sessguard_container(self):
        self.setup_account()
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
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

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

    def test_session_created_long_ago(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.session_created_at = get_unixtime() - 60

        resp = self.make_request()

        self.assert_error_response(resp, ['action.not_required'], track_id=self.track_id)

    def test_ok_session_created_long_ago_with_param(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.session_created_at = get_unixtime() - 60
            track.session_reissue_interval = 300

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

    def test_error_session_created_long_ago_with_param(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.session_reissue_interval = 300
            track.session_created_at = get_unixtime() - 600

        resp = self.make_request()

        self.assert_error_response(resp, ['action.not_required'], track_id=self.track_id)
