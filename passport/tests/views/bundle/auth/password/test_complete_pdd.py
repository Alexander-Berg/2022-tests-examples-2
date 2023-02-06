# -*- coding: utf-8 -*-

import base64
import json
import time

import freezegun
import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
    make_clean_web_test_mixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    FRODO_RESPONSE_BAD_PDD_USER,
    FRODO_RESPONSE_OK,
    FRODO_RESPONSE_SPAM_PDD_USER,
    MDA2_BEACON_VALUE,
    PDD_SESSION_VALUE,
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_COOKIE_TIMESTAMP,
    TEST_DOMAIN,
    TEST_FUID01_COOKIE,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_NOT_STRONG_PASSWORD,
    TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER,
    TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE,
    TEST_NOT_STRONG_PASSWORD_IS_WORD,
    TEST_NOT_STRONG_PASSWORD_LENGTH,
    TEST_NOT_STRONG_PASSWORD_QUALITY,
    TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_WEAK_PASSWORD,
    TEST_WEAK_PASSWORD_CLASSES_NUMBER,
    TEST_WEAK_PASSWORD_HASH,
    TEST_WEAK_PASSWORD_IS_SEQUENCE,
    TEST_WEAK_PASSWORD_IS_WORD,
    TEST_WEAK_PASSWORD_LENGTH,
    TEST_WEAK_PASSWORD_QUALITY,
    TEST_WEAK_PASSWORD_SEQUENCES_NUMBER,
    TEST_YANDEX_GID_COOKIE,
    TEST_YANDEXUID_COOKIE,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.counters import registration_karma
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker.phones import build_phone_secured
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.login.login import masked_login
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from werkzeug.datastructures import Headers


TEST_OLD_SESSIONID = '0:old-session'
TEST_OLD_SSL_SESSIONID = '0:old-sslsession'

eq_ = iterdiff(eq_)


def build_headers(cookie=''):
    return mock_headers(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=cookie,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'changed_password'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'changed_password'},
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    PASSPORT_SUBDOMAIN='passport-test',
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:changed_password': 5,
            'push:changed_password': 5,
        },
    )
)
class CompletePDDTestCaseBase(
    EmailTestMixin,
    AccountModificationNotifyTestMixin,
    BaseBundleTestViews,
    ProfileTestMixin,
):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.default_url = '/2/bundle/auth/password/complete_pdd/?consumer=dev'
        headers = mock_headers(
            host=TEST_HOST, user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT, cookie=TEST_USER_COOKIES, accept_language=TEST_ACCEPT_LANGUAGE,
        )
        self.headers = Headers(headers.items())
        self.expected_session_value = PDD_SESSION_VALUE

        self.setup_track()
        self.setup_statbox_templates()

        self.userinfo = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            subscribed_to=[100],
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.blackbox_response = blackbox_userinfo_response(**self.userinfo)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.blackbox_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): False,
                    base64.b64encode(TEST_WEAK_PASSWORD_HASH): False,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)
        self.build_cookie_lah = mock.Mock(return_value=EXPECTED_LAH_COOKIE)

        self.patches = [
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self.build_cookie_lah,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        for patch in self.patches:
            patch.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_OK)

        self.expected_accounts = [
            {
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_PDD_LOGIN,
            },
        ]
        self.expected_session_value = '2:session'
        self.uid = TEST_PDD_UID
        self.setup_profile_patches()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.teardown_profile_patches()
        self.env.stop()
        for patch in self.patches:
            patch.stop()
        del self.env
        del self.track_manager
        del self.patches
        del self.build_cookies_yx
        del self.build_cookie_l
        del self.build_cookie_lah

    def initial_track_data(self):
        return dict(
            is_complete_pdd_with_password=True,
            is_password_passed=True,
            is_complete_pdd=False,
            is_strong_password_policy_required=False,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            password_hash=TEST_WEAK_PASSWORD_HASH,
            uid=TEST_PDD_UID,
            login=TEST_LOGIN,
            country='ru',
            language='ru',
            domain=TEST_DOMAIN,
            human_readable_login='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            machine_readable_login='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            emails='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            have_password=True,
            is_captcha_required=True,
            is_captcha_checked=True,
            is_captcha_recognized=True,
            auth_method='password',
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ] * 2,
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'] * 2)

    def setup_track(self, track_data=None):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        track_data = track_data or self.initial_track_data()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for field_name, value in track_data.items():
                setattr(track, field_name, value)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'local_cookie_set',
            _inherit_from='cookie_set',
            captcha_passed='1',
            ip_country='ru',
            ip=TEST_IP,
            uid=str(TEST_PDD_UID),
            input_login=TEST_LOGIN,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            person_country='ru',
        )
        self.env.statbox.bind_entry(
            'captcha_failed',
            mode='any_auth',
            action='captcha_failed',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
        )
        self.env.statbox.bind_entry(
            '_base_password_validation_error',
            action='password_validation_error',
            is_additional_word=tskv_bool(False),
            additional_subwords_number='0',
            weak='1',
        )
        self.env.statbox.bind_entry(
            'strong_password_validation_error',
            _inherit_from='_base_password_validation_error',
            password_quality=str(TEST_NOT_STRONG_PASSWORD_QUALITY),
            length=str(TEST_NOT_STRONG_PASSWORD_LENGTH),
            classes_number=str(TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_WORD),
            policy='strong',
        )
        self.env.statbox.bind_entry(
            'weak_password_validation_error',
            _inherit_from='_base_password_validation_error',
            password_quality=str(TEST_WEAK_PASSWORD_QUALITY),
            length=str(TEST_WEAK_PASSWORD_LENGTH),
            classes_number=str(TEST_WEAK_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_WEAK_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_WEAK_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_WEAK_PASSWORD_IS_WORD),
            policy='basic',
        )

    def create_frodo_params(self, **kwargs):
        params = {
            'uid': str(TEST_PDD_UID),
            'login': TEST_PDD_LOGIN,
            'from': '',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': '80',
            'hintqid': '',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'v2_yandex_gid': TEST_YANDEX_GID_COOKIE,
            'fuid': TEST_FUID01_COOKIE,
            'useragent': TEST_USER_AGENT,
            'host': TEST_HOST,
            'ip_from': TEST_IP,
            'v2_ip': TEST_IP,
            'xcountry': 'tr',
            'iname': 'firstname',
            'fname': 'lastname',
            'valkey': '0000000000',
            'lang': 'tr',
            'action': 'complete_pdd',
            'v2_track_created': TimeNow(),
            'v2_old_password_quality': '10',
            'v2_account_country': 'tr',
            'v2_account_language': 'tr',
            'v2_account_timezone': 'Europe/Paris',
            'v2_accept_language': 'ru',
            'v2_account_karma': '',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '1',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '1',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_cookie_my_block_count': '1',
            'v2_cookie_my_language': 'tt',
            'v2_cookie_l_login': TEST_LOGIN,
            'v2_cookie_l_uid': str(TEST_UID),
            'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
        }
        params.update(kwargs)
        return EmptyFrodoParams(**params)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'display_language': 'ru',
            # Пароль
            'password': TEST_PASSWORD,
            # Персональная информация
            'firstname': 'firstname',
            'lastname': 'lastname',
            'gender': 'f',
            'birthday': '1950-01-30',
            'timezone': 'Europe/Paris',
            'country': 'tr',
            'language': 'tr',
            # КО/КВ
            'question': 'question',
            'answer': 'answer',
            'eula_accepted': '1',
        }
        if exclude:
            for key in exclude:
                if key in base_params:
                    del base_params[key]
        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=headers,
        )

    def expected_cookies(self, with_lah=True):
        result = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
            'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/' % TEST_PDD_LOGIN,
        ]
        if with_lah:
            result.append(EXPECTED_LAH_COOKIE)
        return result

    def check_response_ok(self, response, accounts=None, with_lah=True):
        expected_response = {
            'cookies': self.expected_cookies(with_lah=with_lah),
            'default_uid': TEST_PDD_UID,
            'account': {
                'uid': int(TEST_PDD_UID),
                'login': TEST_PDD_LOGIN,
                'domain': {
                    'punycode': TEST_DOMAIN,
                    'unicode': TEST_DOMAIN,
                },
                'display_login': TEST_PDD_LOGIN,
            },
            'accounts': accounts or self.expected_accounts,
        }
        self.assert_ok_response(response, ignore_order_for=['cookies'], **expected_response)

    def check_track_poststate(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.have_password, True)
        eq_(track.session, self.expected_session_value)

    def check_db(self, check_password=True, strong_password=False, with_optional_params=True,
                 clear_creating_required=True, clear_changing_required=True, is_workspace_user=False):
        uid = TEST_PDD_UID
        timenow = TimeNow()

        if not is_workspace_user:
            self.env.db.check('attributes', 'person.firstname', 'firstname', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.lastname', 'lastname', uid=uid, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'karma.value', uid=uid, db='passportdbshard2')

        if with_optional_params and not is_workspace_user:
            self.env.db.check('attributes', 'person.country', 'tr', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.language', 'tr', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.gender', 'f', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.birthday', '1950-01-30', uid=uid, db='passportdbshard2')
        elif with_optional_params and is_workspace_user:
            self.env.db.check('attributes', 'person.country', 'tr', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.language', 'tr', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=uid, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'person.country', uid=uid, db='passportdbshard2')
            self.env.db.check_missing('attributes', 'person.language', uid=uid, db='passportdbshard2')
            self.env.db.check_missing('attributes', 'person.timezone', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.gender', 'm', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'person.birthday', '1963-05-15', uid=uid, db='passportdbshard2')

        if not is_workspace_user:
            self.env.db.check('attributes', 'hint.answer.encrypted', 'answer', uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'hint.question.serialized', '99:question', uid=uid, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=uid, db='passportdbshard2')
            self.env.db.check_missing('attributes', 'hint.question.serialized', uid=uid, db='passportdbshard2')

        self.env.db.check('attributes', 'account.is_pdd_agreement_accepted', '1', uid=uid, db='passportdbshard2')

        if check_password:

            self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'password.update_datetime', timenow, uid=uid, db='passportdbshard2')
            self.env.db.check('attributes', 'password.quality', '3:80', uid=uid, db='passportdbshard2')
            self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=uid, db='passportdbshard2')

            if strong_password:
                self.env.db.check('password_history', 'ts', DatetimeNow(), uid=uid, db='passportdbshard2')
                self.env.db.check('password_history', 'encrypted_password', TEST_WEAK_PASSWORD_HASH, uid=uid, db='passportdbshard2')

        if clear_creating_required:
            self.env.db.check_missing('attributes', 'password.is_creating_required', uid=uid, db='passportdbshard2')

        if clear_changing_required:
            self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=uid, db='passportdbshard2')

    def check_history_db(self, check_password=True, subscriptions=None, clear_is_changing_required=False, exclude=None):
        expected_values = {
            'action': 'complete_pdd',
            'consumer': 'dev',
            'info.firstname': 'firstname',
            'info.lastname': 'lastname',
            'info.sex': '2',
            'info.birthday': '1950-01-30',
            'info.tz': 'Europe/Paris',
            'info.country': 'tr',
            'info.lang': 'tr',
            'info.hinta': 'answer',
            'info.hintq': '99:question',
            'sid.add': '102' if not subscriptions else ','.join([str(sid) for sid in subscriptions]),
            'user_agent': TEST_USER_AGENT,
            'sid.rm': '100|%s' % TEST_PDD_LOGIN,
        }
        if exclude:
            for name in exclude:
                expected_values.pop(name)
        if check_password:
            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_PDD_UID, db='passportdbshard2')
            if self.is_password_hash_from_blackbox:
                eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
            else:
                eq_(len(eav_pass_hash), 36)
                ok_(eav_pass_hash.startswith('1:'))
            expected_values.update({
                'info.glogout': TimeNow(),
                'info.password': eav_pass_hash,
                'info.password_quality': '80',
                'info.password_update_time': TimeNow(),
            })

        if clear_is_changing_required:
            expected_values.update({
                'sid.login_rule': '8|1',
            })

        self.assert_events_are_logged(self.env.handle_mock, expected_values)

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_query_equals(self.create_frodo_params(**kwargs))

    def assert_sessionid_called(self):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[3][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'method': 'sessionid',
                'multisession': 'yes',
                'sessionid': TEST_OLD_SESSIONID,
            },
        )

    def assert_editsession_called(self):
        editsession_request = self.env.blackbox.get_requests_by_method('editsession')[0]
        editsession_request.assert_query_equals(
            {
                'uid': str(self.uid),
                'format': 'json',
                'sessionid': TEST_OLD_SESSIONID,
                'sslsessionid': TEST_OLD_SSL_SESSIONID,
                'host': 'passport-test.yandex.ru',
                'userip': TEST_IP,
                'method': 'editsession',
                'op': 'add',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'new_default': str(self.uid),
                'keyspace': 'yandex.ru',
                'lang': '1',
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_createsession_called(self):
        createsession_request = self.env.blackbox.get_requests_by_method('createsession')[0]
        createsession_request.assert_query_equals(
            {
                'uid': str(self.uid),
                'format': 'json',
                'userip': TEST_IP,
                'method': 'createsession',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'keyspace': 'yandex.ru',
                'is_lite': '0',
                'lang': '1',
                'ver': '3',
                'ttl': '5',
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_IP),
        ]

    def assert_auth_and_event_log_ok(self, expected_auth_log_records,
                                     check_password=True, additional_entries=None, subscriptions=None):
        expected_values = {
            'action': 'complete_pdd',
            'consumer': 'dev',
            'info.firstname': 'firstname',
            'info.lastname': 'lastname',
            'info.sex': '2',
            'info.birthday': '1950-01-30',
            'info.tz': 'Europe/Paris',
            'info.country': 'tr',
            'info.lang': 'tr',
            'info.hinta': 'answer',
            'info.hintq': '99:question',
            'sid.add': '102' if not subscriptions else ','.join([str(sid) for sid in subscriptions]),
            'user_agent': TEST_USER_AGENT,
            'sid.rm': '100|%s' % TEST_PDD_LOGIN,
        }
        if check_password:
            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_PDD_UID, db='passportdbshard2')
            expected_values.update({
                'info.glogout': TimeNow(),
                'info.password': eav_pass_hash,
                'info.password_quality': '80',
                'info.password_update_time': TimeNow(),
            })
        if additional_entries:
            expected_values.update(additional_entries)
        self.assert_events_are_logged(self.env.handle_mock, expected_values)
        # Остальные записи об апдейте сессий для каждого валидного пользователя в куке
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_auth_log_records,
        )

    def assert_statbox_ok(self, session_method, uids_count='1', **kwargs):
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry(
                'local_cookie_set',
                session_method=session_method,
                uids_count=uids_count,
                track_id=self.track_id,
                **kwargs
            ),
            entry_index=-2,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestAuthCompletePDD(CompletePDDTestCaseBase,
                          make_clean_web_test_mixin('test_ok', ['firstname', 'lastname'], statbox_action=None),
                          ):
    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        resp = self.make_request(
            self.query_params(
                **{field: u'Заходи дорогой, гостем будешь диваны.рф'}
            ),
            self.headers,
        )
        self.assert_error_response(resp, ['{}.invalid'.format(field)])

    def test_ok(self):
        """
        Простой сценарий - пришли без готовой сессии
        """
        self.env.db.serialize(self.blackbox_response)
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db()
        self.check_history_db()
        eq_(self.env.auth_handle_mock.call_count, 1)

        createsession_request = self.env.blackbox.get_requests_by_method('createsession')[0]
        createsession_request.assert_query_contains({'is_lite': '0'})
        self.check_frodo_call()
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)

    def test_send_push_when_password_changed(self):
        self.env.db.serialize(self.blackbox_response)
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        resp = self.make_request(
            self.query_params(
                country='ru',
                language='ru',
            ),
            self.headers,
        )

        self.check_response_ok(resp)
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='changed_password',
            uid=TEST_PDD_UID,
            title='Пароль в аккаунте {} успешно изменён'.format(TEST_PDD_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    @freezegun.freeze_time()
    def test_send_mail_when_password_changed(self):
        email = self.create_validated_external_email(TEST_LOGIN, 'gmail.com')
        self.userinfo.update(emails=[email])
        self.blackbox_response = blackbox_userinfo_response(**self.userinfo)
        self.env.blackbox.set_blackbox_response_value('userinfo', self.blackbox_response)
        self.env.db.serialize(self.blackbox_response)

        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        resp = self.make_request(
            self.query_params(
                country='ru',
                language='ru',
            ),
            self.headers,
        )

        self.check_response_ok(resp)

        self.assert_emails_sent([
            self.create_account_modification_mail(
                'changed_password',
                email['address'],
                dict(login=masked_login(self.userinfo['login'])),
            ),
        ])

    def test_ok_clear_password_options_without_password(self):
        self.blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            subscribed_to=[100],
            dbfields={
                'subscription.suid.8': '1',
                'subscription.login_rule.8': '5',
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            emails=[],
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.blackbox_response,
        )
        self.env.db.serialize(self.blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = True

        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(check_password=False)
        self.check_history_db(check_password=False, clear_is_changing_required=True)
        eq_(self.env.auth_handle_mock.call_count, 1)

        url = self.env.blackbox._mock.request.call_args_list[2][0][1]
        check_url_contains_params(url, {'is_lite': '0', 'method': 'createsession'})
        self.check_frodo_call(
            v2_password_quality=u'',
            passwdex=u'0.0.0.0.0.0.0.0',
            v2_old_password_quality=u'',
            passwd=u'0.0.0.0.0.0.0.0',
        )
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)

    def test_ok_with_env_profile_modification(self):
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            headers=build_headers(),
        )

        self.check_response_ok(resp)
        profile = self.make_user_profile(dict(TEST_RAW_ENV_FOR_PROFILE, yandexuid=None))
        self.assert_profile_written_to_auth_challenge_log(uid=TEST_PDD_UID, profile=profile)

    def test_ok_subscribe_user(self):
        self.env.db.serialize(self.blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.service = 'lenta'
        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db()

        self.env.db.check('attributes', 'subscription.23', '1', uid=TEST_PDD_UID, db='passportdbshard2')

        self.check_history_db(subscriptions=[102, 23])
        self.check_frodo_call(**{'from': 'lenta'})

    def test_ok_password_not_required(self):
        self.env.db.serialize(self.blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = True
            track.have_password = True

        resp = self.make_request(
            self.query_params(exclude=['password']),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(check_password=False)
        self.check_history_db(check_password=False)
        self.check_frodo_call(
            v2_password_quality=u'',
            passwdex=u'0.0.0.0.0.0.0.0',
            v2_old_password_quality=u'',
            passwd=u'0.0.0.0.0.0.0.0',
        )

    def test_phone_logged(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            subscribed_to=[100],
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            **deep_merge(
                dict(attributes={
                    'password.encrypted': TEST_WEAK_PASSWORD_HASH,
                }),
                build_phone_secured(
                    1,
                    TEST_PHONE_NUMBER.e164,
                )
            )
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(self.query_params(), self.headers)

        self.check_response_ok(resp)
        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(
                TEST_PDD_UID,
                TEST_PHONE_NUMBER.e164,
                TEST_YANDEXUID_COOKIE,
            ),
        ])

    def test_ok_with_strong_password(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            subscribed_to=[100, 67],
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(strong_password=True)
        self.check_history_db()
        self.check_frodo_call()

    def test_ok_with_question_id(self):
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(exclude=['question'], question_id=1),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()

        # В новой схеме данные хранятся в utf-8, при выборке, FakeDB будет возвращать byte-string
        answer = u'1:Девичья фамилия матери'.encode('utf-8')
        self.env.db.check('attributes', 'hint.question.serialized', answer, uid=TEST_PDD_UID, db='passportdbshard2')

        self.check_frodo_call()

    def test_short_session(self):
        self.env.db.serialize(self.blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp, with_lah=False)
        self.check_track_poststate()
        self.check_db()
        self.check_history_db()
        self.check_frodo_call()

    def test_frodo_report_spam(self):
        self.env.db.serialize(self.blackbox_response)

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_SPAM_PDD_USER)
        self.env.frodo.set_response_value(u'confirm', u'')

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()

        self.env.db.check('attributes', 'karma.value', '85', uid=TEST_PDD_UID, db='passportdbshard2')

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params())

    def test_frodo_bad_user(self):
        self.env.db.serialize(self.blackbox_response)
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_BAD_PDD_USER)
        self.env.frodo.set_response_value(u'confirm', u'')

        resp = self.make_request(self.query_params(), self.headers)
        self.check_response_ok(resp)
        self.check_track_poststate()

        self.env.db.check('attributes', 'karma.value', '100', uid=TEST_PDD_UID, db='passportdbshard2')

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(self.create_frodo_params())
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

    def test_ok_without_optional_params(self):
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(exclude=['gender', 'birthday', 'country', 'timezone', 'language']),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_frodo_call(
            xcountry='ru',
            # Fallback наших саджестеров - 'ru'
            v2_account_country='ru',
            v2_account_language='ru',
            v2_account_timezone='Europe/Moscow',
            lang='ru',
        )
        self.check_db(with_optional_params=False)

    def test_ok_with_empty_headers(self):
        resp = self.make_request(
            self.query_params(),
            mock_headers(
                host=TEST_HOST,
                user_ip=TEST_IP,
                user_agent='',
                cookie='',
                referer='',
            ),
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_frodo_call(
            useragent='',
            v2_accept_language='',
            valkey='0000000100',
            fuid='',
            yandexuid='',
            v2_yandex_gid='',
            v2_has_cookie_my='0',
            v2_has_cookie_l='0',
            v2_cookie_my_block_count='',
            v2_cookie_my_language='',
            v2_cookie_l_uid='',
            v2_cookie_l_login='',
            v2_cookie_l_timestamp='',
        )

    def test_complete__wrong_host__error(self):
        resp = self.make_request(
            self.query_params(),
            mock_headers(
                host='google.com',
                user_ip=TEST_IP,
                user_agent='',
                cookie='',
            ),
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['host.invalid'],
            },
        )

    def test_blackbox_userinfo_no_uid_error(self):
        """ЧЯ вернул пустой ответ по методу userinfo - ошибка обрабатывается"""
        userinfo_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['account.not_found'],
            },
        )

    def test_blackbox_user_is_disabled_error(self):
        """Пользователь с этим uid "выкл" (disabled) - ошибка обрабатывается"""
        blackbox_response = blackbox_userinfo_response(enabled=False)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['account.disabled'],
            },
        )

    def test_blackbox_user_is_disabled_on_deletion_error(self):
        """
        Пользователь с этим uid "заблокирован при удалении" (disabled),
        т.к. подписан на блокирующий SID.
        """
        blackbox_response = blackbox_userinfo_response(
            enabled=False,
            attributes={
                'account.is_disabled': ACCOUNT_DISABLED_ON_DELETION,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['account.disabled_on_deletion'],
            },
        )

    def test_blackbox_domain_is_disabled_error(self):
        """Домен пользователя "выкл" (disabled) - ошибка обрабатывается"""
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            domain_enabled=False,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['account.disabled'],
            },
        )

    def test_pdd_cannot_have_password(self):
        """ПДД пользователь, для которого не предусмотрено заведение пароля"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = True
            track.have_password = False
        resp = self.make_request(
            self.query_params(exclude=['password']),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(json.loads(resp.data), {'status': 'error', 'errors': ['account.without_password']})

    def test_track_invalid_state(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = False
            track.have_password = False
        resp = self.make_request(
            self.query_params(exclude=['password']),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(json.loads(resp.data), {'status': 'error', 'errors': ['track.invalid_state']})

    def test_not_pdd(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 1
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            login=TEST_LOGIN,
            subscribed_to=[100],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request(
            self.query_params(exclude=['password']),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(json.loads(resp.data), {'status': 'error', 'errors': ['action.not_required']})

    def test_error_authorization_already_passed(self):
        """В треке указано, что авторизация уже пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.auth_passed'])

        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_eula_not_accepted(self):
        resp = self.make_request(
            self.query_params(eula_accepted=0),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['eula_accepted.not_accepted']},
        )

    def test_no_control_question_args(self):
        resp = self.make_request(
            self.query_params(exclude=['question']),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['question.empty']},
        )

    def test_too_many_control_question_args(self):
        resp = self.make_request(
            self.query_params(question_id=1),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['question.inconsistent']},
        )

    def test_password_equals_previous(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.password_hash = TEST_PASSWORD_HASH
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): True,
                },
            ),
        )

        resp = self.make_request(
            self.query_params(uid=TEST_PDD_UID),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.equals_previous']},
        )

    def test_strong_password_found_in_history(self):
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.found_in_history']},
        )

    def test_strong_password_short(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        resp = self.make_request(
            self.query_params(password='aa11bb22'),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.short']},
        )

    def test_password_short(self):
        resp = self.make_request(
            self.query_params(password='123'),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.short']},
        )

    def test_password_long(self):
        resp = self.make_request(
            self.query_params(password='a' * 256),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.long']},
        )

    def test_password_invalid(self):
        resp = self.make_request(
            self.query_params(password='№' * 10),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.prohibitedsymbols']},
        )

    def test_password_like_login(self):
        resp = self.make_request(
            self.query_params(
                password='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            ),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.likelogin']},
        )

    def test_account_global_logout_after_track_created_error(self):
        """
        Хотим закомплитить пользователя, но аккаунт был глобально разлогинен
        уже после того, как завели трек для комплита.
        """
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            domain=TEST_DOMAIN,
            subscribed_to=[100],
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={
                'account.global_logout_datetime': str(int(time.time()) + 1),
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES),
        )
        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['account.global_logout'],
            },
        )

    def test_password_like_yandex_login_ok(self):
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(
                password='%s@yandex.ru' % TEST_LOGIN,
            ),
            self.headers,
        )
        self.check_response_ok(resp)

    def test_password_too_weak(self):
        # Пароль с качеством 0
        resp = self.make_request(
            self.query_params(password=TEST_WEAK_PASSWORD),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.weak']},
        )

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('weak_password_validation_error'),
            ],
        )

    def test_strong_password_too_weak(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True

        # Пароль с качеством 50
        resp = self.make_request(
            self.query_params(password=TEST_NOT_STRONG_PASSWORD),
            self.headers,
        )

        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        eq_(
            json.loads(resp.data),
            {'status': 'error', 'errors': ['password.weak']},
        )

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('strong_password_validation_error'),
            ],
        )

    def test_with_cookies__overflow_error(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                time=TEST_COOKIE_TIMESTAMP,
                ip=TEST_IP,
                age='123',
                allow_more_users=False,
            ),
        )
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='Session_id=%s;sessionid2=%s;%s' % (
                    TEST_OLD_SESSIONID,
                    TEST_OLD_SSL_SESSIONID,
                    TEST_USER_COOKIES,
                ),
            ),
        )
        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        actual_response = json.loads(resp.data)
        eq_(
            actual_response,
            {
                'status': 'error',
                'errors': [u'sessionid.overflow'],
            },
        )

    def test_ok_without_cookie(self):
        """
        Дорегистрируем ПДД пользователя с паролем вообще без сессионной куки.
        Вызов должен проходить так же как для моноавторизации.
        """
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES),
        )
        self.check_response_ok(
            resp,
            accounts=[{
                'uid': self.uid,
                'login': TEST_PDD_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_PDD_LOGIN,
            }],
        )
        self.check_track_poststate()
        self.check_db()
        self.assert_createsession_called()

        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_ok(session_method='create')
        self.check_frodo_call()

    def test_after_oauth__ok(self):
        """Дорегистрация после авторизации по oauth-токену проходит с выписыванием защищенной куки"""
        self.env.db.serialize(self.blackbox_response)
        track_data = self.initial_track_data()
        track_data.update(is_oauth_pdd_authorization=True)
        self.setup_track(track_data=track_data)

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )

        self.check_response_ok(
            resp,
            accounts=[{
                'uid': self.uid,
                'login': TEST_PDD_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_PDD_LOGIN,
            }],
        )
        self.check_track_poststate()
        self.check_db()
        self.assert_createsession_called()

        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_ok(session_method='create')
        self.check_frodo_call()

    def test_ok_with_invalid_cookie(self):
        """
        Дорегистрируем пользователя с паролем и невалидной полностью кукой.
        Вызов должен проходить так же как для моноавторизации.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            build_headers(cookie='Session_id=%s;%s' % (TEST_OLD_SESSIONID, TEST_USER_COOKIES)),
        )
        self.check_response_ok(
            resp,
            accounts=[{
                'uid': self.uid,
                'login': TEST_PDD_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_PDD_LOGIN,
            }],
        )
        self.check_track_poststate()
        self.check_db()

        self.assert_sessionid_called()
        self.assert_createsession_called()

        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_ok(session_method='create')
        self.check_frodo_call()

    def test_ok_with_wrong_sessguard(self):
        """
        Поведение с неверным sessguard аналогично поведению с невалидной кукой
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )
        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            build_headers(cookie='Session_id=%s;%s' % (TEST_OLD_SESSIONID, TEST_USER_COOKIES)),
        )
        self.check_response_ok(
            resp,
            accounts=[{
                'uid': self.uid,
                'login': TEST_PDD_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_PDD_LOGIN,
            }],
        )
        self.check_track_poststate()
        self.check_db()

        self.assert_sessionid_called()
        self.assert_createsession_called()

        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_ok(session_method='create')
        self.check_frodo_call()

    def test_ok_with_cookie_with_other_account(self):
        """
        Дорегистрируем ПДД пользователя с паролем и мультикукой.
        Проверим что записали в auth логи и статбокс все верно.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                time=TEST_COOKIE_TIMESTAMP,
                ip=TEST_IP,
                age='123',
                ttl=5,
            ),
        )

        self.env.db.serialize(self.blackbox_response)

        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='Session_id=%s;sessionid2=%s;%s' % (
                    TEST_OLD_SESSIONID,
                    TEST_OLD_SSL_SESSIONID,
                    TEST_USER_COOKIES,
                ),
            ),
        )

        self.check_response_ok(
            resp,
            accounts=[
                {
                    'uid': 1234,
                    'login': 'other_login',
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': 'other_login',
                },
                {
                    'uid': self.uid,
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
        )

        self.assert_sessionid_called()
        self.assert_editsession_called()

        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', '1234'),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
        )
        self.assert_statbox_ok(
            session_method='edit',
            uids_count='2',
            old_session_uids='1234',
        )
        self.check_frodo_call(
            v2_session_age='123',
            v2_session_ip=TEST_IP,
            v2_session_create_timestamp=str(TEST_COOKIE_TIMESTAMP),
        )

    def test_ok_password_not_required_with_other_account(self):
        """
        Дорегистрируем ПДД пользователя без пароля и мультикукой.
        Проверим что записали в auth логи и статбокс все верно.
        """
        self.env.db.serialize(self.blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                ttl=5,
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = True
            track.have_password = True

        resp = self.make_request(
            self.query_params(),
            build_headers(
                cookie='Session_id=%s;sessionid2=%s;%s' % (
                    TEST_OLD_SESSIONID,
                    TEST_OLD_SSL_SESSIONID,
                    TEST_USER_COOKIES,
                ),
            ),
        )
        self.check_response_ok(
            resp,
            accounts=[
                {
                    'uid': 1234,
                    'login': 'other_login',
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': 'other_login',
                },
                {
                    'uid': self.uid,
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
        )
        self.check_track_poststate()
        self.check_db(check_password=False)
        self.check_history_db(check_password=False)
        self.assert_auth_and_event_log_ok(
            [
                self.build_auth_log_entry('ses_update', '1234'),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
            check_password=False,
        )
        self.assert_statbox_ok(
            session_method='edit',
            uids_count='2',
            old_session_uids='1234',
        )

    def test_captcha_required_error(self):
        """
        Пришли с неразгаданной капчей - показываем ошибку.
        """
        self.env.db.serialize(self.blackbox_response)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        resp = self.make_request(self.query_params(), self.headers)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['captcha.required'],
            },
        )
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry('captcha_failed'),
            entry_index=-1,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestAuthCompleteWorkspacePDD(CompletePDDTestCaseBase):
    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'display_language': 'ru',
            'password': TEST_PASSWORD,
            # Персональная информация
            'birthday': '1950-01-30',  # не должно записаться
            'timezone': 'Europe/Paris',
            'country': 'tr',
            'language': 'ru',
            'eula_accepted': '1',
        }
        if exclude:
            for key in exclude:
                if key in base_params:
                    del base_params[key]
        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        """
        Дорегистрация WS-пользователя без смены пароля
        """
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            attributes={
                'account.have_organization_name': '1',
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            language='tr',
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd_with_password = False
            track.is_complete_pdd = True
            track.have_password = True

        resp = self.make_request(
            self.query_params(exclude=['password']),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(check_password=False, is_workspace_user=True)
        self.check_history_db(
            check_password=False,
            exclude=[
                'info.birthday',
                'info.firstname',
                'info.lastname',
                'info.hintq',
                'info.hinta',
                'info.sex',
                'info.lang',
                'sid.rm',
            ],
        )
        eq_(self.env.auth_handle_mock.call_count, 1)

        url = self.env.blackbox._mock.request.call_args_list[-1][0][1]
        check_url_contains_params(url, {'is_lite': '0', 'method': 'createsession'})
        self.check_frodo_call(
            v2_password_quality=u'',
            passwdex=u'0.0.0.0.0.0.0.0',
            v2_old_password_quality=u'',
            passwd=u'0.0.0.0.0.0.0.0',
            fname='',
            iname='',
        )
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)

    def test_ok_with_password_creating_required(self):
        """
        Дорегистрация WS-пользователя с требованием создать пароль
        """
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            subscribed_to=[100],
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            attributes={
                'account.have_organization_name': '1',
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            language='tr',
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(is_workspace_user=True)
        self.check_history_db(
            exclude=[
                'info.birthday',
                'info.firstname',
                'info.lastname',
                'info.hintq',
                'info.hinta',
                'info.sex',
                'info.lang',
            ],
        )
        eq_(self.env.auth_handle_mock.call_count, 1)

        createsession_request = self.env.blackbox.get_requests_by_method('createsession')[0]
        createsession_request.assert_query_contains({'is_lite': '0'})
        self.check_frodo_call(fname='', iname='')
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)

    def test_ok_with_password_changing_required(self):
        """
        Дорегистрация WS-пользователя с требованием сменить пароль
        """
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            dbfields={
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            attributes={
                'account.have_organization_name': '1',
                'password.forced_changing_reason': '1',
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            language='tr',
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(
            self.query_params(),
            self.headers,
        )
        self.check_response_ok(resp)
        self.check_track_poststate()
        self.check_db(is_workspace_user=True)
        self.check_history_db(
            clear_is_changing_required=True,
            exclude=[
                'info.birthday',
                'info.firstname',
                'info.lastname',
                'info.hintq',
                'info.hinta',
                'info.sex',
                'info.lang',
                'sid.rm',
            ],
        )
        eq_(self.env.auth_handle_mock.call_count, 1)

        createsession_request = self.env.blackbox.get_requests_by_method('createsession')[0]
        createsession_request.assert_query_contains({'is_lite': '0'})
        self.check_frodo_call(fname='', iname='')
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAuthCompletePDDNoBlackboxHash(TestAuthCompletePDD):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAuthCompleteWorkspacePDDNoBlackboxHash(TestAuthCompleteWorkspacePDD):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
